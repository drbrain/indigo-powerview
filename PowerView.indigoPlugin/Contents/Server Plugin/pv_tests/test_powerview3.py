
import logging
from powerview2 import PowerView
from powerview3 import PowerViewGen3
import requests
import pytest
from .mock_powerview import MockPowerView

logger = logging.getLogger("wsgmac.com.test.powerview")
mp = MockPowerView()


@pytest.fixture()
def tpv3(monkeypatch):
    if not MockPowerView.hub_available("V2"):
        monkeypatch.setattr(PowerView, "do_get", MockPowerView.mock_get)
    if not MockPowerView.hub_available("V3"):
        monkeypatch.setattr(PowerViewGen3, "do_get", MockPowerView.mock_get)
    monkeypatch.setattr(requests, "put", MockPowerView.mock_put)
    tpv3 = PowerViewGen3({'logger': "wsgmac.com.test.powerview", 'debugPref': True})
    return tpv3


def test_1_shade_ids(tpv3: PowerViewGen3) -> None:
    logger.debug("test_1_shade_ids(tpv3: PowerViewGen3) -> None:")

    # def scenes(self, hubHostname):
    result = tpv3.shadeIds(MockPowerView.hub_host3())

    assert isinstance(result, list)
    if result:
        for shade_id in result:
            assert isinstance(shade_id, int)
    logger.debug("==========================")


def test_shade(tpv3: PowerViewGen3) -> None:
    logger.debug("test_shade(tpv3: PowerViewGen3) -> None:")

    # def shade(self, hubHostname, shadeId):

    for shadeId in tpv3.shadeIds(MockPowerView.hub_host3()):
        result = tpv3.shade(MockPowerView.hub_host3(), shadeId)

        if result:
            assert isinstance(result, dict)
            assert result['name']
            assert isinstance(result['type'], int)
    logger.debug("==========================")


def test_2_room(tpv3: PowerViewGen3) -> None:
    logger.debug("test_2_room(tpv3: PowerViewGen3) -> None:")

    # def room(self, hubHostname, roomId):

    room_list = tpv3.do_get('http://{}/home/rooms/'.format(MockPowerView.hub_host3()))
    rooms = room_list.json()

    for room in rooms:
        result = tpv3.room(MockPowerView.hub_host3(), room['id'])

        if result:
            assert isinstance(result, dict)
            assert result['name']
            assert isinstance(result['type'], int)
        else:
            pytest.fail('Room not found (id={}'.format(room['id']))

    logger.debug("==========================")


def test_3_scenes(tpv3: PowerViewGen3) -> None:
    logger.debug("test_3_scenes(tpv3: PowerViewGen3) -> None:")

    # def scenes(self, hubHostname):
    result = tpv3.scenes(MockPowerView.hub_host3())

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
        assert result[0]['name']
    logger.debug("==========================")


def test_activate_scene(tpv3: PowerViewGen3) -> None:
    logger.debug("test_activate_scene(tpv3: PowerViewGen3) -> None:")

    # def activateScene(self, hubHostname, sceneId):

    for scene in tpv3.scenes(MockPowerView.hub_host3()):
        tpv3.activateScene(MockPowerView.hub_host3(), scene['id'])
        assert MockPowerView.mock_put_called
    logger.debug("==========================")


def test_jog_shade(tpv3: PowerViewGen3) -> None:
    logger.debug("test_jog_shade(tpv3: PowerViewGen3) -> None:")

    # def jogShade(self, hubHostname, shadeId):

    for shadeId in tpv3.shadeIds(MockPowerView.hub_host3()):
        tpv3.jogShade(MockPowerView.hub_host3(), shadeId)
        assert MockPowerView.mock_put_called
    logger.debug("==========================")


def test_set_shade_position(tpv3: PowerViewGen3) -> None:
    logger.debug("test_set_shade_position(tpv3: PowerViewGen3) -> None:")

    # def setShadePosition(self, hubHostname, shadeId, positions):

    for shadeId in tpv3.shadeIds(MockPowerView.hub_host3()):
        tpv3.setShadePosition(MockPowerView.hub_host3(), shadeId, {'primary': 0, 'secondary': 0, 'tilt': 0, 'velocity': 0})
        assert MockPowerView.mock_put_called
    logger.debug("==========================")
