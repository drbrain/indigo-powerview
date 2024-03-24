
try:
    import indigo
except ImportError:
    pass
import re
from time import sleep
import pytest
import requests
import logging
from pv_tests import mock_powerview as mp
from plugin import Plugin

# DEVICE_IDS = {'V3': mp.DEV_ID_V3, 'V2': mp.DEV_ID_V2}
OK = requests.codes.ok
POWERVIEW_DEVICES = 'net.segment7.powerview.self'
POWERVIEW_ID = 'net.segment7.powerview'
POWERVIEW_HUB = 'PowerViewHub'
POWERVIEW_SHADE = 'PowerViewShade'

gen = ''
logger = logging.getLogger("wsgmac.com.test.powerview")
logger.setLevel(10)
plg: Plugin  # PowerView Plugin instance used for all tests
prefs = {}  # PluginPrefs used to send
pv = None  # PowerView driver instance used for all tests


def gplg(pv_driver, gen_in):
    global gen
    global plg
    global pv

    gen = gen_in
    pv = pv_driver

    if 'pv3' not in prefs and gen == 'V3':
        prefs['pv3'] = pv_driver
    if 'pv2' not in prefs and gen == 'V2':
        prefs['pv2'] = pv_driver
    prefs['logger'] = 'wsgmac.com.test.powerview'
    prefs['debugPref'] = True
    plg = TestPlugin(POWERVIEW_ID, 'PowerViewPluginTest', "0", prefs)
    plg.startup()
    logger.debug("gplg: gen={}, pv={}".format(gen, pv))


class PluginAction:
    """
    deviceId	integer	The id of the device
    pluginId	string	The unique ID of the plugin, specified in the Info.plist for the plugin (or it’s documentation)
    pluginTypeId	string	The id specified in the Actions.xml (or it’s documentation)
    props	dictionary	An indigo.Dict() defining this action's parameters
    """
    deviceId = 0
    pluginId = ''
    pluginTypeId = ''
    props = {}

    def __init__(self, initial: dict):
        self.deviceId = initial.get('deviceId', 0)
        self.pluginId = initial.get('pluginId', POWERVIEW_ID)
        self.pluginTypeId = initial.get('pluginTypeId', '')
        self.props = initial.get('props', {})

    def __repr__(self):
        return f"Action: deviceId={self.deviceId}, pluginTypeId={self.pluginTypeId}, props={self.props}"


class TestPlugin(Plugin):
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        super().__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

    def listScenes(self, filter="", valuesDict="", type="", targetId=0):
        self.load_devices()
        return super().listScenes(filter=filter, valuesDict=valuesDict, type=type, targetId=targetId)

    def listSceneCollections(self, filter="", valuesDict="", type="", targetId=0):
        self.load_devices()
        return super().listSceneCollections(filter=filter, valuesDict=valuesDict, type=type, targetId=targetId)

    def load_devices(self):
        # Make sure all hubs are listed in self.devices. This only does anything for mocked hubs.
        for hub in indigo.devices.iter():
            if hub.id not in self.devices:
                self.devices[hub.id] = hub


def assert_put_response(item_name, config, hub_address, id):
    if 'url' in config:
        if mp.MockPowerView.mock_put_called():
            put_response = mp.put_response
            if put_response:
                data = put_response.json()
                url = config['url'].format(hub_address=hub_address, id=id)

                assert put_response.status_code == OK, \
                    f'Unexpected status code for "{item_name}" put={put_response.status_code} on url={put_response.url}'
                assert put_response.url == url, f'Invalid url={put_response.url} for "{item_name}"'
                if data:
                    compare_data = config['compare_put_send']
                    assert data == compare_data, f'Invalid Put, body={data} for "{item_name} on url={put_response.url}"'
    else:
        logger.debug(f"assert_put_response for {item_name} is called but not configured.")


def perform_shade_action(hub, props, type_id, do_action):
    action = PluginAction({'deviceId': -1, 'pluginTypeId': type_id, 'props': props})
    dev_found = 0
    for shade in indigo.devices.iter(POWERVIEW_SHADE):
        if shade.address.startswith(hub):
            dev_found += 1
            action.deviceId = shade.id
            do_action(action, shade)
    return dev_found


# ====================================================

