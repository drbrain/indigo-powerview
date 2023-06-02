#!/usr/bin/env python
# coding: utf-8
import logging

from powerview2 import PowerView
from powerview3 import PowerViewGen3
import requests
try:
    import indigo
except ImportError:
    pass


class Plugin(indigo.PluginBase):

    # Shade Type lookup table. Indexed by 'capabilities' property.
    SHADE_TYPE = [
        "Bottom Up",
        "Bottom Up w/ 90° Tilt",
        "Bottom Up w/ 180° Tilt",
        "Vertical (Traversing)",
        "Vertical (Traversing) w/ 180° Tilt",
        "Tilt Only 180°",
        "Top Down",
        "Top-Down/Bottom-Up",
        "Duolite",
        "Duolite with 90° Tilt",
        "Duolite with 180° Tilt"
    ]

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.DEBUG_SERVER_IP = "10.10.28.191"  # IP address of the Mac running PyCharm
        # indigo.DEBUG_SERVER_IP = "localhost"  # IP address of the Mac running PyCharm
        super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.pluginPrefs = pluginPrefs

        # import pydevd_pycharm
        # pydevd_pycharm.settrace('localhost', port=5678)

        self.debugSetting = pluginPrefs.get('debugPref', '')
        self.logger = logging.getLogger('Plugin')
        if isinstance(self.debugSetting, str):
            self.logger.setLevel = self.debugSetting

        self.devices = {}
        self.powerview = None

    #########################################
    #  Devices
    #########################################
    def createShade(self, hubHostname, shadeId, hubId):
        address = '%s:%s' % (hubHostname, shadeId)

        if self.findShade(address):
            self.logger.info('Shade %s already exists' % address)
            return

        folderId = 0
        if hubId:
            hub = indigo.devices[hubId]
            folderId = hub.folderId

        self.logger.info('Creating shade %s' % address)
        shade_data = self.findShadeOnHub(hubHostname, shadeId)

        new_shade = self.create_shade_device(address, shade_data, folderId)
        if new_shade:
            new_shade.replaceOnServer()
            self.updateShadeLater(new_shade)
            return True

        return False

    #########################################
    #  Actions
    #########################################
    def activateScene(self, action):
        hub = indigo.devices[action.deviceId]
        sceneId = action.props['sceneId']

        self.logger.info('activate scene %s on hub %s' % (sceneId, hub.name))
        self.getPV(hub.address).activateScene(hub.address, sceneId)
        self.updateShadeLater(hub)

    def activateSceneCollection(self, action):
        hub = indigo.devices[action.deviceId]
        sceneCollectionId = action.props['sceneCollectionId']

        self.logger.info('activate scene collection %s on hub %s' % (sceneCollectionId, hub.name))
        self.getPV(hub.address).activateSceneCollection(hub.address, sceneCollectionId)
        self.updateShadeLater(hub)

    def calibrateShade(self, action):
        shade = indigo.devices[action.deviceId]
        hubHostname, shadeId = shade.address.split(':')

        self.logger.info('Calibrating shade %s (%s) (id:%s)' % (shade.name, shade.id, shadeId))
        self.getPV(hubHostname).calibrateShade(hubHostname, shadeId)

    def jogShade(self, action):
        shade = indigo.devices[action.deviceId]
        hubHostname, shadeId = shade.address.split(':')

        self.logger.info('Jogging shade %s (%s) (id:%s)' % (shade.name, shade.id, shadeId))
        self.getPV(hubHostname).jogShade(hubHostname, shadeId)
        self.updateShadeLater(shade)

    def stopShade(self, action):
        shade = indigo.devices[action.deviceId]
        hubHostname, shadeId = shade.address.split(':')
        self.logger.info('Stopping shade %s (%s) (id:%s)' % (shade.name, shade.id, shadeId))
        self.getPV(hubHostname).stopShade(hubHostname, shadeId)
        self.updateShadeLater(shade)

    def setShadePosition(self, action):
        shade = indigo.devices[action.deviceId]
        primary = action.props.get('primary', '0')
        secondary = action.props.get('secondary', '0')
        tilt = action.props.get('tilt', '0')
        velocity = action.props.get('velocity', '0')

        self.logger.info('Setting position of %s (%s) primary (bottom): %s, secondary (top): %s, tilt: %s, velocity: %s' %
                      (shade.name, action.deviceId, primary, secondary, tilt, velocity))

        hubHostname, shadeId = shade.address.split(':')

        if shade.states['generation'] == 2:
            top = int(float(secondary) / 100.0 * 65535.0)
            bottom = int(float(primary) / 100.0 * 65535.0)
            self.getPV(hubHostname).setShadePosition(hubHostname, shadeId, top, bottom)
        else:
            primary = float(primary) / 100.0
            secondary = float(secondary) / 100.0
            tilt = float(tilt) / 100.0
            velocity = float(velocity) / 100.0

            positions = {"primary": primary, "secondary": secondary, "tilt": tilt, "velocity": velocity}
            self.getPV(hubHostname).setShadePosition(hubHostname, shadeId, positions)

        self.updateShadeLater(shade)

    #########################################
    #  UI Support Routines
    #########################################
    def currentPosition(self, valuesDict, typeId, devId):
        """ Returns the current values of primary, secondary, tilt and velocity for
            existing shade devices. If the shade device is new, the devId will be
            zero, so the shade  address is unavailable.
        """
        #   typeId is the device type specified in the Devices.xml
        #   devId is the device ID - 0 if it's a new device

        if devId:
            shade = indigo.devices[devId]
            hubHostname, shadeId = shade.address.split(':')

            self.getPV(hubHostname).jogShade(hubHostname, shadeId)
            data = self.getPV(hubHostname).shade(hubHostname, shadeId)

            # Enable/disable entry fields so only those needed are enabled.
            capabilities = data.get('capabilities', -1)
            valuesDict['enablePri'] = (capabilities in [0, 1, 2, 3, 4, 6, 7, 8, 9, 10])  # Primary
            valuesDict['enableSec'] = (capabilities in [7, 8, 9, 10])  # Secondary
            if shade.states['generation'] == 2:  # Gen 2
                valuesDict['enableTlt'] = False  # Tilt
                valuesDict['enableVel'] = False

            pos = data.get('positions')
            if pos:
                valuesDict['primary'] = "{:.0f}".format(self.to_percent(pos['primary']))
                valuesDict['secondary'] = "{:.0f}".format(self.to_percent(pos['secondary']))
                valuesDict['tilt'] = "{:.0f}".format(self.to_percent(pos['tilt']))
                valuesDict['velocity'] = "{:.0f}".format(self.to_percent(pos['velocity']))
                valuesDict['enableTlt'] = (capabilities in [1, 2, 4, 5, 9, 10])  # Tilt

        return valuesDict

    def discoverShades(self, valuesDict, typeId, deviceId):
        address = valuesDict['address']

        self.logger.info('Discovering shades on %s' % address)
        shadeIds = self.getPV(address).shadeIds(address)
        device_count = 0

        for shadeId in shadeIds:
            if self.createShade(address, shadeId, deviceId):
                device_count = device_count + 1

        valuesDict['message'] = "Discovered {} Shade{}, and Created {} Device{}.".format(
                len(shadeIds), 's' if len(shadeIds) != 1 else '', device_count, 's' if device_count != 1 else '')

        return valuesDict

    def listHubs(self, filter="", valuesDict="", type="", targetId=0):
        hub_list = []
        my_devices = indigo.devices.iter('self.PowerViewHub')
        for device in my_devices:
            hub_list.append([device.id, device.name])

        hub_list = sorted(hub_list, key=lambda pair: pair[1])
        return hub_list

    def listScenes(self, filter="", valuesDict="", type="", targetId=0):
        hub = self.devices[targetId]

        scenes = self.getPV(hub.address).scenes(hub.address)
        scene_list = []

        for scene in scenes:
            scene_list.append([scene['id'], scene['name']])

        scene_list = sorted(scene_list, key=lambda pair: pair[1])
        return scene_list

    def listSceneCollections(self, filter="", valuesDict="", type="", targetId=0):
        hub = self.devices[targetId]

        data = self.getPV(hub.address).sceneCollections(hub.address)
        scene_list = []

        for sceneCollection in data:
            scene_list.append([sceneCollection['id'], sceneCollection['name']])

        scene_list = sorted(scene_list, key=lambda pair: pair[1])
        return scene_list

    def listShades(self, filter="", valuesDict=None, typeId="", targetId=0):
        """ Produces a list of all shades on all hubs that do NOT exist as devices."""
        shade_list = []
        my_devices = indigo.devices.iter('self.PowerViewHub')

        if my_devices:
            for hub in my_devices:
                shade_devices = indigo.devices.iter('self.PowerViewShade')
                shade_dev_addresses = []
                for dev in shade_devices:
                    shade_dev_addresses.append(dev.address)

                shade_ids = self.getPV(hub.address).shadeIds(hub.address)
                for shade_id in shade_ids:
                    address = '%s:%s' % (hub.address, shade_id)
                    if address not in shade_dev_addresses:

                        shade = self.getPV(hub.address).shade(hub.address, shade_id)
                        room_name = self.getPV(hub.address).room(hub.address, shade['roomId'])['name']
                        shade_name = shade['name']
                        shade_list.append([address, '%s - %s' % (room_name, shade_name)])

            shade_list = sorted(shade_list, key=lambda pair: pair[1])

        return shade_list

    #########################################
    #  Indigo Defined
    #########################################
    def deviceStartComm(self, device):
        if device.id not in self.devices:
            self.devices[device.id] = device
            self.update(device)

    def deviceStopComm(self, device):
        if device.id in self.devices:
            self.devices.pop(device.id)

    def getDeviceDisplayStateId(self, dev):
        """ Returns the property name to be shown in the State column, since the <UiDisplayStateId>
        tag seems to be ignored (and undocumented)."""
        if dev.deviceTypeId == 'PowerViewShade':
            return 'open'
        return None

    def runConcurrentThread(self):
        try:
            while True:
                for shade in indigo.devices.iter('self.PowerViewShade'):
                    props = shade.pluginProps
                    need_upd = props.get('need_update', 0)
                    if need_upd > 0:
                        # update device with new position
                        # self.updateShade(shade)
                        need_upd -= 1
                        # This props update will trigger call to deviceStartComm which will update the position
                        props.update({'need_update': need_upd})
                        shade.replacePluginPropsOnServer(props)

                self.sleep(15)

        except self.StopThread:
            pass

    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        valid = True
        errors_dict = indigo.Dict()
        if typeId == 'PowerViewShade':
            heading = valuesDict.get('heading', '0')
            heading = int(heading) if heading.isdigit() else -1
            if heading not in range(0, 361):
                errors_dict['heading'] = "Heading must be a compass reading from 0 to 360."
                valid = False

        if not valid:
            return valid, valuesDict, errors_dict

        if typeId == 'PowerViewShade':
            shade = indigo.devices[devId]
            props = shade.pluginProps
            props['stateField'] = valuesDict.get('stateField', '0')
            shade.replacePluginPropsOnServer(props)
        return valid, valuesDict

    def validateActionConfigUi(self, valuesDict, typeId, deviceId):
        valid = True
        errors_dict = indigo.Dict()
        
        if typeId == 'setShadePosition':
            for pos_name in ['primary', 'secondary', 'tilt', 'velocity']:
                pos_val = valuesDict.get(pos_name, '0')
                pos_val = int(pos_val) if pos_val.isdigit() else -1
                if pos_val not in range(0, 101):
                    errors_dict[pos_name] = "'{}' must be a percentage 0-100, where 0 is closed and 100 is fully open.".format(pos_name)
                    valid = False

        if not valid:
            return valid, valuesDict, errors_dict
        return valid, valuesDict

    #########################################
    #  Utilities
    #########################################
    def create_shade_device(self, address, data, folderId):
        name = data['name']
        new_shade = None

        try:
            new_shade = indigo.device.create(
                protocol=indigo.kProtocol.Plugin,
                address=address,
                deviceTypeId='PowerViewShade',
                name=name,
                description="Shade {} in {}".format(data['name'], data['room']),
                props={'stateField': 0},  # default to 0 for primary position as visible state
                folder=folderId
            )
        except Exception:
            self.logger.exception("Create failed for shade {} at address {}.".format(name, address))

        return new_shade

    def findShadeOnHub(self, hubHostname, shadeId, need_room=False):
        shade_data = self.getPV(hubHostname).shade(hubHostname, shadeId, room=need_room)
        shade_data['shadeType'] = self.SHADE_TYPE[shade_data['capabilities']]

        if 'positions' in shade_data:
            shadePositions = shade_data.pop('positions')
            shadePositions['open'] = ''
            shade_data.update(shadePositions)
        return shade_data

    def findShade(self, address):
        for device in indigo.devices.iter('self.PowerViewShade'):
            if device.address == address:
                return device

        return None

    def getPV(self, hub_address):
        """ Detects and returns the correct powerview class, based on how the gateway responds."""

        if self.powerview is None:
            home = requests.get("http://{}/home".format(hub_address))
            if home.status_code == requests.codes.ok:
                self.powerview = PowerViewGen3(self.logger)
            else:
                home = requests.get("http://{}/api/fwversion".format(hub_address))
                if home.status_code == requests.codes.ok:
                    self.powerview = PowerView()
                else:
                    raise KeyError("Invalid hub address ({})".format(hub_address))
        return self.powerview

    @staticmethod
    def to_percent(pos, divr=1.0):
        return float(pos) / divr * 100.0

    def update(self, device):
        if device.deviceTypeId == 'PowerViewShade':
            self.updateShade(device)

    def updateShade(self, shade):
        self.logger.info('Updating shade %s' % shade.address)

        if shade.address == '':
            return

        try:
            hubHostname, shadeId = shade.address.split(':')

            data = self.findShadeOnHub(hubHostname, shadeId)
            data.pop('name')  # don't overwrite local changes

            shade_states_details = super(Plugin, self).getDeviceStateList(shade)
            shade_states = []
            for shade_states_detail in shade_states_details:
                shade_states.append(shade_states_detail['Key'])

            # update the shade state for items in the device.
            # PV2 hubs have at least one additional data item
            # (signalStrength) not in the device definition
            shade.stateListOrDisplayStateIdChanged()  # Ensure any new states are added to this shade
            for key in data.keys():
                if key in shade_states:  # update if hub has state key from Devices.xml. This adds new states.
                    if key == 'open':
                        self.updateShadeOpenState(shade, data, key)
                    else:
                        shade.updateStateOnServer(key=key, value=data[key])
        except Exception as ex:
            self.logger.exception("Exception in updateShade.")
            raise ex

    def updateShadeLater(self, dev):
        """ Save an indicator in plugin properties for this shade to signal to do an update later, after it has moved. """
        if dev.deviceTypeId == 'PowerViewShade':
            props = dev.pluginProps
            props.update({'need_update': 4})
            dev.replacePluginPropsOnServer(props)

        elif dev.deviceTypeId == 'PowerViewHub':
            for shade in indigo.devices.iter('self.PowerViewShade'):
                if shade.address.startswith(dev.address):
                    props = shade.pluginProps
                    props.update({'need_update': 4})
                    shade.replacePluginPropsOnServer(props)

    def updateShadeOpenState(self, shade, data, key):
        stateField = shade.pluginProps.get('stateField', 0)

        if stateField == 0:  # 0 - Primary
            shade.updateStateOnServer(key=key, value="{:.0f}% Open".format(self.to_percent(data['primary'])), decimalPlaces=0)

        elif stateField == 1:  # 1 - Primary and Secondary
            shade.updateStateOnServer(key=key, value="{:.0f}% P, {:.0f}% S".format(self.to_percent(data['primary']),
                                                                                   self.to_percent(data['secondary'])), decimalPlaces=0)
        elif stateField == 2:  # 2 - Primary and Tilt
            shade.updateStateOnServer(key=key, value="{:.0f}% P, {:.0f}% T".format(self.to_percent(data['primary']),
                                                                                   self.to_percent(data['tilt'])), decimalPlaces=0)
        elif stateField == 3:  # 3 - Tilt
            shade.updateStateOnServer(key=key, value="{:.0f}% Open".format(self.to_percent(data['tilt'])), decimalPlaces=0)

        elif stateField == 4:  # 4 - Primary Secondary and Tilt
            shade.updateStateOnServer(key=key, value="{:.0f}% P, {:.0f}% S, {:.0f}% T".format(self.to_percent(data['primary']),
                                      self.to_percent(data['secondary']), self.to_percent(data['tilt'])), decimalPlaces=0)
