import logging
import os
import re
import requests

host_ip = ''
mock_get_called = False
mock_put_called = False


# custom class to be the mocked return value that
# will override the requests.Response object returned from requests.get and requests.put
class MockResponse(requests.models.Response):
    def __init__(self):
        super().__init__()

        self.status_code = requests.codes.ok  # mock status code is always 200 Success
        self.data = None
        self.url = ''

        self.logger = logging.getLogger('Plugin')
        self.logger.setLevel(10)

    # mock json() method always returns a specific testing dictionary
    def json(self, *args, **kwds):
        # if self.data:
        #     return mock_get2(self.url).data
        #     # return {"mock_key": "static response json for put() from MockResponse class"}
        # else:
        #     return self.data
        return self.data

    def set_json(self, value):
        self.data = value


def mock_get2(url: str, headers: str = None) -> MockResponse:
    global mock_get_called

    mock_get_called = True
    resp = MockResponse()
    resp.url = url

    a_match = re.search(r"/shades/(\d+)", url)
    if a_match is not None:
        shade_id = a_match.group(1)
        if shade_id:
            resp.data = {'shade': {'id': shade_id,
                                   'name': 'TG93ZXIgTGVmdA==', 'roomId': 4102, 'groupId': 28514, 'order': 0, 'type': 6,
                                   'batteryStrength': 142, 'batteryStatus': 2,
                                   'firmware': {'revision': 1, 'subRevision': 3, 'build': 1522}, 'signalStrength': 4,
                                   'motor': {'revision': 0, 'subRevision': 0, 'build': 223}, 'aid': 13, 'capabilities': 0,
                                   'batteryKind': 'unassigned', 'positions': {'position1': 30146, 'posKind1': 1, 'position2': 16384, 'posKind2': 2},
                                   'smartPowerSupply': {'status': 0, 'id': 0, 'port': 0}}}
    elif url.endswith('/shades/'):
        resp.data = {'shadeIds': [1, 2, 3], 'shadeData': []}

    elif url.endswith('/rooms/'):
        resp.data = {'roomIds': [1, 2], 'roomData': [{"colorId": 15, "iconId": 10, "id": 1, "name": "Um9vbSBuYW1l", "order": 0},
                                                     {"colorId": 15, "iconId": 10, "id": 2, "name": "Um9vbSBuYW1l", "order": 0}]}

    elif url.endswith('/scenes/'):
        resp.data = {'sceneIds': [1, 2], 'sceneData': [{"colorId": 9, "iconId": 0, "id": 1, "name": "U2NlbmUgbmFtZQ==", "networkNumber": 0,
                                                        "order": 0, "roomId": 1},
                                                       {"colorId": 9, "iconId": 0, "id": 1, "name": "U2NlbmUgbmFtZQ==", "networkNumber": 0,
                                                        "order": 0, "roomId": 1}]}
    elif url.endswith('/scenecollections/'):
        resp.data = {'sceneCollectionIds': [1, 2], 'sceneCollectionData': [{"colorId": 15, "iconId": 0, "id": 1,
                                                                            "name": "U2NlbmUgY29sbGVjdGlvbiBuYW1l", "order": 0},
                                                                           {"colorId": 15, "iconId": 0, "id": 2,
                                                                            "name": "U2NlbmUgY29sbGVjdGlvbiBuYW1l", "order": 0}]}
    else:
        a_match = re.search(r"/rooms/(\d+)", url)
        if a_match is not None:
            room_id = a_match.group(1)
            if room_id:
                resp.data = {'room': {"colorId": 15, "iconId": 10, "id": room_id, "name": "Um9vbSBuYW1l", "order": 0}, 'roomData': []}
        else:
            a_match = re.search(r"/scenes?sceneId=(\d+)", url)
            if a_match is not None:
                scene_id = a_match.group(1)
                if scene_id:
                    resp.data = {"colorId": 9, "iconId": 0, "id": scene_id, "name": "U2NlbmUgbmFtZQ==", "networkNumber": 0, "order": 0, "roomId": 1}
    return resp


