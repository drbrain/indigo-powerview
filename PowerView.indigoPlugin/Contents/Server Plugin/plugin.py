#!/usr/bin/env python
# coding: utf-8
import inspect
import logging
from powerview2 import PowerView
from powerview3 import PowerViewGen3
import requests
try:
    import indigo
except ImportError:
    pass

POWERVIEW_DEVICES = 'net.segment7.powerview.self'
POWERVIEW_ID = 'net.segment7.powerview'
POWERVIEW_HUB = 'PowerViewHub'
POWERVIEW_SHADE = 'PowerViewShade'

powerview2: PowerView = None
powerview3: PowerViewGen3 = None


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
        self.debugSetting = pluginPrefs.get('debugPref', False)
        self.logger = logging.getLogger(pluginPrefs.get('logger', 'Plugin'))
        self.production = 'PowerView' == pluginDisplayName  # No exceptions when production is True
        self.devices = {}
        self.hubs = {}

    class HDHub:
        def __init__(self, hub_address, generation):
            global powerview2
            global powerview3

            self.hub_address = hub_address
            self.generation = generation
            if generation == 'V3' or generation == 3:
                self._driver = powerview3
            else:
                self._driver = powerview2

        @property
        def driver(self):
            if not self._driver:
                self._driver = powerview3 if self.generation == 'V3' else powerview2
            return self._driver

        @driver.setter
        def driver(self, new_driver):
            self._driver = new_driver

    def startup(self):
        global powerview2
        global powerview3

        # prefs are set when testing
        powerview2 = self.pluginPrefs.get("pv2", PowerView(self.pluginPrefs))
        powerview3 = self.pluginPrefs.get("pv3", PowerViewGen3(self.pluginPrefs))
        self.logger.setLevel('INFO' if not self.debugSetting else 'DEBUG')

    #########################################
    #  Actions
    #########################################
    def activateScene(self, action):
        hub = indigo.devices[action.deviceId]
        sceneId = action.props['sceneId']

        indigo.server.log(f"activate scene {sceneId} on hub {hub.name}")
        self.get_pv(hub.address).activateScene(hub.address, sceneId)
        self.update_shade_later(hub)

    def activateSceneCollection(self, action):
        hub = indigo.devices[action.deviceId]
        sceneCollectionId = action.props['sceneCollectionId']

        indigo.server.log(f'activate scene collection {sceneCollectionId} on hub {hub.name}')
        self.get_pv(hub.address).activateSceneCollection(hub.address, sceneCollectionId)
        self.update_shade_later(hub)

    def calibrateShade(self, action):
        shade = indigo.devices[action.deviceId]
        hubHostname, shadeId = shade.address.split(':')

        indigo.server.log('Calibrating shade %s (%s) (id:%s)' % (shade.name, shade.id, shadeId))
        self.get_pv(hubHostname).calibrateShade(hubHostname, shadeId)

    def jogShade(self, action):
        shade = indigo.devices[action.deviceId]
        hubHostname, shadeId = shade.address.split(':')

        indigo.server.log('Jogging shade %s (%s) (id:%s)' % (shade.name, shade.id, shadeId))
        self.get_pv(hubHostname).jogShade(hubHostname, shadeId)
        self.update_shade_later(shade)

    def stopShade(self, action):
        shade = indigo.devices[action.deviceId]
        hubHostname, shadeId = shade.address.split(':')
        indigo.server.log('Stopping shade %s (%s) (id:%s)' % (shade.name, shade.id, shadeId))
        self.get_pv(hubHostname).stopShade(hubHostname, shadeId)
        self.update_shade_later(shade)

    def setShadePosition(self, action):
        shade = indigo.devices[action.deviceId]
        primary = int(action.props.get('primary', '0'))
        secondary = int(action.props.get('secondary', '0'))
        tilt = int(action.props.get('tilt', '0'))
        velocity = int(action.props.get('velocity', '0'))

        self.logger.debug('Setting position of %s (%s) to primary (bottom): %s, secondary (top): %s, tilt: %s, velocity: %s' %
                         (shade.name, action.deviceId, primary, secondary, tilt, velocity))

        hubHostname, shadeId = shade.address.split(':')

        positions = {"primary": primary, "secondary": secondary, "tilt": tilt, "velocity": velocity}
        self.get_pv(hubHostname).setShadePosition(hubHostname, shadeId, positions)

        self.update_shade_later(shade)

    #########################################
    #  Indigo UI Support Routines
    #########################################
    def getCurrentPosition(self, valuesDict, typeId, devId):
        """ Returns the current values of primary, secondary, tilt and velocity for
            existing shade devices. If the shade device is new, the devId will be
            zero, so the shade  address is unavailable.
        """
        #   typeId is the device type specified in the Devices.xml
        #   devId is the device ID - 0 if it's a new device

        if devId:
            shade = indigo.devices[devId]
            hubHostname, shadeId = shade.address.split(':')

            self.get_pv(hubHostname).jogShade(hubHostname, shadeId)
            data = self.get_pv(hubHostname).shade(hubHostname, shadeId)

            # Enable/disable entry fields so only those needed are enabled.
            capabilities = data.get('capabilities', -1)
            valuesDict['enablePri'] = (capabilities in [0, 1, 2, 3, 4, 6, 7, 8, 9, 10])  # Primary
            valuesDict['enableSec'] = (capabilities in [7, 8, 9, 10])  # Secondary

            pos = data.get('positions')
            if pos:
                valuesDict['primary'] = "{:.0f}".format(pos['primary'])
                valuesDict['secondary'] = "{:.0f}".format(pos['secondary'])
                valuesDict['tilt'] = "{:.0f}".format(pos['tilt'])
                valuesDict['velocity'] = "{:.0f}".format(pos['velocity'])
                valuesDict['enableTlt'] = (capabilities in [1, 2, 4, 5, 9, 10])  # Tilt

            if shade.states['generation'] == 2:  # Gen 2
                valuesDict['enableTlt'] = False  # Tilt
                valuesDict['enableVel'] = False

        return valuesDict

    def discoverShades(self, valuesDict, typeId, hub_deviceId):
        hub_address = valuesDict.get('address')

        if not hub_address or not self.validate_hub(hub_address):
            valuesDict['message'] = "The Hostname/IP must be the address of a valid Hunter Douglas hub or gateway."
            return valuesDict

        indigo.server.log(f'Discovering shades on {hub_address}')
        shadeIds = self.get_pv(hub_address).shadeIds(hub_address)
        device_count = 0

        for shadeId in shadeIds:
            if self.create_shade(hub_address, shadeId, hub_deviceId):
                device_count += 1

        valuesDict['message'] = "Discovered {} Shade{}, and Created {} Device{}.".format(
            len(shadeIds), 's' if len(shadeIds) != 1 else '', device_count, 's' if device_count != 1 else '')

        return valuesDict

    def listHubs(self, filter="", valuesDict="", type="", targetId=0):
        hub_list = []
        my_devices = indigo.devices.iter(POWERVIEW_HUB)
        for device in my_devices:
            hub_list.append([device.id, device.name])

        hub_list = sorted(hub_list, key=lambda pair: pair[1])
        return hub_list

    def listScenes(self, filter="", valuesDict="", type="", targetId=0):
        hub = self.devices[targetId]

        scenes = self.get_pv(hub.address).scenes(hub.address)
        scene_list = []

        for scene in scenes:
            scene_list.append([scene['id'], scene['name']])

        scene_list = sorted(scene_list, key=lambda pair: pair[1])
        return scene_list

    def listSceneCollections(self, filter="", valuesDict="", type="", targetId=None):
        hub = self.devices[targetId]

        data = self.get_pv(hub.address).sceneCollections(hub.address)
        scene_list = []

        for sceneCollection in data:
            scene_list.append([sceneCollection['id'], sceneCollection['name']])

        scene_list = sorted(scene_list, key=lambda pair: pair[1])
        return scene_list

    def listShades(self, filter="", valuesDict=None, typeId="", targetId=0):
        """ Produces a list of all shades on all hubs that do NOT exist as devices."""
        shade_list = []
        my_devices = indigo.devices.iter(POWERVIEW_HUB)

        if my_devices:
            for hub in my_devices:
                shade_devices = indigo.devices.iter(POWERVIEW_SHADE)
                shade_dev_addresses = []
                for dev in shade_devices:
                    shade_dev_addresses.append(dev.address)

                shade_ids = self.get_pv(hub.address).shadeIds(hub.address)
                for shade_id in shade_ids:
                    address = '%s:%s' % (hub.address, shade_id)

                    if address not in shade_dev_addresses:
                        shade = self.get_pv(hub.address).shade(hub.address, shade_id)
                        room_name = self.get_pv(hub.address).room(hub.address, shade['roomId'])['name']
                        shade_name = shade['name']
                        shade_list.append([address, '%s - %s' % (room_name, shade_name)])

            shade_list = sorted(shade_list, key=lambda pair: pair[1])

        return shade_list

    #########################################
    #  Indigo Defined
    #########################################
    def closedPrefsConfigUi(self, valuesDict, userCancelled):
        if not userCancelled:
            self.debugSetting = valuesDict.get('debugPref', False)
            if isinstance(self.debugSetting, bool):
                if self.debugSetting:
                    self.logger.setLevel('DEBUG')
                else:
                    self.logger.setLevel('INFO')
        return True

    def deviceStartComm(self, device):
        if device.deviceTypeId == POWERVIEW_HUB:
            self.logger.debug(f'About to validate hub at address={device.address}.')
            self.validate_hub(device.address, device=device)

        if device.id not in self.devices:
            self.devices[device.id] = device
            self.update(device)

    def deviceStopComm(self, device):
        if device.id in self.devices:
            self.devices.pop(device.id)

    def getDeviceDisplayStateId(self, dev):
        """ Returns the property name to be shown in the State column, since the <UiDisplayStateId>
        tag seems to be ignored (and undocumented)."""
        if dev.deviceTypeId == POWERVIEW_SHADE:
            return 'open'
        return None

    def runConcurrentThread(self):
        try:
            while True:
                for shade in indigo.devices.iter(POWERVIEW_SHADE):
                    props = shade.pluginProps
                    need_upd = props.get('need_update', 0)
                    if need_upd > 0:
                        need_upd -= 1
                        # This props update will trigger call to deviceStartComm which will update the position
                        props.update({'need_update': need_upd})
                        shade.replacePluginPropsOnServer(props)

                self.sleep(15)

        except self.StopThread:
            pass

    def validateActionConfigUi(self, valuesDict, typeId, deviceId):
        valid = True
        errors_dict = indigo.Dict()

        if typeId == 'setShadePosition':
            for pos_name in ['primary', 'secondary', 'tilt', 'velocity']:
                pos_val = valuesDict.get(pos_name, '0')
                pos_val = int(pos_val) if pos_val.isdigit() else -1
                if pos_val not in range(0, 101):
                    errors_dict[pos_name] = "'{}' must be a percentage 0-100, where 0 is closed and 100 is fully open.".format(pos_name.title())
                    valid = False

        if not valid:
            return valid, valuesDict, errors_dict
        return valid, valuesDict

    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        valid = True
        errors_dict = indigo.Dict()
        if typeId == POWERVIEW_SHADE:
            heading = valuesDict.get('heading')
            if heading and heading not in range(0, 361):
                errors_dict['heading'] = "Heading must be a compass reading in degrees from 0 to 360."
                valid = False

            state_field = valuesDict.get('stateField', '0')
            if state_field and state_field not in range(5):
                errors_dict['stateField'] = "Invalid state selection."
                valid = False

            if valid:
                shade = indigo.devices[devId]
                props = shade.pluginProps
                props['stateField'] = state_field if state_field else 0
                shade.replacePluginPropsOnServer(props)

        elif typeId == POWERVIEW_HUB:
            hub_address = valuesDict.get("address", None)
            if not hub_address:
                errors_dict['address'] = "The Hostname/IP must be the hostname or IP address of a valid Hunter Douglas hub or gateway."
                valid = False

            if not self.validate_hub(hub_address):
                errors_dict['address'] = "That Hostname/IP is not the hostname or IP address of a valid Hunter Douglas hub or gateway."
                valid = False

        if not valid:
            return valid, valuesDict, errors_dict
        else:
            return valid, valuesDict

    #########################################
    #  Utilities. Only used in this file.
    #########################################
    def create_shade(self, hub_hostname, shade_id, hub_id):
        shade_address = f"{hub_hostname}:{shade_id}"

        for device in indigo.devices.iter(POWERVIEW_DEVICES):
            self.logger.debug(f"device.address={device.address}")
            if device.address == shade_address:
                indigo.server.log("Shade {} already exists".format(shade_address))
                return False

        folder_id = None
        if hub_id:
            hub = indigo.devices[hub_id]
            folder_id = hub.folderId

        indigo.server.log("Creating shade {}".format(shade_address))
        shade_data = self.find_shade_on_hub(hub_hostname, shade_id)

        try:
            new_shade = self.create_shade_device(shade_address, shade_data, folder_id)
            if new_shade:
                new_shade.replaceOnServer()
                self.update_shade_later(new_shade)
                return True
        except Exception as ex1:
            self.logger.debug(f'Exception in create_shade of {shade_address} ', exc_info=True)
            pass

        self.logger.debug(f'create_shade failed on address {shade_address}')
        return False

    def create_shade_device(self, address, data, folder_id):
        name = data['name']
        room = '' if 'room' not in data else 'in {}'.format(data['room'])
        new_shade = None

        try:
            new_shade = indigo.device.create(
                protocol=indigo.kProtocol.Plugin,
                address=address,
                deviceTypeId=POWERVIEW_SHADE,
                pluginId=POWERVIEW_ID,
                name=name,
                description="Shade {} {}".format(data['name'], room),
                props={'stateField': 0, 'need_update': 0},  # default stateField to 0 for primary position as visible state
                folder=folder_id
            )
        except (OSError, LookupError) as ex1:
            self.logger.exception(f"Create failed for shade {name} at address {address}.", exc_info=True)
            # raise ex1

        return new_shade

    def find_shade_on_hub(self, hubHostname, shadeId, need_room=False):
        shade_data = self.get_pv(hubHostname).shade(hubHostname, shadeId, room=need_room)
        if not shade_data:
            return {}

        shade_data['shadeType'] = self.SHADE_TYPE[shade_data['capabilities']]

        if 'positions' in shade_data:
            shade_positions = shade_data.pop('positions')
            shade_positions['open'] = ''
            shade_data.update(shade_positions)
        return shade_data

    def get_pv(self, hub_address):
        """ Detects and returns the correct powerview class, based on how the gateway responds."""
        found_by = 'n/a'
        pv = None
        if hub_address in self.hubs:
            hub = self.hubs[hub_address]
            pv = hub.driver
            found_by = 'self.hubs' if pv else 'self.hubs has blank driver'

        else:
            if self.validate_hub(hub_address):
                hub = self.hubs[hub_address]
                pv = hub.driver
                found_by = 'validate_hub' if pv else f'validate added hub {hub} to self.hubs'

        self.logger.debug(f'pv={pv} from: {found_by}')
        if not pv and not self.production:
            raise KeyError(f'Invalid hub address {hub_address}.')
        return pv

    def validate_hub(self, hub_address, device=None) -> bool:
        """Validates that the supplied hub address is a valid hub.
            If the indigo device is supplied, or it can be looked up, the hub is added to the list of known hubs so
            the next time it can be found fast."""
        global powerview2
        global powerview3

        gen = None
        if not hub_address:
            pass

        elif hub_address in self.hubs:
            gen = self.hubs[hub_address].generation

        elif device is not None and 'generation' in device.states:
            gen = device.states['generation']
            hub = self.HDHub(hub_address, generation=gen)
            self.hubs[hub_address] = hub
            self.logger.debug(f'Hub at {hub_address} found with gen={hub.generation} from device {device.name}')

        else:
            try:
                home = powerview3.do_get(f"http://{hub_address}/home", timeout=30.0)
            except OSError:
                home = None
                self.logger.debug(f"validate_hub: Timeout on get http://{hub_address}/home")
            self.logger.debug(f"Get http://{hub_address}/home returned {home}")
            if home and home.status_code == requests.codes.ok:
                gen = "V3"

            else:
                try:
                    home = powerview2.do_get(f"http://{hub_address}/api/fwversion", timeout=30.0)
                except OSError:
                    home = None
                    self.logger.debug(f"validate_hub: Timeout on get http://{hub_address}/api/fwversion")
                self.logger.debug(f"Get http://{hub_address}/api/fwversion returned {home}")
                if home and home.status_code == requests.codes.ok:
                    gen = "V2"

        if hub_address not in self.hubs and gen:
            hub = self.HDHub(hub_address, generation=gen)
            self.hubs[hub_address] = hub

        if not gen:
            caller = inspect.stack()[1][3]
            self.logger.error(f'Hub {hub_address} not found for device={"None" if not device else device.name} when called from {caller}.')
            if not self.production:
                raise KeyError(f"Invalid hub address: {hub_address}")
            else:
                indigo.server.log(f'Invalid hub address: {hub_address}')

        return (gen is not None)

    def update(self, device):
        if device.deviceTypeId == POWERVIEW_HUB:
            pv = self.get_pv(device.address)
            if pv:
                gen = pv.GENERATION[1]  # select the digit after the leading 'V'
                device.stateListOrDisplayStateIdChanged()  # Ensure any new states are added to this shade
                device.updateStateOnServer(key='generation', value=gen)

        elif device.deviceTypeId == POWERVIEW_SHADE:
            if device.address == '':
                return

            try:
                hub_hostname, shade_id = device.address.split(':')

                data = self.find_shade_on_hub(hub_hostname, shade_id)
                if not data:
                    return
                data.pop('name')  # don't overwrite local changes

                # Get all states defined for this device, since they may have been upgraded.
                shade_states_details = super(Plugin, self).getDeviceStateList(device)
                shade_states = []
                if shade_states:
                    for shade_states_detail in shade_states_details:
                        shade_states.append(shade_states_detail['Key'])

                # update the shade state for items in the device.
                # PV2 hubs have at least one additional data item
                # (signalStrength) not in the device definition
                device.stateListOrDisplayStateIdChanged()  # Ensure any new states are added to this shade
                for key in data.keys():
                    if key in shade_states:  # update if hub has state key from Devices.xml. This adds new states.
                        if key == 'open':
                            self.update_shade_open_state(device, data, key)
                        else:
                            device.updateStateOnServer(key=key, value=data[key])
            except:
                self.logger.exception(f"Exception in update() of device={device.name} with address={device.address}.", exc_info=True)

    def update_shade_later(self, dev):
        """ Save an indicator in plugin properties for this shade to signal to do an update later, after it has moved. """
        if dev.deviceTypeId == POWERVIEW_SHADE:
            props = dev.pluginProps
            props.update({'need_update': 4})
            dev.replacePluginPropsOnServer(props)

        elif dev.deviceTypeId == POWERVIEW_HUB:
            for shade in indigo.devices.iter(POWERVIEW_SHADE):
                if shade.address.startswith(dev.address):
                    props = shade.pluginProps
                    props.update({'need_update': 4})
                    shade.replacePluginPropsOnServer(props)

    def update_shade_open_state(self, shade, data, key):
        state_field = shade.pluginProps.get('stateField', 0)

        if state_field == 0:  # 0 - Primary
            shade.updateStateOnServer(key=key, value="{:.0f}% Open".format(data['primary']), decimalPlaces=0)

        elif state_field == 1:  # 1 - Primary and Secondary
            shade.updateStateOnServer(key=key, value="{:.0f}% P, {:.0f}% S".format(data['primary'],
                                                                                   data['secondary']), decimalPlaces=0)
        elif state_field == 2:  # 2 - Primary and Tilt
            shade.updateStateOnServer(key=key, value="{:.0f}% P, {:.0f}% T".format(data['primary'],
                                                                                   data['tilt']), decimalPlaces=0)
        elif state_field == 3:  # 3 - Tilt
            shade.updateStateOnServer(key=key, value="{:.0f}% Open".format(data['tilt']), decimalPlaces=0)

        elif state_field == 4:  # 4 - Primary Secondary and Tilt
            shade.updateStateOnServer(key=key, value="{:.0f}% P, {:.0f}% S, {:.0f}% T".format(data['primary'],
                                                                                              data['secondary'],
                                                                                              data['tilt']), decimalPlaces=0)