def testbody_create_shade(hub_address, config):
    logger.debug("testbody  ==========================  create_shade: hub={}".format(hub_address))
    # create_shade(hubHostname, shadeId, hubId) -> bool:
    # create_shade_device(address, shade_data, folderId) -> indigo.device:
    shade_id = 1  # hard coded shade id to avoid creating a duplicate indigo device
    address = f'{hub_address}:{shade_id}'
    new_shade = None

    if plg.create_shade(hub_address, shade_id, 0):
        for new_shade in indigo.devices.iter(POWERVIEW_SHADE):
            logger.debug(f'Checking dev {new_shade} for address={address}')
            if new_shade.address == address:
                break
        else:
            new_shade = None

        assert new_shade, f'Create_shade returned True but no device has the matching address of {address}'
        logger.debug(f'Deleting shade id={new_shade.id}, address={new_shade.address}')
        delete_shade(new_shade)
    else:
        assert True, f'create_shade failed to create the device with address {address}'

    assert new_shade.address == address, f"Invalid address={new_shade.address} w/ id={new_shade.id} given address{address}."
    # assert new_shade.name == shade_data['name'], f"Invalid name={shade_data['name']}."
    logger.debug("==========================")


def find_device(hub_address):
    for hub in indigo.devices.iter(POWERVIEW_HUB):
        logger.debug(f'find_device: Devices.iter returned {hub}')
        if hub.address == hub_address:
            return hub
    logger.debug(f'find_device: Devices.iter found no match for {hub_address}')
    return None


def testbody_activate_scene(hub_address, config):
    # activateScene(self, action):
    logger.debug("testbody  ==========================  activate_scene: hub={}".format(hub_address))

    hub = find_device(hub_address)
    logger.debug(f"testbody  ==========================  activate_scene: after find returned {hub}")
    hub_device_id = hub.id
    scenes = plg.listScenes(targetId=hub_device_id)
    logger.debug(f"testbody  ==========================  activate_scene: found {len(scenes)} scenes.")

    for scene in scenes:
        scene_id = scene[0]
        action = PluginAction({'deviceId': hub_device_id, 'props': {'sceneId': scene_id}})
        plg.activateScene(action)

        assert_put_response(f'activate scene({scene_id})', config, hub_address, scene_id)

    logger.debug("==========================")


def testbody_activate_scene_collection(hub_address, config):
    # activateSceneCollection(self, action):
    logger.debug("testbody  ==========================  activate_scene_collection: hub={}".format(hub_address))

    hub = find_device(hub_address)
    scenes = plg.listSceneCollections(targetId=hub.id)

    # Only test one collection since it is only supported on V2, and uses a Get request, not Put, so it will be run by the test when using the hub.
    if scenes:
        scene_id = scenes[0][0]
        action = PluginAction({'deviceId': hub.id, 'props': {'sceneCollectionId': scene_id}})
        plg.activateSceneCollection(action)

        assert_put_response(f'activate scene collections({scene_id})', config, hub_address=hub_address, id=scene_id)

    logger.debug("==========================")


def testbody_calibrate_shade(hub, config):
    # calibrate_shade(self, action):
    logger.debug("testbody  ==========================  calibrate_shade: hub={}".format(hub))

    def body_calibrate_shade(action, shade):
        plg.calibrateShade(action)

        hub_address, shade_id = shade.address.split(':')
        assert_put_response(f'calibrate_shade({shade.name})', config, hub_address=hub_address, id=shade_id)

    type_id = 'calibrate_shade'
    props = {}
    dev_found = perform_shade_action(hub, props, type_id, body_calibrate_shade)

    logger.debug(f"testbody_calibrate_shade: Tested {dev_found} shades.")
    logger.debug("==========================")


def testbody_jog_shade(hub, config):
    # jogShade(self, action):
    logger.debug("testbody  ==========================  jog_shade: hub={}".format(hub))

    def body_jog_shade(action, shade):
        plg.jogShade(action)

        hub_address, shade_id = shade.address.split(':')
        assert_put_response(f'jog_shade({shade.name})', config, hub_address=hub_address, id=shade_id)

    type_id = 'jog_shade'
    props = {}
    dev_found = perform_shade_action(hub, props, type_id, body_jog_shade)

    logger.debug(f"testbody  ==========================  jog_shade: Tested {dev_found} shades.")
    logger.debug("==========================")


