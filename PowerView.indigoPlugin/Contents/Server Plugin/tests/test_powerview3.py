import logging
import os
from powerview3 import PowerViewGen3
import requests
import pytest


@pytest.fixture
def host():
    host = os.getenv('POWERVIEW_GATEWAY_IP', default=None)
    if host is None:
        raise AttributeError('Define an Environment Variable: POWERVIEW_GATEWAY_IP=<host IP or hostname>')
    return host


@pytest.fixture(scope='session')
def tpv3():
    tpv3 = PowerViewGen3(TestLogger())
    return tpv3


def test_1_shades(tpv3, host):
    # def scenes(self, hubHostname):
    result = tpv3.shades(host)

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
        assert result[0]['name']


def test_2_room(tpv3, host):
    # def room(self, hubHostname, roomId):

    room_list = requests.get('http://{}/home/rooms'.format(host))
    rooms = room_list.json()

    for room in rooms:
        result = tpv3.room(host, room['id'])

        if result:
            assert isinstance(result, dict)
            assert result['name']
            assert isinstance(result['type'], int)
        else:
            fail('Room not found (id={}'.format(room['id']))


def test_3_scenes(tpv3, host):
    # def shades(self, hubHostname):
    result = tpv3.scenes(host)

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
        assert result[0]['name']


def test_activate_scene(tpv3, host):
    # def activateScene(self, hubHostname, sceneId):

    for scene in tpv3.scenes(host):
        result = tpv3.activateScene(host, scene['id'])

        if result:
            assert isinstance(result, list)
            assert result


def test_jog_shade(tpv3, host):
    # def jogShade(self, hubHostname, shadeId):

    for shade in tpv3.shades(host):
        result = tpv3.jogShade(host, shade['id'])

        if result:
            assert isinstance(result, dict)
            assert result['err']


def test_set_shade_position(tpv3, host):
    # def setShadePosition(self, hubHostname, shadeId, top, bottom):

    for shade in tpv3.shades(host):
        result = tpv3.setShadePosition(host, shade['id'], shade['positions']['secondary'], shade['positions']['primary'])

        if result:
            assert isinstance(result, dict)
            assert result['err']


def test_shade(tpv3, host):
    # def shade(self, hubHostname, shadeId):

    for shade in tpv3.shades(host):
        result = tpv3.shade(host, shade['id'])

        if result:
            assert isinstance(result, dict)
            assert result['name']
            assert isinstance(result['type'], int)


# def activateSceneCollection(self, hubHostname, sceneCollectionId):
# def sceneCollections(self, hubHostname):


class TestLogger:

    def error(self, log_msg):
        logging.getLogger().error(log_msg)
