import logging

from plugin import Plugin
import pytest

logger = logging.getLogger('Plugin')
# logger = logging.getLogger('pytest.log')


@pytest.fixture()
def pv():
    return Plugin


def testbody_create_shade(pv):
    logger.error('test create_shade(pv):')
    assert False


def testbody_activate_scene(pv):
    logger.error('test activate_scene(pv):')
    assert False


def testbody_activate_scene_collection(pv):
    logger.error('test activate_scene_collection(pv):')
    assert False


def testbody_calibrate_shade(pv):
    logger.error('test calibrate_shade(pv):')
    assert False


def testbody_jog_shade(pv):
    logger.error('test jog_shade(pv):')
    assert False


def testbody_stop_shade(pv):
    logger.error('test stop_shade(pv):')
    assert False


def testbody_set_shade_position(pv):
    logger.error('test set_shade_position(pv):')
    assert False


def testbody_current_position(pv):
    logger.error('test current_position(pv):')
    # def currentPosition(self, valuesDict, typeId, devId):
    values_dict = {'current': '', 'enablePri': True, 'enableSec': True, 'enableTlt': True, 'enableVel': True, 'lblNumbers': '',
                   'primary': '.9', 'secondary': '.45', 'tilt': '0', 'velocity': '0'}
    type_id = 'setShadePosition'
    dev_id = 936067543
    values_dict2 = pv.currentPosition(values_dict, type_id, dev_id)
    pos = values_dict2['position']
    assert pos == {'primary': 0.46, 'secondary': 0.0, 'tilt': 0.0, 'velocity': 0.0}


def testbody_discover_shades(pv):
    logger.error('test discover_shades(pv):')
    assert False


def testbody_list_hubs(pv):
    logger.error('test list_hubs(pv):')
    assert False


def testbody_list_scenes(pv):
    logger.error('test list_scenes(pv):')
    assert False


def testbody_list_scene_collections(pv):
    logger.error('test list_scene_collections(pv):')
    assert False


def testbody_list_shades(pv):
    logger.error('test list_shades(pv):')
    assert False


def testbody_device_start_comm(pv):
    logger.error('test device_start_comm(pv):')
    assert False


def testbody_device_stop_comm(pv):
    logger.error('test device_stop_comm(pv):')
    assert False


def testbody_get_device_display_state_id(pv):
    logger.error('test get_device_display_state_id(pv):')
    assert False


def testbody_run_concurrent_thread(pv):
    logger.error('test run_concurrent_thread(pv):')
    assert False


def testbody_validate_device_config_ui(pv):
    logger.error('test validate_device_config_ui(pv):')
    assert False


def testbody_validate_action_config_ui(pv):
    logger.error('test validate_action_config_ui(pv):')
    assert False


def testbody_create_shade_device(pv):
    logger.error('test create_shade_device(pv):')
    assert False


def testbody_find_shade_on_hub(pv):
    logger.error('test find_shade_on_hub(pv):')
    assert False


def testbody_find_shade(pv):
    logger.error('test find_shade(pv):')
    assert False


def testbody_update(pv):
    logger.error('test update(pv):')
    assert False


def testbody_update_shade_later(pv):
    logger.error('test update_shade_later(pv):')
    assert False
