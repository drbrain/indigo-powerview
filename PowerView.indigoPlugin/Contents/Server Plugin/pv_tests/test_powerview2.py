
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
    tpv2 = PowerView({'logger': "wsgmac.com.test.powerview"})
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
            assert isinstance(result, dict)
            assert result['name']
            assert isinstance(result['type'], int)
            shade_type = result['type']
            assert shade_type in range(11)
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