def testbody_stop_shade(hub, config):
    # stopShade(self, action):
    logger.debug("testbody  ==========================  stopShade: hub={}".format(hub))

    def body_stop_shade(action, shade):
        plg.stopShade(action)

        hub_address, shade_id = shade.address.split(':')
        assert_put_response(f'stopShade({shade.name})', config, hub_address=hub_address, id=shade_id)

    logger.debug("testbody  ==========================  stop_shade: hub={}".format(hub))
    type_id = 'stop_shade'
    props = {}
    dev_found = perform_shade_action(hub, props, type_id, body_stop_shade)

    logger.debug(f"testbody  ==========================  stop_shade: Tested {dev_found} shades.")
    logger.debug("==========================")


def testbody_set_shade_position(hub, config, gen2=False):
    def body_set_body_position(action, shade):
        logger.debug(f"testbody_set_shade_position: Setting shade action={action}")
        plg.setShadePosition(action)

        hub_address, shade_id = shade.address.split(':')
        assert_put_response(f'set_shade_position({shade.name})', config, hub_address=hub_address, id=shade_id)

    type_id = 'setShadePosition'
    props = {'primary': 10, 'secondary': 20, 'tilt': 30, 'velocity': 40}
    logger.debug(f"testbody  ==========================  set_shade_position: hub={hub}, props={props}")
    dev_found = perform_shade_action(hub, props, type_id, body_set_body_position)

    if gen2:
        props = {'primary': 6554, 'secondary': 13107, 'tilt': 19661, 'velocity': 26214}
        logger.debug(f"testbody  ==========================  set_shade_position: hub={hub}, props={props}")
        dev_found += perform_shade_action(hub, props, type_id, body_set_body_position)

    logger.debug(f"testbody_set_shade_position: Tested {dev_found} shades.")
    logger.debug("==========================")


def testbody_current_position(hub, config):
    logger.debug("testbody  ==========================  current_position: hub={}".format(hub))
    # def getCurrentPosition(self, valuesDict, typeId, devId):
    # values_dict contains the content of the UI window at the time the user clicks the 'Current Position' button. This is NOT the current position.

    values_dict = {'current': '', 'enablePri': True, 'enableSec': True, 'enableTlt': True, 'enableVel': True,
                   'lblNumbers': '', 'primary': '10', 'secondary': '20', 'tilt': '30', 'velocity': '40'}
    type_id = 'getShadePosition'

    dev_id = None
    for shade in indigo.devices.iter(POWERVIEW_SHADE):
        logger.debug(f'Devices.iter returned {shade.address}')
        dev_id = shade.id

    logger.debug(f"About to call getCurrentPosition: dev_id={dev_id}")
    values_dict2 = plg.getCurrentPosition(values_dict, type_id, dev_id)
    logger.debug(f"values_dict2={values_dict2}")
    assert values_dict2, f'Empty response from getCurrentPosition'
    # {'primary': 46, 'secondary': 25, 'tilt': 0, 'velocity': 0}
    assert values_dict2['primary'].isdecimal(), f"primary value is not only digits. primary={values_dict2['primary']}"
    assert values_dict2['secondary'].isdecimal(), f"secondary value is not only digits. secondary={values_dict2['secondary']}"
    assert values_dict2['tilt'].isdecimal(), f"tilt value is not only digits. tilt={values_dict2['tilt']}"
    assert values_dict2['velocity'].isdecimal(), f"velocity value is not only digits. velocity={values_dict2['velocity']}"
    assert int(values_dict2['primary']) in range(101), f"primary={values_dict2['primary']} not an integer value from 0 100"
    assert int(values_dict2['secondary']) in range(101), f"secondary={values_dict2['secondary']} not an integer value from 0 100"
    assert int(values_dict2['tilt']) in range(101), f"tilt={values_dict2['tilt']} not an integer value from 0 100"
    assert int(values_dict2['velocity']) in range(101), f"velocity={values_dict2['velocity']} not an integer value from 0 100"
    logger.debug("==========================")


