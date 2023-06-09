
import logging
from powerview2 import PowerView
import pytest
import requests

logger = logging.getLogger('net.segment7.powerview')


@pytest.fixture()
def tpv2(monkeypatch):
    if '127.0.0.1' == mp.host2():
        monkeypatch.setattr(requests, "get", mp.mock_get2)
    monkeypatch.setattr(requests, "put", mp.mock_put)
    tpv2 = PowerView()
    return tpv2


def test_1_shade_ids(tpv2: PowerView) -> None:
    # def scenes(self, hubHostname):
    result = tpv2.shadeIds(mp.host2())

    assert isinstance(result, list)
    if result:
        for shade_id in result:
            assert isinstance(shade_id, int)
    else:
        pytest.fail('Shade IDs not returned in a non-empty list.')


def test_shade(tpv2: PowerView) -> None:
    # def shade(self, hubHostname, shadeId):

    for shadeId in tpv2.shadeIds(mp.host2()):
        result = tpv2.shade(mp.host2(), shadeId)

        if result:
            assert isinstance(result, dict)
            assert result['name']
            assert isinstance(result['type'], int)
            shade_type = result['type']
            assert shade_type in range(11)


def test_2_room(tpv2: PowerView) -> None:
    # def room(self, hubHostname, roomId):

    room_response = requests.get('http://{}/api/rooms/'.format(mp.host2()))
    room_ids = (room_response.json())['roomIds']

    for room_id in room_ids:
        room = tpv2.room(mp.host2(), room_id)

        if room:
            assert isinstance(room, dict)
            assert room['name']
        else:
            pytest.fail('Room not found (id={}'.format(room['id']))


def test_3_scenes(tpv2: PowerView) -> None:
    # def scenes(self, hubHostname):
    result = tpv2.scenes(mp.host2())

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
        assert result[0]['name']


def test_4_scene_collections(tpv2: PowerView) -> None:
    # def sceneCollections(self, hubHostname):
    result = tpv2.sceneCollections(mp.host2())

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
        assert result[0]['name']


def test_activate_scene(tpv2: PowerView) -> None:
    # def activateScene(self, hubHostname, sceneId):

    for scene in tpv2.scenes(mp.host2()):
        tpv2.activateScene(mp.host2(), scene['id'])
        assert mp.mock_get_called


def test_activate_scene_collection(tpv2: PowerView) -> None:
    # def activateSceneCollection(self, hubHostname, sceneCollectionId):

    for scene in tpv2.sceneCollections(mp.host2()):
        tpv2.activateSceneCollection(mp.host2(), scene['id'])
        assert mp.mock_get_called


def test_jog_shade(tpv2: PowerView) -> None:
    # def jogShade(self, hubHostname, shadeId):

    for shadeId in tpv2.shadeIds(mp.host2()):
        tpv2.jogShade(mp.host2(), shadeId)
        assert mp.mock_put_called


def test_set_shade_position(tpv2: PowerView) -> None:
    # def setShadePosition(self, hubHostname, shadeId, top, bottom):

    for shadeId in tpv2.shadeIds(mp.host2()):
        tpv2.setShadePosition(mp.host2(), shadeId, 0, 0)
        assert mp.mock_put_called
