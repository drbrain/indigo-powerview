
import logging
from powerview2 import PowerView
from powerview3 import PowerViewGen3
import pytest
import requests
from pv_tests import mock_powerview as mp
from pv_tests import plugin_body as pb

logger = logging.getLogger('net.segment7.powerview')


@pytest.fixture()
def tpv2(monkeypatch):
    if '127.0.0.1' == mp.host2():
        monkeypatch.setattr(requests, "get", mp.mock_get2)
    monkeypatch.setattr(requests, "put", mp.mock_put)
    tpv2 = PowerView()
    return tpv2


@pytest.fixture()
def tpv3(monkeypatch):
    if '127.0.0.1' == mp.host3():
        monkeypatch.setattr(requests, "get", mp.mock_get3)
    monkeypatch.setattr(requests, "put", mp.mock_put)
    tpv3 = PowerViewGen3(TestLogger())
    return tpv3


class TestLogger:

    @staticmethod
    def error(log_msg):
        logger.error(log_msg)

    @staticmethod
    def exception(log_msg):
        logger.exception(log_msg)

    @staticmethod
    def debug(log_msg):
        logger.debug(log_msg)


@pytest.mark.parametrize("tpv", [tpv3, tpv2])
class TestPlugin:

    def test_create_shade(self, tpv):
        pb.testbody_create_shade(tpv)

    def test_activate_scene(self, tpv):
        pb.testbody_activate_scene(tpv)

    def test_activate_scene_collection(self, tpv):
        pb.testbody_activate_scene_collection(tpv)

    def test_calibrate_shade(self, tpv):
        pb.testbody_calibrate_shade(tpv)

    def test_jog_shade(self, tpv):
        pb.testbody_jog_shade(tpv)

    def test_stop_shade(self, tpv):
        pb.testbody_stop_shade(tpv)

    def test_set_shade_position(self, tpv):
        pb.testbody_set_shade_position(tpv)

    def test_current_position(self, tpv):
        # def currentPosition(self, valuesDict, typeId, devId, tpv):
        pb.testbody_current_position(tpv)

    def test_discover_shades(self, tpv):
        pb.testbody_discover_shades(tpv)

    def test_list_hubs(self, tpv):
        pb.testbody_list_hubs(tpv)

    def test_list_scenes(self, tpv):
        pb.testbody_list_scenes(tpv)

    def test_list_scene_collections(self, tpv):
        pb.testbody_list_scene_collections(tpv)

    def test_list_shades(self, tpv):
        pb.testbody_list_shades(tpv)

    def test_device_start_comm(self, tpv):
        pb.testbody_device_start_comm(tpv)

    def test_device_stop_comm(self, tpv):
        pb.testbody_device_stop_comm(tpv)

    def test_get_device_display_state_id(self, tpv):
        pb.testbody_get_device_display_state_id(tpv)

    def test_run_concurrent_thread(self, tpv):
        pb.testbody_run_concurrent_thread(tpv)

    def test_validate_device_config_ui(self, tpv):
        pb.testbody_validate_device_config_ui(tpv)

    def test_validate_action_config_ui(self, tpv):
        pb.testbody_validate_action_config_ui(tpv)

    def test_create_shade_device(self, tpv):
        pb.testbody_create_shade_device(tpv)

    def test_find_shade_on_hub(self, tpv):
        pb.testbody_find_shade_on_hub(tpv)

    def test_find_shade(self, tpv):
        pb.testbody_find_shade(tpv)

    def test_update(self, tpv):
        pb.testbody_update(tpv)

    def test_update_shade_later(self, tpv):
        pb.testbody_update_shade_later(tpv)


# class TestPlugin2:
#
#     def test_create_shade(self, tpv2):
#         pb.testbody_create_shade(tpv2)
#
#     def test_activate_scene(self, tpv2):
#         pb.testbody_activate_scene(tpv2)
#
#     def test_activate_scene_collection(self, tpv2):
#         pb.testbody_activate_scene_collection(tpv2)
#
#     def test_calibrate_shade(self, tpv2):
#         pb.testbody_calibrate_shade(tpv2)
#
#     def test_jog_shade(self, tpv2):
#         pb.testbody_jog_shade(tpv2)
#
#     def test_stop_shade(self, tpv2):
#         pb.testbody_stop_shade(tpv2)
#
#     def test_set_shade_position(self, tpv2):
#         pb.testbody_set_shade_position(tpv2)
#
#     def test_current_position(self, tpv2):
#         pb.testbody_current_position(tpv2)
#
#     def test_discover_shades(self, tpv2):
#         pb.testbody_discover_shades(tpv2)
#
#     def test_list_hubs(self, tpv2):
#         pb.testbody_list_hubs(tpv2)
#
#     def test_list_scenes(self, tpv2):
#         pb.testbody_list_scenes(tpv2)
#
#     def test_list_scene_collections(self, tpv2):
#         pb.testbody_list_scene_collections(tpv2)
#
#     def test_list_shades(self, tpv2):
#         pb.testbody_list_shades(tpv2)
#
#     def test_device_start_comm(self, tpv2):
#         pb.testbody_device_start_comm(tpv2)
#
#     def test_device_stop_comm(self, tpv2):
#         pb.testbody_device_stop_comm(tpv2)
#
#     def test_get_device_display_state_id(self, tpv2):
#         pb.testbody_get_device_display_state_id(tpv2)
#
#     def test_run_concurrent_thread(self, tpv2):
#         pb.testbody_run_concurrent_thread(tpv2)
#
#     def test_validate_device_config_ui(self, tpv2):
#         pb.testbody_validate_device_config_ui(tpv2)
#
#     def test_validate_action_config_ui(self, tpv2):
#         pb.testbody_validate_action_config_ui(tpv2)
#
#     def test_create_shade_device(self, tpv2):
#         pb.testbody_create_shade_device(tpv2)
#
#     def test_find_shade_on_hub(self, tpv2):
#         pb.testbody_find_shade_on_hub(tpv2)
#
#     def test_find_shade(self, tpv2):
#         pb.testbody_find_shade(tpv2)
#
#     def test_update(self, tpv2):
#         pb.testbody_update(tpv2)
#
#     def test_update_shade_later(self, tpv2):
#         pb.testbody_update_shade_later(tpv2)