def mock_get3(url: str, headers: str = None) -> MockResponse:
    global mock_get_called

    mock_get_called = True
    resp = MockResponse()
    resp.url = url
    # URL_ROOM_ = 'http://{h}/home/rooms/{id}'
    # URL_SHADES_ = 'http://{h}/home/shades/{id}'
    # URL_SHADES_MOTION_ = 'http://{h}/home/shades/{id}/motion'
    # URL_SHADES_POSITIONS_ = 'http://{h}/home/shades/positions?ids={id}'
    # URL_SHADES_STOP_ = 'http://{h}/home/shades/stop?ids={id}'
    # URL_SCENES_ = 'http://{h}/home/scenes/{id}'
    # URL_SCENES_ACTIVATE_ = 'http://{h}/home/scenes/{id}/activate'

    a_match = re.search(r"/shades/(\d+)", url)
    if a_match is not None:
        shade_id = a_match.group(1)
        if shade_id:  # V3
            resp.data = {'id': shade_id,
                         'type': 5, 'name': 'QmF5ICBDZW50ZXI=', 'ptName': 'Bay  Center', 'motion': None, 'capabilities': 0, 'powerType': 0,
                         'batteryStatus': 3, 'roomId': 10, 'firmware': {'revision': 3, 'subRevision': 0, 'build': 359}, 'shadeGroupIds': [],
                         'positions': {'primary': 0.46, 'secondary': 0.25, 'tilt': 0, 'velocity': 0}, 'signalStrength': -49, 'bleName': 'R23:BA88'}
    elif url.endswith('/shades/'):  # V3
        resp.data = [{'id': 1, 'type': 5, 'name': 'QmF5ICBDZW50ZXI=', 'ptName': 'Bay  Center', 'motion': None, 'capabilities': 0, 'powerType': 0,
                      'batteryStatus': 3, 'roomId': 10, 'firmware': {'revision': 3, 'subRevision': 0, 'build': 359}, 'shadeGroupIds': [],
                      'positions': {'primary': 0.46, 'secondary': 0, 'tilt': 0, 'velocity': 0}, 'signalStrength': -49, 'bleName': 'R23:BA88'},
                     {'id': 2, 'type': 5, 'name': 'QmF5ICBMZWZ0', 'ptName': 'Bay  Left', 'motion': None, 'capabilities': 0, 'powerType': 0,
                      'batteryStatus': 3, 'roomId': 10, 'firmware': {'revision': 3, 'subRevision': 0, 'build': 359}, 'shadeGroupIds': [],
                      'positions': {'primary': 1, 'secondary': 0, 'tilt': 0, 'velocity': 0}, 'signalStrength': -62, 'bleName': 'R23:56E2'},
                     {'id': 3, 'type': 5, 'name': 'QmF5ICBSaWdodA==', 'ptName': 'Bay  Right', 'motion': None, 'capabilities': 0, 'powerType': 0,
                      'batteryStatus': 3, 'roomId': 10, 'firmware': {'revision': 3, 'subRevision': 0, 'build': 359}, 'shadeGroupIds': [],
                      'positions': {'primary': 0.36, 'secondary': 0, 'tilt': 0, 'velocity': 0}, 'signalStrength': -52, 'bleName': 'R23:3A59'}]

    elif url.endswith('/rooms/'):  # V3
        resp.data = [{'id': 1, 'name': 'QmVkcm9vbQ==', 'ptName': 'Bedroom', 'color': '11', 'icon': '12', 'type': 0, 'shadeGroups': []},
                     {'id': 10, 'name': 'TGl2aW5nIFJvb20=', 'ptName': 'Living Room', 'color': '7', 'icon': '54', 'type': 0, 'shadeGroups': []},
                     {'id': 30, 'name': 'T2ZmaWNl', 'ptName': 'Office', 'color': '13', 'icon': '123', 'type': 0, 'shadeGroups': []}]

    elif url.endswith('/scenes/'):  # V3
        resp.data = [{"id": 58, "name": "RGF5dGltZSBTaGFkZXM=", "ptName": "Daytime Shades", "networkNumber": 64540, "color": "3", "icon": "183",
                      "roomIds": [1, 10, 30], "shadeIds": [1, 2, 3]},
                     {"id": 80, "name": "U2hhZHkgQ291Y2g=", "ptName": "Shady Couch", "networkNumber": 58656, "color": "15", "icon": "184",
                      "roomIds": [10], "shadeIds": [2]},
                     {"id": 12, "name": "TGl2aW5nIFJvb20gT3Blbg==", "ptName": "Living Room Open", "networkNumber": 457, "color": "7", "icon": "183",
                      "roomIds": [10], "shadeIds": [2, 3]},
                     {"id": 14, "name": "TGl2aW5nIFJvb20gQ2xvc2U=", "ptName": "Living Room Close", "networkNumber": 458, "color": "7", "icon": "185",
                      "roomIds": [10], "shadeIds": [2, 3]}]

    elif url.endswith('/scenecollections/'):  # V3
        resp.data = []
    else:
        a_match = re.search(r"/rooms/(\d+)", url)  # V3
        if a_match is not None:
            room_id = a_match.group(1)
            if room_id:
                resp.data = {'id': room_id, 'name': 'QmVkcm9vbQ==', 'ptName': 'Bedroom', 'color': '11', 'icon': '12', 'type': 0, 'shadeGroups': []}

        elif url.endswith('/activate') and url.rfind('/scenes/') > -1:  # V3
            a_match = re.search(r"/scenes/(\d+)/", url)
            if a_match is not None:
                scene_id = a_match.group(1)
                if scene_id:
                    resp.data = {"id": scene_id, "name": "RXZlbmluZyBTaGFkZXM=", "ptName": "Evening Shades", "networkNumber": 33076, "color": "3",
                                 "icon": "185", "roomIds": [1, 10, 30], "shadeIds": [1, 2, 3]},

        else:
            a_match = re.search(r"/scenes?sceneId=(\d+)", url)  # V3
            if a_match is not None:
                s_id = a_match.group(1)
                if s_id:
                    resp.data = {"colorId": 9, "iconId": 0, "id": s_id, "name": "U2NlbmUgbmFtZQ==", "networkNumber": 0, "order": 0, "roomIds": [1]}
    return resp


