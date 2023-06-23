
try:
    import indigo
except ImportError:
    pass
import logging
from plugin import Plugin

logger = logging.getLogger("net.segment7.powerview")
plg = Plugin(pluginId='net.segment7.powerview', pluginDisplayName='PowerViewPluginTestV2', pluginVersion="0", pluginPrefs={})


def testbody_create_shade(hub, pv):
    logger.warning("test create_shade: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_activate_scene(hub, pv):
    logger.warning("test activate_scene: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_activate_scene_collection(hub, pv):
    logger.warning("test activate_scene_collection: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_calibrate_shade(hub, pv):
    logger.warning("test calibrate_shade: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_jog_shade(hub, pv):
    logger.warning("test jog_shade: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_stop_shade(hub, pv):
    logger.warning("test stop_shade: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_set_shade_position(hub, pv):
    logger.warning("test set_shade_position: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_current_position(hub, pv):
    logger.warning("test current_position: hub={}, pv={}".format(hub, pv))
    # def currentPosition(self, valuesDict, typeId, devId):
    values_dict = {'current': '', 'enablePri': True, 'enableSec': True, 'enableTlt': True, 'enableVel': True,
                   'lblNumbers': '', 'primary': '.9', 'secondary': '.45', 'tilt': '0', 'velocity': '0'}
    type_id = 'setShadePosition'

    dev_id = None
    for shade in indigo.devices.iter('net.segment7.powerview.PowerViewShade'):
        logger.warning("shade={}".format(shade))
        dev_id = shade.id
    if not dev_id:
        dev_id = 1  # only works when mocking the hub
    logger.warning("dev_id={}".format(dev_id))

    logger.warning("About to call currentPosition: self.pv={}, hub={}".format(pv, hub))
    values_dict2 = plg.currentPosition(values_dict, type_id, dev_id)
    logger.warning("values_dict2={}".format(values_dict2))
    # {'primary': 46, 'secondary': 25, 'tilt': 0, 'velocity': 0}
    assert values_dict2['primary'] == '46', "Invalid primary={}".format(values_dict2['primary'])
    assert values_dict2['secondary'] == '25', "Invalid secondary={}".format(values_dict2['secondary'])
    assert values_dict2['tilt'] == '0', "Invalid tilt={}".format(values_dict2['tilt'])
    assert values_dict2['velocity'] == '0', "Invalid velocity={}".format(values_dict2['velocity'])
    logger.info("==========================")


def testbody_discover_shades(hub, pv):
    logger.warning("test discover_shades: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_list_hubs(hub, pv):
    logger.warning("test list_hubs: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_list_scenes(hub, pv):
    logger.warning("test list_scenes: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_list_scene_collections(hub, pv):
    logger.warning("test list_scene_collections: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_list_shades(hub, pv):
    logger.warning("test list_shades: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_device_start_comm(hub, pv):
    logger.warning("test device_start_comm: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_device_stop_comm(hub, pv):
    logger.warning("test device_stop_comm: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_get_device_display_state_id(hub, pv):
    logger.warning("test get_device_display_state_id: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_run_concurrent_thread(hub, pv):
    logger.warning("test run_concurrent_thread: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_validate_device_config_ui(hub, pv):
    logger.warning("test validate_device_config_ui: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_validate_action_config_ui(hub, pv):
    logger.warning("test validate_action_config_ui: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_create_shade_device(hub, pv):
    logger.warning("test create_shade_device: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_find_shade_on_hub(hub, pv):
    logger.warning("test find_shade_on_hub: hub={}, pv={}".format(hub, pv))
    shade_ids = pv.shadeIds(hub)

    if shade_ids:
        shade_id = shade_ids[0]
        logger.warning("test  findShadeOnHub(hubHostname={}, shadeId={}, need_room=False)".format(hub, shade_id))

        found_shade = plg.findShadeOnHub(hub, shade_id, need_room=False)
        assert found_shade, "No shade found."
        assert found_shade["batteryStatus"], "Found shade is invalid - missing batteryStatus"
    logger.info("==========================")


def testbody_find_shade(hub, pv):
    logger.warning("test find_shade: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_update(hub, pv):
    logger.warning("test update: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")


def testbody_update_shade_later(hub, pv):
    logger.warning("test update_shade_later: hub={}, pv={}".format(hub, pv))
    # assert False, "Not Yet Implemented."
    logger.info("==========================")
