
import logging
from plugin import Plugin
from powerview2 import PowerView
from powerview3 import PowerViewGen3
# import pydevd_pycharm
import pytest
import requests
from .mock_powerview import MockPowerView
from pv_tests import plugin_body as pb
try:
    import indigo
except ImportError:
    pass

logger = logging.getLogger("wsgmac.com.test.powerview")


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    if not MockPowerView.hub_available("V2"):
        monkeypatch.setattr(PowerView, "do_get", MockPowerView.mock_do_get)
        monkeypatch.setattr(indigo, "devices", MockPowerView.DevicesMock())

    if not MockPowerView.hub_available("V3"):
        monkeypatch.setattr(PowerViewGen3, "do_get", MockPowerView.mock_get)
        monkeypatch.setattr(indigo, "devices", MockPowerView.DevicesMock())
    monkeypatch.setattr(requests, "put", MockPowerView.mock_put)
    monkeypatch.setattr(indigo.Device, "replacePluginPropsOnServer", MockPowerView.DevicesMock.MockedDevice.replacePluginPropsOnServer)
    monkeypatch.setattr(Plugin, "create_shade_device", MockPowerView.DevicesMock.create)


class TestPluginV2:

    COMPARE_DATA = {
        'ACTIVATE-S': {}, # Get url cannot be matched
        'ACTIVATE-C': {}, # Get url cannot be matched
        'CALIBRATE': {'url': 'http://{hub_address}/api/shades/{id}', 'compare_put_send': {'shade': {'motion': 'calibrate'}}},
        'JOG': {'url': 'http://{hub_address}/api/shades/{id}', 'compare_put_send': {'shade': {'motion': 'jog'}}},
        'STOP':{}, # Not supported on Gen2
        'SET_POSITION': {'url': 'http://{hub_address}/api/shades/{id}',
                         'compare_put_send': {'shade': {'positions': {'position1': 6554, 'posKind1': 1,'position2': 13107, 'posKind2': 2}}}}
    }

    def __init__(self):
        # pydevd_pycharm.settrace('192.168.0.200', port=5678, stdoutToServer=True, stderrToServer=True, suspend=False)
        pv = None

    @pytest.fixture(scope="function", autouse=True)
    def set_vals(self):
        self.hub_address = MockPowerView.hub_host2()
        if not self.pv:
            self.pv = PowerView({'logger': logger})
            pb.gplg(self.pv, 'V2')

    def test_create_shade(self, setup):
        pb.testbody_create_shade(self.hub_address, self.COMPARE_DATA)

    def test_activate_scene(self, setup):
        pb.testbody_activate_scene(self.hub_address, self.COMPARE_DATA['ACTIVATE-S'])

    def test_activate_scene_collection(self, setup):
        pb.testbody_activate_scene_collection(self.hub_address, self.COMPARE_DATA['ACTIVATE-C'])

    def test_calibrate_shade(self, setup):
        pb.testbody_calibrate_shade(self.hub_address, self.COMPARE_DATA['CALIBRATE'])

    def test_jog_shade(self, setup):
        pb.testbody_jog_shade(self.hub_address, self.COMPARE_DATA['JOG'])

    def test_stop_shade(self, setup):
        pb.testbody_stop_shade(self.hub_address, self.COMPARE_DATA['STOP'])

    def test_set_shade_position(self, setup):
        pb.testbody_set_shade_position(self.hub_address, self.COMPARE_DATA['SET_POSITION'], gen2=True)

    def test_current_position(self, setup):
        # def getCurrentPosition(self, valuesDict, typeId, devId):
        pb.testbody_current_position(self.hub_address, self.COMPARE_DATA)

    def test_discover_shades(self, setup):
        pb.testbody_discover_shades(self.hub_address, self.COMPARE_DATA)

    def test_list_hubs(self, setup):
        pb.testbody_list_hubs(self.hub_address, self.COMPARE_DATA)

    def test_list_scenes(self, setup):
        pb.testbody_list_scenes(self.hub_address, self.COMPARE_DATA)

    def test_list_scene_collections(self, setup):
        pb.testbody_list_scene_collections(self.hub_address, self.COMPARE_DATA)

    def test_list_shades(self, setup):
        pb.testbody_list_shades(self.hub_address, self.COMPARE_DATA)

    def test_device_start_comm(self, setup):
        pb.testbody_device_start_comm(self.hub_address, self.COMPARE_DATA)

    def test_device_stop_comm(self, setup):
        pb.testbody_device_stop_comm(self.hub_address, self.COMPARE_DATA)

    def test_validate_device_config_ui(self, setup):
        pb.testbody_validate_device_config_ui(self.hub_address, self.COMPARE_DATA)

    def test_validate_action_config_ui(self, setup):
        pb.testbody_validate_action_config_ui(self.hub_address, self.COMPARE_DATA)

    def test_find_shade_on_hub(self, setup):
        pb.testbody_find_shade_on_hub(self.hub_address, self.COMPARE_DATA)
