
from powerview3 import PowerViewGen3
import logging
import requests
import pytest
from pv_tests import mock_powerview as mp


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
        logging.getLogger().error(log_msg)

    @staticmethod
    def exception(log_msg):
        logging.getLogger().error(log_msg)

    @staticmethod
    def debug(log_msg):
        logging.getLogger().debug(log_msg)


def test_1_shade_ids(tpv3):
    # def scenes(self, hubHostname):
    result = tpv3.shadeIds(mp.host3())

    assert isinstance(result, list)
    if result:
        for shade_id in result:
            assert isinstance(shade_id, int)


def test_shade(tpv3):
    # def shade(self, hubHostname, shadeId):

    for shadeId in tpv3.shadeIds(mp.host3()):
        result = tpv3.shade(mp.host3(), shadeId)

        if result:
            assert isinstance(result, dict)
            assert result['name']
            assert isinstance(result['type'], int)


def test_2_room(tpv3):
    # def room(self, hubHostname, roomId):

    room_list = requests.get('http://{}/home/rooms/'.format(mp.host3()))
    rooms = room_list.json()

    for room in rooms:
        result = tpv3.room(mp.host3(), room['id'])

        if result:
            assert isinstance(result, dict)
            assert result['name']
            assert isinstance(result['type'], int)
        else:
            pytest.fail('Room not found (id={}'.format(room['id']))


def test_3_scenes(tpv3):
    # def scenes(self, hubHostname):
    result = tpv3.scenes(mp.host3())

    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
        assert result[0]['name']


def test_activate_scene(tpv3):
    # def activateScene(self, hubHostname, sceneId):

    for scene in tpv3.scenes(mp.host3()):
        tpv3.activateScene(mp.host3(), scene['id'])
        assert mp.mock_put_called


def test_jog_shade(tpv3):
    # def jogShade(self, hubHostname, shadeId):

    for shadeId in tpv3.shadeIds(mp.host3()):
        tpv3.jogShade(mp.host3(), shadeId)
        assert mp.mock_put_called


def test_set_shade_position(tpv3):
    # def setShadePosition(self, hubHostname, shadeId, positions):

    for shadeId in tpv3.shadeIds(mp.host3()):
        tpv3.setShadePosition(mp.host3(), shadeId, {'primary': 0, 'secondary': 0, 'tilt': 0, 'velocity': 0})
        assert mp.mock_put_called