def mock_put(url: str, data=None, json=None) -> MockResponse:
    global mock_put_called
    mock_put_called = True
    resp = MockResponse()
    resp.url = url
    resp.data = data if data else json

    return resp


def host2():
    global host_ip
    if not host_ip:
        local_ip = '127.0.0.1'  # localhost
        host_ip = os.getenv('POWERVIEW_GATEWAY_IP', default=local_ip)
        logger = logging.getLogger('Plugin')
        if host_ip == local_ip:
            logger.error("mock_powerview: No hub defined for testing, so using built-in tests. To test with a local V2 hub, define an "
                         "Environment Variable: POWERVIEW_GATEWAY_IP=<host IP or hostname>. Testing with a local hub will read information "
                         "from the hub but will make no changes.")
        else:
            logger.error("mock_powerview: Using v2 hub {}".format(host_ip))
    return host_ip


def host3():
    global host_ip
    if not host_ip:
        local_ip = '127.0.0.1'  # localhost
        host_ip = os.getenv('POWERVIEW3_GATEWAY_IP', default=local_ip)
        logger = logging.getLogger('Plugin')
        if host_ip == local_ip:
            logger.error("mock_powerview: No hub defined for testing, so using built-in tests. To test with a local V3 gateway, define an "
                         "Environment Variable: POWERVIEW3_GATEWAY_IP=<host IP or hostname>. Testing with a local hub will read information "
                         "from the hub but will make no changes.")
        else:
            logger.error("mock_powerview: Using v3 gateway {}".format(host_ip))
    return host_ip
