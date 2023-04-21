#!/usr/bin/env python
# coding: utf-8

import json
from powerview import PowerView
from powerview3 import PowerViewGen3
import requests


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
        super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

        self.devices = {}
        self.debug = pluginPrefs.get('debug', False)
        self.powerview = None

    #########################################
    #  Devices
    #########################################
    def createShade(self, hubHostname, shadeId, hubId):
        address = '%s:%s' % (hubHostname, shadeId)

        if self.findShade(address):
            self.debugLog('Shade %s already exists' % address)
            return

        folderId = 0
        if hubId:
            hub = indigo.devices[hubId]
            folderId = hub.folderId

        self.debugLog('Creating shade %s' % address)
        shade_data = self.findShadeOnHub(hubHostname, shadeId)

        new_shade = self.create_shade_device(address, shade_data, folderId)
        if new_shade:
            new_shade.replaceOnServer()
            return True

        return False

    #########################################
    #  Actions
    #########################################
    def activateScene(self, action):
        hub = indigo.devices[action.deviceId]
        sceneId = action.props['sceneId']

        self.debugLog('activate scene %s on hub %s' % (sceneId, hub.name))

        self.getPV(hub.address).activateScene(hub.address, sceneId)

    def activateSceneCollection(self, action):
        hub = indigo.devices[action.deviceId]
        sceneCollectionId = action.props['sceneCollectionId']

        self.debugLog('activate scene collection %s on hub %s' % (sceneCollectionId, hub.name))

        self.getPV(hub.address).activateSceneCollection(hub.address, sceneCollectionId)

    def calibrateShade(self, action):
        shade = indigo.devices[action.deviceId]


        hubHostname, shadeId = shade.address.split(':')

        self.debugLog('Calibrating shade %s (%s) (id:%s)' % (shade.name, shade.id, shadeId))

        self.getPV(hubHostname).calibrateShade(hubHostname, shadeId)

    def jogShade(self, action):
        shade = indigo.devices[action.deviceId]

        hubHostname, shadeId = shade.address.split(':')

        self.debugLog('Jogging shade %s (%s) (id:%s)' % (shade.name, shade.id, shadeId))

        self.getPV(hubHostname).jogShade(hubHostname, shadeId)

    def stopShade(self, action):
        shade = indigo.devices[action.deviceId]
        hubHostname, shadeId = shade.address.split(':')
        self.debugLog('Stopping shade %s (%s) (id:%s)' % (shade.name, shade.id, shadeId))
        self.getPV(hubHostname).stopShade(hubHostname, shadeId)
        self.updateShadeLater(shade)

    def setShadePosition(self, action):
        shade = indigo.devices[action.deviceId]
        primary = action.props.get('primary', '')
        secondary = action.props.get('secondary', '')
        tilt = action.props.get('tilt', '')
        velocity = action.props.get('velocity', '')

        self.debugLog('Setting position of %s (%s) primary (bottom): %s, secondary (top): %s, tilt: %s, velocity: %s' % \
                    (shade.name, action.deviceId, primary, secondary, tilt, velocity))

        hubHostname, shadeId = shade.address.split(':')

        if shade.states['generation'] == 2:
            top = int(float(primary) / 100.0 * 65535.0)
            bottom = int(float(secondary) / 100.0 * 65535.0)
            self.getPV(hubHostname).setShadePosition(hubHostname, shadeId, top, bottom)
        else:
            primary = float(primary) / 100.0
            secondary = float(secondary) / 100.0
            tilt = float(tilt) / 100.0
            velocity = float(velocity) / 100.0

            positions = {'primary':primary, 'secondary':secondary, 'tilt':tilt, 'velocity':velocity}
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

            pos = data.get('positions')
            if pos:
                if 'primary' in pos:  # Gen 3
                    valuesDict['primary'] = "{:.0f}".format(self.to_percent(pos['primary']))
                    valuesDict['secondary'] = "{:.0f}".format(self.to_percent(pos['secondary']))
                    valuesDict['tilt'] = "{:.0f}".format(self.to_percent(pos['tilt']))
                    valuesDict['velocity'] = "{:.0f}".format(self.to_percent(pos['velocity']))
                    valuesDict['enableTlt'] = (capabilities in [1, 2, 4, 5, 9, 10])  # Tilt
                elif 'posKind1' in pos:  # Gen 2
                    valuesDict['primary'] = "{:.0f}".format(self.to_percent(pos['position1'], 65535))
                    valuesDict['secondary'] = "{:.0f}".format(self.to_percent(pos['position2'], 65535))
                    valuesDict['tilt'] = 0
                    valuesDict['velocity'] = 0
                    valuesDict['enableTlt'] = False  # Tilt
                    valuesDict['enableVel'] = False

        return valuesDict

    def discoverShades(self, valuesDict, typeId, deviceId):
        address = valuesDict['address']

        self.debugLog('Discovering shades on %s' % address)
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
                for dev in shade_devices: shade_dev_addresses.append(dev.address)

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
        return 'open'

    def runConcurrentThread(self):
        try:
            while True:
                for shade in indigo.devices.iter('self.PowerViewShade'):
                    props = shade.pluginProps
                    need_upd = props.get('need_update', 0)
                    if need_upd > 0:
                        # update device with new position
                        self.updateShade(shade)
                        need_upd -= 1
                        props.update({'need_update':need_upd})
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

        if not valid: return valid, valuesDict, errors_dict
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

        if not valid: return valid, valuesDict, errors_dict
        return valid, valuesDict

    #########################################
    #  Utilities
    #########################################
    def create_shade_device(self, address, data, folderId):
        name = data['name']
        new_shade = None

        while new_shade is None:
            try:
                new_shade = indigo.device.create(
                    protocol=indigo.kProtocol.Plugin,
                    address=address,
                    deviceTypeId='PowerViewShade',
                    name=name,
                    description="Shade {} in {}".format(data['name'], data['room']),
                    folder=folderId
                )
            except Exception as nnu:
                if name == data['name']:
                    self.errorLog("Another device exists with the same name as shade {} at address {}.".format(name, address))
                name += " " + str(data['shadeId'])

        return new_shade

    def findShadeOnHub(self, hubHostname, shadeId):
        shade_data = self.getPV(hubHostname).shade(hubHostname, shadeId)
        shade_data['shadeType'] = self.SHADE_TYPE[shade_data['capabilities']]

        if 'positions' in shade_data:
            shadePositions = shade_data.pop('positions')
            if 'posKind1' in shadePositions:
                shadePositions.update(primary=shadePositions['position1'], secondary=shadePositions['position2'], tilt=0, velocity=0)
            shadePositions['open'] = self.to_percent(shadePositions['primary']) + self.to_percent(shadePositions['secondary'])
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

    def to_percent(self, pos, divr=1.0):
        return float(pos) / divr * 100.0

    def update(self, device):
        if device.deviceTypeId == 'PowerViewShade':
            self.updateShade(device)

    def updateShade(self, shade):
        self.debugLog('Updating shade %s' % shade.address)

        if shade.address == '':
            return

        hubHostname, shadeId = shade.address.split(':')

        data = self.findShadeOnHub(hubHostname, shadeId)
        data.pop('name')  # don't overwrite local changes

        shade_states_details = super(Plugin, self).getDeviceStateList(shade)
        shade_states = []
        for shade_states_detail in shade_states_details:
            shade_states.append(shade_states_detail['Key'])

        # update the shade state for items in the device.
        # PV2 hubs have at least one additional data item
        # (signalStrengh) not in the device definition
        shade.stateListOrDisplayStateIdChanged()  # Ensure any new states are added to this shade
        for key in data.keys():
            if key in shade_states or key in shade.states:  # update if hub has state key from Devices.xml. This adds new states.
                if key == 'open':
                    shade.updateStateOnServer(key=key, value=data[key], uiValue="{:.0f}% Open".format(data[key]), decimalPlaces=0)
                else:
                    shade.updateStateOnServer(key=key, value=data[key])

    def updateShadeLater(self, shade):
        """ Save an indicator in plugin properties for this shade to signal to do an update later, after it has moved. """
        props = shade.pluginProps
        props.update({'need_update': 4})
        shade.replacePluginPropsOnServer(props)

