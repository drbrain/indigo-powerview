
import logging
import mock_powerview
from plugin import Plugin as pv

logger = logging.getLogger('net.segment7.powerview')


def testbody_create_shade():
    logger.warning('test create_shade(pv):')
    assert False, "Not Yet Implemented."


def testbody_activate_scene():
    logger.warning('test activate_scene(pv):')
    assert False, "Not Yet Implemented."


def testbody_activate_scene_collection():
    logger.warning('test activate_scene_collection(pv):')
    assert False, "Not Yet Implemented."


def testbody_calibrate_shade():
    logger.warning('test calibrate_shade(pv):')
    assert False, "Not Yet Implemented."


def testbody_jog_shade():
    logger.warning('test jog_shade(pv):')
    assert False, "Not Yet Implemented."


def testbody_stop_shade():
    logger.warning('test stop_shade(pv):')
    assert False, "Not Yet Implemented."


def testbody_set_shade_position():
    logger.warning('test set_shade_position(pv):')
    assert False, "Not Yet Implemented."


def testbody_current_position():
    logger.warning('test current_position(pv):')
    # def currentPosition(self, valuesDict, typeId, devId):
    values_dict = {'current': '', 'enablePri': True, 'enableSec': True, 'enableTlt': True, 'enableVel': True, 'lblNumbers': '',
                   'primary': '.9', 'secondary': '.45', 'tilt': '0', 'velocity': '0'}
    type_id = 'setShadePosition'
    shade_ids = pv.shadeIds(get_hub_address())

    if shade_ids:
        dev_id = shade_ids[0]
        values_dict2 = pv.currentPosition(values_dict, type_id, dev_id)
        pos = values_dict2['position']
        assert pos == {'primary': 0.46, 'secondary': 0.0, 'tilt': 0.0, 'velocity': 0.0}
    else:
        assert False, "No device defined in Indigo for any shades."


def testbody_discover_shades():
    logger.warning('test discover_shades(pv):')
    assert False, "Not Yet Implemented."


def testbody_list_hubs():
    logger.warning('test list_hubs(pv):')
    assert False, "Not Yet Implemented."


def testbody_list_scenes():
    logger.warning('test list_scenes(pv):')
    assert False, "Not Yet Implemented."


def testbody_list_scene_collections():
    logger.warning('test list_scene_collections(pv):')
    assert False, "Not Yet Implemented."


def testbody_list_shades():
    logger.warning('test list_shades(pv):')
    assert False, "Not Yet Implemented."


def testbody_device_start_comm():
    logger.warning('test device_start_comm(pv):')
    assert False, "Not Yet Implemented."


def testbody_device_stop_comm():
    logger.warning('test device_stop_comm(pv):')
    assert False, "Not Yet Implemented."


def testbody_get_device_display_state_id():
    logger.warning('test get_device_display_state_id(pv):')
    assert False, "Not Yet Implemented."


def testbody_run_concurrent_thread():
    logger.warning('test run_concurrent_thread(pv):')
    assert False, "Not Yet Implemented."


def testbody_validate_device_config_ui():
    logger.warning('test validate_device_config_ui(pv):')
    assert False, "Not Yet Implemented."


def testbody_validate_action_config_ui():
    logger.warning('test validate_action_config_ui(pv):')
    assert False, "Not Yet Implemented."


def testbody_create_shade_device():
    logger.warning('test create_shade_device(pv):')
    assert False, "Not Yet Implemented."


def testbody_find_shade_on_hub():
    logger.warning('test find_shade_on_hub(pv):')
    pv.find_shade_on_hub()
    assert False, "Not Yet Implemented."


def testbody_find_shade():
    logger.warning('test find_shade(pv):')
    assert False, "Not Yet Implemented."


def testbody_update():
    logger.warning('test update(pv):')
    assert False, "Not Yet Implemented."


def testbody_update_shade_later():
    logger.warning('test update_shade_later(pv):')
    assert False, "Not Yet Implemented."

def get_hub_address(pv):
    if pv.GENERATION == "V3":
        return mock_powerview.host3()
    else:
        return mock_powerview.host2()
