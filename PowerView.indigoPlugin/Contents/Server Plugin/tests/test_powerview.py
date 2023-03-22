
import logging
import os
from powerview import PowerView
import requests
import pytest

mock_put_called = False


def mock_put(*args, **kwargs):
    global mock_put_called
    mock_put_called = True
    return MockResponse()


@pytest.fixture(scope='session')
def host():
    host = os.getenv('POWERVIEW_GATEWAY_IP', default=None)
    if host is None:
        raise AttributeError('Define an Environment Variable: POWERVIEW_GATEWAY_IP=<host IP or hostname>')
    return host


@pytest.fixture()
def tpv(monkeypatch):
    monkeypatch.setattr(requests, "put", mock_put)
    tpv = PowerView()
    return tpv


def test_1_shadeIds(tpv, host):
    # def scenes(self, hubHostname):
    result = tpv.shadeIds(host)

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], int)


def test_shade(tpv, host):
    # def shade(self, hubHostname, shadeId):

    for shadeId in tpv.shadeIds(host):
        result = tpv.shade(host, shadeId)

        if result:
            assert isinstance(result, dict)
            assert result['name']
            assert isinstance(result['type'], int)


def test_2_room(tpv, host):
    # def room(self, hubHostname, roomId):

    room_response = requests.get('http://{}/api/rooms'.format(host))
    room_ids = (room_response.json())['roomIds']

    for room_id in room_ids:
        room = tpv.room(host, room_id)

        if room:
            assert isinstance(room, dict)
            assert room['name']
            assert isinstance(room['type'], int)
        else:
            pytest.fail('Room not found (id={}'.format(room['id']))


def test_3_scenes(tpv, host):
    # def scenes(self, hubHostname):
    result = tpv.scenes(host)

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
        assert result[0]['name']


def test_4_sceneCollections(tpv, host):
    # def sceneCollections(self, hubHostname):
    result = tpv.sceneCollections(host)

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
        assert result[0]['name']


def test_activate_scene(tpv, host):
    global mock_put_called
    # def activateScene(self, hubHostname, sceneId):

    for scene in tpv.scenes(host):
        tpv.activateScene(host, scene['id'])
        assert mock_put_called
        mock_put_called = False


def test_activateSceneCollection(tpv, host):
    global mock_put_called
    # def activateSceneCollection(self, hubHostname, sceneCollectionId):

    for scene in tpv.sceneCollections(host):
        tpv.activateSceneCollection(host, scene['id'])
        assert mock_put_called
        mock_put_called = False


def test_jog_shade(tpv, host):
    global mock_put_called
    # def jogShade(self, hubHostname, shadeId):

    for shadeId in tpv.shadeIds(host):
        tpv.jogShade(host, shadeId)
        assert mock_put_called
        mock_put_called = False


def test_set_shade_position(tpv, host):
    global mock_put_called
    # def setShadePosition(self, hubHostname, shadeId, positions):

    for shadeId in tpv.shadeIds(host):
        tpv.setShadePosition(host, shadeId, {'primary':0, 'secondary':0, 'tilt':0, 'velocity':0})
        assert mock_put_called
        mock_put_called = False


# custom class to be the mocked return value that
# will override the requests.Response object returned from requests.put
class MockResponse:
    # mock status code is always 200 Success
    status_code = requests.codes.ok

    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {"mock_key": "static response json for put() from MockResponse class"}
