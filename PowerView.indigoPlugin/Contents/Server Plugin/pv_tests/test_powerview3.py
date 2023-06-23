
from powerview3 import PowerViewGen3
import logging
import requests
import pytest
from pv_tests import mock_powerview as mp

logger = logging.getLogger("net.segment7.powerview")


@pytest.fixture()
def tpv3(monkeypatch):
    if not mp.hub_available("V3"):
        monkeypatch.setattr(requests, "get", mp.mock_get)
    monkeypatch.setattr(requests, "put", mp.mock_put)
    tpv3 = PowerViewGen3()
    return tpv3


def test_1_shade_ids(tpv3: PowerViewGen3) -> None:
    logger.info("test_1_shade_ids(tpv3: PowerViewGen3) -> None:")

    # def scenes(self, hubHostname):
    result = tpv3.shadeIds(mp.hub_host3())

    assert isinstance(result, list)
    if result:
        for shade_id in result:
            assert isinstance(shade_id, int)
    logger.info("==========================")


def test_shade(tpv3: PowerViewGen3) -> None:
    logger.info("test_shade(tpv3: PowerViewGen3) -> None:")

    # def shade(self, hubHostname, shadeId):

    for shadeId in tpv3.shadeIds(mp.hub_host3()):
        result = tpv3.shade(mp.hub_host3(), shadeId)

        if result:
            assert isinstance(result, dict)
            assert result['name']
            assert isinstance(result['type'], int)
    logger.info("==========================")


def test_2_room(tpv3: PowerViewGen3) -> None:
    logger.info("test_2_room(tpv3: PowerViewGen3) -> None:")

    # def room(self, hubHostname, roomId):

    room_list = requests.get('http://{}/home/rooms/'.format(mp.hub_host3()))
    rooms = room_list.json()

    for room in rooms:
        result = tpv3.room(mp.hub_host3(), room['id'])

        if result:
            assert isinstance(result, dict)
            assert result['name']
            assert isinstance(result['type'], int)
        else:
            pytest.fail('Room not found (id={}'.format(room['id']))
    logger.info("==========================")


def test_3_scenes(tpv3: PowerViewGen3) -> None:
    logger.info("test_3_scenes(tpv3: PowerViewGen3) -> None:")

    # def scenes(self, hubHostname):
    result = tpv3.scenes(mp.hub_host3())

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
        assert result[0]['name']
    logger.info("==========================")


def test_activate_scene(tpv3: PowerViewGen3) -> None:
    logger.info("test_activate_scene(tpv3: PowerViewGen3) -> None:")

    # def activateScene(self, hubHostname, sceneId):

    for scene in tpv3.scenes(mp.hub_host3()):
        tpv3.activateScene(mp.hub_host3(), scene['id'])
        assert mp.mock_put_called
    logger.info("==========================")


def test_jog_shade(tpv3: PowerViewGen3) -> None:
    logger.info("test_jog_shade(tpv3: PowerViewGen3) -> None:")

    # def jogShade(self, hubHostname, shadeId):

    for shadeId in tpv3.shadeIds(mp.hub_host3()):
        tpv3.jogShade(mp.hub_host3(), shadeId)
        assert mp.mock_put_called
    logger.info("==========================")


def test_set_shade_position(tpv3: PowerViewGen3) -> None:
    logger.info("test_set_shade_position(tpv3: PowerViewGen3) -> None:")

    # def setShadePosition(self, hubHostname, shadeId, positions):

    for shadeId in tpv3.shadeIds(mp.hub_host3()):
        tpv3.setShadePosition(mp.hub_host3(), shadeId, {'primary': 0, 'secondary': 0, 'tilt': 0, 'velocity': 0})
        assert mp.mock_put_called
    logger.info("==========================")