def testbody_discover_shades(hub_address, config):
    # discoverShades(self, valuesDict, typeId, deviceId):
    logger.debug("testbody  ==========================  discover_shades: hub={}".format(hub_address))

    type_id = 'discoverShades'

    hub_dev_id = 0
    dev_ids = []
    for a_device in indigo.devices.iter(POWERVIEW_DEVICES):
        logger.debug(f'Found device {a_device.address}')
        dev_ids.append(a_device.id)
        if a_device['deviceTypeId'] == POWERVIEW_HUB and a_device.address == hub_address:
            hub_dev_id = a_device.id
    values_dict = {'address': hub_address}
    assert hub_dev_id
    # assert dev_ids

    try:
        logger.debug(f"About to call discoverShades: hub_dev_id={hub_dev_id}")
        values_dict2 = plg.discoverShades(values_dict, type_id, hub_dev_id)
        logger.debug(f"values_dict2={values_dict2}")

        assert values_dict2, 'No return value from discoverShades.'
        assert values_dict2['message'], 'discoverShades did not return correct message.'
        a_match = re.search(r"Discovered (\d+) Shades?, and Created (\d+) Devices?\.", values_dict2['message'])
        assert a_match, f'Failed to find any shades without a corresponding device'

        logger.debug(f"About to call discoverShades with invalid address='': dev_id={hub_dev_id}")
        values_dict2 = plg.discoverShades({'address': ''}, type_id, hub_dev_id)
        logger.debug(f"values_dict2={values_dict2}")

        assert values_dict2, 'No return value from discoverShades.'
        assert values_dict2['message'].startswith('The Hostname'), 'discoverShades did not return correct message.'

        logger.debug(f"About to call discoverShades with unknown address='unknown.tld': dev_id={hub_dev_id}")
        with pytest.raises(KeyError):
            values_dict2 = plg.discoverShades({'address': 'unknown.tld'}, type_id, hub_dev_id)
        logger.debug(f"values_dict2={values_dict2}")

        assert values_dict2, 'No return value from discoverShades.'
        assert values_dict2['message'].startswith('The Hostname'), 'discoverShades did not return correct message.'

    finally:
        for a_device in indigo.devices.iter(POWERVIEW_DEVICES):
            logger.debug(f'Check for deletion device {a_device.address}')
            if a_device.id not in dev_ids:
                delete_shade(a_device)

    logger.debug("==========================")


def delete_shade(a_device):
    if isinstance(a_device, mp.MockPowerView.DevicesMock.MockedDevice):
        logger.debug(f'Deleting shade id={a_device.id}, address={a_device["address"]}')
        a_device.delete()
    else:
        logger.debug(f'Deleting shade id={a_device.id}, address={a_device.address}')
        indigo.device.delete(a_device.id)
    sleep(2)


def testbody_list_hubs(hub, config):
    # listHubs(self, filter="", valuesDict="", type="", targetId=0):
    logger.debug("testbody  ==========================  list_hubs: hub={}".format(hub))

    hub_list = plg.listHubs()
    assert isinstance(hub_list, list), f'Return value from listHubs should be a list: hub_list={hub_list}'
    for a_hub in hub_list:
        assert len(a_hub) == 2, f'Each item in hub list should have 2 entries. a_hub={a_hub}'
        assert isinstance(a_hub[0], int), f'First entry in a hub list item should be integer.'
        assert indigo.devices[a_hub[0]].name == a_hub[1], f'Item should contain id and name of a hub: {a_hub[1]}'

    logger.debug("==========================")


def testbody_list_scenes(hub, config):
    # listScenes(self, filter="", valuesDict="", type="", targetId=0):
    logger.debug("testbody  ==========================  list_scenes: hub={}".format(hub))

    for a_hub in indigo.devices.iter(POWERVIEW_HUB):
        scene_list = plg.listScenes(targetId=a_hub.id)

        assert scene_list, f"No scenes found to test activation on hub={hub.name}"
        assert isinstance(scene_list, list), f'Return value from listScenes should be a list: scene_list={scene_list}'
        for a_scene in scene_list:
            assert len(a_scene) == 2, f'Each item in scene list should have 2 entries. a_scene={a_scene}'
            assert isinstance(a_scene[0], int), f'First entry in a scene list item should be integer: {a_scene[0]}.'
            assert isinstance(a_scene[1], str), f'Item should contain id and name of a scene: {a_scene[1]}'

    logger.debug("==========================")


