
import logging
from .mock_powerview import MockPowerView
from powerview2 import PowerView
from powerview3 import PowerViewGen3
import pytest
import requests

logger = logging.getLogger("wsgmac.com.test.powerview")
mp = MockPowerView()


@pytest.fixture()
def tpv2(monkeypatch):

    if not MockPowerView.hub_available("V2"):
        monkeypatch.setattr(PowerView, "do_get", MockPowerView.mock_get)
    if not MockPowerView.hub_available("V3"):
        monkeypatch.setattr(PowerViewGen3, "do_get", MockPowerView.mock_get)
    monkeypatch.setattr(requests, "put", MockPowerView.mock_put)
    tpv2 = PowerView({'logger': logger})
    return tpv2


def test_1_shade_ids(tpv2: PowerView) -> None:
    logger.debug("test_1_shade_ids(tpv2: PowerView) -> None:")

    # def scenes(self, hubHostname):
    result = tpv2.shadeIds(MockPowerView.hub_host2())

    assert isinstance(result, list)
    if result:
        for shade_id in result:
            assert isinstance(shade_id, int)
    else:
        pytest.fail('Shade IDs not returned in a non-empty list.')
    logger.debug("==========================")


def test_shade(tpv2: PowerView) -> None:
    logger.debug("test_shade(tpv2: PowerView) -> None:")

    # def shade(self, hubHostname, shadeId):

    for shadeId in tpv2.shadeIds(MockPowerView.hub_host2()):
        result = tpv2.shade(MockPowerView.hub_host2(), shadeId)

        if result:
            assert isinstance(result, dict), "Bad result from PowerView.shade"
            assert result['name'], "Bad result from PowerView.shade"
            assert isinstance(result['type'], int), "Bad result from PowerView.shade"
            assert result['positions'], f"Position data missing from shade {result['name']}"
            assert result['positions']['primary'] in range(101), f"Invalid primary position = {result['positions']['primary']}"
            assert result['positions']['secondary'] in range(101), f"Invalid secondary position = {result['positions']['secondary']}"
            assert result['positions']['tilt'] in range(101), f"Invalid tilt position = {result['positions']['tilt']}"
            assert result['positions']['velocity'] in range(101), f"Invalid velocity position = {result['positions']['velocity']}"
            assert result['capabilities'] in range(12)
    logger.debug("==========================")


def test_2_room(tpv2: PowerView) -> None:
    logger.debug("test_2_room(tpv2: PowerView) -> None:")

    # def room(self, hubHostname, roomId):

    room_response = tpv2.do_get('http://{}/api/rooms/'.format(MockPowerView.hub_host2()))
    room_ids = (room_response.json())['roomIds']

    for room_id in room_ids:
        room = tpv2.room(MockPowerView.hub_host2(), room_id)

        if room:
            assert isinstance(room, dict)
            assert room['name']
        else:
            pytest.fail('Room not found (id={}'.format(room['id']))
    logger.debug("==========================")


def test_3_scenes(tpv2: PowerView) -> None:
    logger.debug("test_3_scenes(tpv2: PowerView) -> None:")

    # def scenes(self, hubHostname):
    result = tpv2.scenes(MockPowerView.hub_host2())

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
        assert result[0]['name']
    logger.debug("==========================")


def test_4_scene_collections(tpv2: PowerView) -> None:
    logger.debug("test_4_scene_collections(tpv2: PowerView) -> None:")

    # def sceneCollections(self, hubHostname):
    result = tpv2.sceneCollections(MockPowerView.hub_host2())

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
        assert result[0]['name']
    logger.debug("==========================")


def test_activate_scene(tpv2: PowerView) -> None:
    logger.debug("test_activate_scene(tpv2: PowerView) -> None:")

    # def activateScene(self, hubHostname, sceneId):

    for scene in tpv2.scenes(MockPowerView.hub_host2()):
        logger.debug("activate_scene({})".format(scene.get('name')))
        tpv2.activateScene(MockPowerView.hub_host2(), scene['id'])
    logger.debug("==========================")


def test_activate_scene_collection(tpv2: PowerView) -> None:
    logger.debug("test_activate_scene_collection(tpv2: PowerView) -> None:")

    # def activateSceneCollection(self, hubHostname, sceneCollectionId):

    for scene in tpv2.sceneCollections(MockPowerView.hub_host2()):
        logger.debug("activateSceneCollection({})".format(scene.get('name')))
        tpv2.activateSceneCollection(MockPowerView.hub_host2(), scene['id'])
    logger.debug("==========================")


def test_jog_shade(tpv2: PowerView) -> None:
    logger.debug("test_jog_shade(tpv2: PowerView) -> None:")

    # def jogShade(self, hubHostname, shadeId):

    for shadeId in tpv2.shadeIds(MockPowerView.hub_host2()):
        tpv2.jogShade(MockPowerView.hub_host2(), shadeId)
        assert MockPowerView.mock_put_called
    logger.debug("==========================")


def test_set_shade_position(tpv2: PowerView) -> None:
    logger.debug("test_set_shade_position(tpv2: PowerView) -> None:")

    # def setShadePosition(self, hubHostname, shadeId, top, bottom):

    for shadeId in tpv2.shadeIds(MockPowerView.hub_host2()):
        tpv2.setShadePosition(MockPowerView.hub_host2(), shadeId, {'primary': 0, 'secondary': 0, 'tilt': 0, 'velocity': 0})
        assert MockPowerView.mock_put_called
    logger.debug("==========================")


def test_to_percent(tpv2: PowerView) -> None:
    logger.debug("test_to_percent(tpv2: PowerView) -> None:")

    # def test_to_percent(pos, divr=1.0):

    assert 0 == tpv2.to_percent(0), "to_percent(0) failed"
    assert 1 == tpv2.to_percent(655), "to_percent(655) failed"
    assert 10 == tpv2.to_percent(6554), "to_percent(6554) failed"
    assert 50 == tpv2.to_percent(32768), "to_percent(32768) failed"
    assert 90 == tpv2.to_percent(58982), "to_percent(58982) failed"
    assert 99 == tpv2.to_percent(64880), "to_percent(64880) failed"
    assert 100 == tpv2.to_percent(65535), "to_percent(65535) failed"
    assert 200 == tpv2.to_percent(131070), "to_percent(131070) failed"
    logger.debug("==========================")


def test_fm_percent(tpv2: PowerView) -> None:
    logger.debug("test_fm_percent(tpv2: PowerView) -> None:")

    # def test_fm_percent(pos, divr=1.0):

    assert 0 == tpv2.fm_percent(0), "fm_percent(0) failed"
    assert 655 == tpv2.fm_percent(1), "fm_percent(1) failed"
    assert 6554 == tpv2.fm_percent(10), "fm_percent(10) failed"
    assert 32768 == tpv2.fm_percent(50), "fm_percent(50) failed"
    assert 58982 == tpv2.fm_percent(90), "fm_percent(90) failed"
    assert 64880 == tpv2.fm_percent(99), "fm_percent(99) failed"
    assert 65535 == tpv2.fm_percent(100), "fm_percent(100) failed"
    assert 131070 == tpv2.fm_percent(200), "fm_percent(200) failed"
    logger.debug("==========================")
