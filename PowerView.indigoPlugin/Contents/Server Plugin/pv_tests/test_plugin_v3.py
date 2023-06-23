
import logging
from powerview3 import PowerViewGen3
import pytest
import requests
from pv_tests import mock_powerview as mp
from pv_tests import plugin_body as pb
try:
    import indigo
except ImportError:
    pass

logger = logging.getLogger("net.segment7.powerview")


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


@pytest.fixture()
def setup(monkeypatch):
    # if not mp.hub_available("V3"):
    monkeypatch.setattr(requests, "get", mp.mock_get)
    monkeypatch.setattr(requests, "put", mp.mock_put)
    monkeypatch.setattr(indigo, "devices", mp.mock_devices())


class TestPluginV3:
    @pytest.fixture(scope="function", autouse=True)
    def set_vals(self):
        self.hub_address = mp.hub_host3()
        self.pv = PowerViewGen3()

    def test_create_shade(self, setup):
        pb.testbody_create_shade(self.hub_address, self.pv)

    def test_activate_scene(self, setup):
        pb.testbody_activate_scene(self.hub_address, self.pv)

    def test_activate_scene_collection(self, setup):
        pb.testbody_activate_scene_collection(self.hub_address, self.pv)

    def test_calibrate_shade(self, setup):
        pb.testbody_calibrate_shade(self.hub_address, self.pv)

    def test_jog_shade(self, setup):
        pb.testbody_jog_shade(self.hub_address, self.pv)

    def test_stop_shade(self, setup):
        pb.testbody_stop_shade(self.hub_address, self.pv)

    def test_set_shade_position(self, setup):
        pb.testbody_set_shade_position(self.hub_address, self.pv)

    def test_current_position(self, setup):
        pb.testbody_current_position(self.hub_address, self.pv)

    def test_discover_shades(self, setup):
        pb.testbody_discover_shades(self.hub_address, self.pv)

    def test_list_hubs(self, setup):
        pb.testbody_list_hubs(self.hub_address, self.pv)

    def test_list_scenes(self, setup):
        pb.testbody_list_scenes(self.hub_address, self.pv)

    def test_list_scene_collections(self, setup):
        pb.testbody_list_scene_collections(self.hub_address, self.pv)

    def test_list_shades(self, setup):
        pb.testbody_list_shades(self.hub_address, self.pv)

    def test_device_start_comm(self, setup):
        pb.testbody_device_start_comm(self.hub_address, self.pv)

    def test_device_stop_comm(self, setup):
        pb.testbody_device_stop_comm(self.hub_address, self.pv)

    def test_get_device_display_state_id(self, setup):
        pb.testbody_get_device_display_state_id(self.hub_address, self.pv)

    def test_run_concurrent_thread(self, setup):
        pb.testbody_run_concurrent_thread(self.hub_address, self.pv)

    def test_validate_device_config_ui(self, setup):
        pb.testbody_validate_device_config_ui(self.hub_address, self.pv)

    def test_validate_action_config_ui(self, setup):
        pb.testbody_validate_action_config_ui(self.hub_address, self.pv)

    def test_create_shade_device(self, setup):
        pb.testbody_create_shade_device(self.hub_address, self.pv)

    def test_find_shade_on_hub(self, setup):
        pb.testbody_find_shade_on_hub(self.hub_address, self.pv)

    def test_find_shade(self, setup):
        pb.testbody_find_shade(self.hub_address, self.pv)

    def test_update(self, setup):
        pb.testbody_update(self.hub_address, self.pv)

    def test_update_shade_later(self, setup):
        pb.testbody_update_shade_later(self.hub_address, self.pv)