def testbody_list_scene_collections(hub, config):
    # listSceneCollections(self, filter="", valuesDict="", type="", targetId=None):
    logger.debug("testbody  ==========================  list_scene_collections: hub={}".format(hub))

    for a_hub in indigo.devices.iter(POWERVIEW_HUB):
        scene_list = plg.listSceneCollections(targetId=a_hub.id)

        assert isinstance(scene_list, list), f'Return value from listSceneCollections should be a list: scene_list={scene_list}'
        for a_scene in scene_list:
            assert len(a_scene) == 2, f'Each item in sceneCollection list should have 2 entries. a_scene={a_scene}'
            assert isinstance(a_scene[0], int), f'First entry in a sceneCollection list item should be integer: {a_scene[0]}.'
            assert isinstance(a_scene[1], str), f'Item should contain id and name of a sceneCollection: {a_scene[1]}'

    logger.debug("==========================")


def testbody_list_shades(hub, config):
    # listShades(self, filter="", valuesDict=None, typeId="", targetId=0):
    logger.debug("testbody  ==========================  list_shades: hub={}".format(hub))

    shade_list = plg.listShades()

    assert isinstance(shade_list, list), f'Return value from listShades should be a list: shade_list={shade_list}'
    for a_shade in shade_list:
        assert len(a_shade) == 2, f'Each item in listShades list should have 2 entries. a_shade={a_shade}'
        assert isinstance(a_shade[0], str), f'First entry in a listShades list item should be string: {a_shade[0]}.'
        assert isinstance(a_shade[1], str), f'Item should contain id and name of a listShades: {a_shade[1]}'

    logger.debug("==========================")


def testbody_device_start_comm(hub, config):
    # deviceStartComm(self, device):
    logger.debug(f"testbody  ==========================  device_start_comm: hub={hub}")

    for dev in indigo.devices.iter(POWERVIEW_DEVICES):
        plg.deviceStartComm(dev)

    # No way to confirm correct operation
    logger.debug("==========================")


def testbody_device_stop_comm(hub, config):
    # deviceStopComm(self, device):
    logger.debug("testbody  ==========================  device_stop_comm: hub={}".format(hub))

    for dev in indigo.devices.iter(POWERVIEW_DEVICES):
        plg.deviceStopComm(dev)

    # No way to confirm correct operation
    logger.debug("==========================")


def testbody_validate_action_config_ui(hub, config):
    # validateActionConfigUi(self, valuesDict, typeId, deviceId):
    logger.debug("testbody  ==========================  validate_action_config_ui: hub={}".format(hub))

    typeId = 'setShadePosition'
    assert len(plg.validateActionConfigUi({'primary': '0', 'secondary': '0', 'tilt': '0', 'velocity': '0'}, typeId, None)) == 2, \
        'Error message returned from validateActionConfigUi when data is valid'
    result = plg.validateActionConfigUi({'primary': '105', 'secondary': '0', 'tilt': '0', 'velocity': '0'}, typeId, None)
    logger.debug(f'result={result}')
    assert len(result) == 3, 'No error message returned from validateActionConfigUi when data is invalid'
    result = result[2]
    assert len(result), 'No error message returned from validateActionConfigUi when data is invalid'
    assert result['primary'], 'Expected error message is missing.'
    assert result['primary'].startswith("'Primary'"), \
        f"Incorrect error message returned from validateActionConfigUi when data is invalid: {result['primary']}"

    logger.debug("==========================")


def testbody_validate_device_config_ui(hub, config):
    # validateDeviceConfigUi(self, valuesDict, typeId, devId):
    logger.debug("testbody  ==========================  validate_device_config_ui: hub={}".format(hub))

    pass

    logger.debug("========================== Not Yet Implemented.")


def testbody_find_shade_on_hub(hub, config):
    # find_shade_on_hub(self, hubHostname, shadeId, need_room=False)
    logger.debug("testbody  ==========================  find_shade_on_hub: hub={}".format(hub))

    shade_ids = pv.shadeIds(hub)

    if shade_ids:
        shade_id = shade_ids[0]
        logger.debug("testbody  find_shade_on_hub(hubHostname={}, shadeId={}, need_room=False)".format(hub, shade_id))

        found_shade = plg.find_shade_on_hub(hub, shade_id, need_room=False)
        assert found_shade, "No shade found."
        assert found_shade["batteryStatus"], "Found shade is invalid - missing batteryStatus"
        assert found_shade["firmware"], "Found shade is invalid - missing firmware"
    logger.debug("==========================")
