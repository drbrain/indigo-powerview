import logging
import os
import re
import requests

host_ip2 = ''
host_ip3 = ''
mock_get_called_ = False
mock_put_called_ = False
logger = logging.getLogger("net.segment7.powerview")


@property
def mock_get_called():
    global mock_get_called_
    rtn_val = mock_get_called_
    mock_get_called_ = False
    return rtn_val


@property
def mock_put_called():
    global mock_put_called_
    rtn_val = mock_put_called_
    mock_put_called_ = False
    return rtn_val


# custom class to be the mocked return value that
# will override the requests.Response object returned from requests.get and requests.put
class MockResponse(requests.models.Response):

    def __init__(self):
        super().__init__()

        self.status_code = requests.codes.ok  # mock status code is always 200 Success
        self.data = None
        self.url = ''

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


mocked_shade3 = {"id": 1,
                 "type": 5, "name": "QmF5ICBDZW50ZXI=", "ptName": "Bay  Center", "motion": None, "capabilities": 0, "powerType": 0,
                 "batteryStatus": 3, "roomId": 10, "firmware": {"revision": 3, "subRevision": 0, "build": 359}, "shadeGroupIds": [],
                 "positions": {"primary": 0.46, "secondary": 0.25, "tilt": 0, "velocity": 0}, "signalStrength": -49,
                 "bleName": "R23:BA88", "address": "127.0.0.1:1"}
mocked_shades3 = [{"id": 1, "type": 5, "name": "QmF5ICBDZW50ZXI=", "ptName": "Bay  Center", "motion": None, "capabilities": 0, "powerType": 0,
                   "batteryStatus": 3, "roomId": 10, "firmware": {"revision": 3, "subRevision": 0, "build": 359}, "shadeGroupIds": [],
                   "positions": {"primary": 0.46, "secondary": 0, "tilt": 0, "velocity": 0}, "signalStrength": -49, "bleName": "R23:BA88",
                   "address": "127.0.0.1:1"},
                  {"id": 2, "type": 5, "name": "QmF5ICBMZWZ0", "ptName": "Bay  Left", "motion": None, "capabilities": 0, "powerType": 0,
                   "batteryStatus": 3, "roomId": 10, "firmware": {"revision": 3, "subRevision": 0, "build": 359}, "shadeGroupIds": [],
                   "positions": {"primary": 1, "secondary": 0, "tilt": 0, "velocity": 0}, "signalStrength": -62, "bleName": "R23:56E2",
                   "address": "127.0.0.1:2"},
                  {"id": 3, "type": 5, "name": "QmF5ICBSaWdodA==", "ptName": "Bay  Right", "motion": None, "capabilities": 0, "powerType": 0,
                   "batteryStatus": 3, "roomId": 10, "firmware": {"revision": 3, "subRevision": 0, "build": 359}, "shadeGroupIds": [],
                   "positions": {"primary": 0.36, "secondary": 0, "tilt": 0, "velocity": 0}, "signalStrength": -52, "bleName": "R23:3A59",
                   "address": "127.0.0.1:3"}]

mocked_hubs = [{"id": 100, "address": "127.0.0.1:83"}, {"id": 101, "address": "127.0.0.1:82"}]


class MockedShade:
    def __init__(self, shade):
        self.shade = shade

    def __getitem__(self, key=None):
        if key:
            return self.shade[key]
        else:
            return self.shade

    @property
    def address(self):
        if self.shade and 'address' in self.shade:
            return self.shade['address']
        raise KeyError

    @property
    def id(self):
        if self.shade and 'id' in self.shade:
            return self.shade['id']
        raise KeyError

    @property
    def states(self):
        if self.shade:
            if 'id' in self.shade and (self.shade['id'] / 2).is_integer():
                return {"generation": 2}
            else:
                return {"generation": 3}
        raise KeyError


class DeviceMock:
    def __init__(self):
        self.last_item = None

    def __getitem__(self, param=None):
        if param:
            logger.debug("__getitem__: param={}".format(param))
            for item in self.last_item:
                if param == item['id']:
                    return item
        else:
            raise KeyError

    @property
    def id(self):
        logger.debug("id: ")
        if self.last_item and 'id' in self.last_item:
            return self.last_item['id']
        raise KeyError

    def iter(self, it_filter=None):
        logger.debug("DeviceMock.iter: self={}, filter={}".format(self, it_filter))
        if not it_filter:
            self.last_item = [{'id': 1, 'folderId': 0}, {'id': 2, 'folderId': 0}, {'id': 3, 'folderId': 0}]
            logger.debug("DeviceMock.iter: last_item={}".format(self.last_item))
            return self.last_item

        elif it_filter.endswith("Hub"):
            self.last_item = mocked_hubs.copy()
            logger.debug("DeviceMock.iter: Hub last_item={}".format(self.last_item))
            return self.last_item

        elif it_filter.endswith("Shade"):
            self.last_item = []
            for shade in mocked_shades3.copy():
                self.last_item.append(MockedShade(shade))
            logger.debug("DeviceMock.iter: Shade last_item={}".format(self.last_item))
            return self.last_item


def mock_devices():
    mocked_device_list = DeviceMock()
    return mocked_device_list


def mock_get(url: str, headers: str = None) -> MockResponse:
    global mock_get_called_

    mock_get_called_ = True
    resp = MockResponse()
    resp.url = url

    if url.rfind('/home') >= 0:  # if url contains "/home/" it is V3
        a_match = re.search(r"/home/shades/(\d+)", url)
        if a_match is not None:
            shade_id = a_match.group(1)
            if shade_id:  # V3
                resp.data = mocked_shade3.copy()
                resp.data['id'] = shade_id

        elif url.endswith('/home/shades/'):  # V3
            resp.data = mocked_shades3.copy()

        elif url.endswith('/home/rooms/'):  # V3
            resp.data = [{'id': 1, 'name': 'QmVkcm9vbQ==', 'ptName': 'Bedroom', 'color': '11', 'icon': '12', 'type': 0, 'shadeGroups': []},
                         {'id': 10, 'name': 'TGl2aW5nIFJvb20=', 'ptName': 'Living Room', 'color': '7', 'icon': '54', 'type': 0, 'shadeGroups': []},
                         {'id': 30, 'name': 'T2ZmaWNl', 'ptName': 'Office', 'color': '13', 'icon': '123', 'type': 0, 'shadeGroups': []}]

        elif url.endswith('/home/scenes/'):  # V3
            resp.data = [{"id": 58, "name": "RGF5dGltZSBTaGFkZXM=", "ptName": "Daytime Shades", "networkNumber": 64540, "color": "3",
                          "icon": "183", "roomIds": [1, 10, 30], "shadeIds": [1, 2, 3]},
                         {"id": 80, "name": "U2hhZHkgQ291Y2g=", "ptName": "Shady Couch", "networkNumber": 58656, "color": "15",
                          "icon": "184", "roomIds": [10], "shadeIds": [2]},
                         {"id": 12, "name": "TGl2aW5nIFJvb20gT3Blbg==", "ptName": "Living Room Open", "networkNumber": 457, "color": "7",
                          "icon": "183", "roomIds": [10], "shadeIds": [2, 3]},
                         {"id": 14, "name": "TGl2aW5nIFJvb20gQ2xvc2U=", "ptName": "Living Room Close", "networkNumber": 458, "color": "7",
                          "icon": "183", "roomIds": [10], "shadeIds": [2, 3]}]

        elif url.endswith('/home/scenecollections/'):  # V3
            resp.data = []

        elif url.endswith('/home'):  # V3
            resp.data = ""

        else:
            a_match = re.search(r"/home/rooms/(\d+)", url)  # V3
            if a_match is not None:
                room_id = a_match.group(1)
                if room_id:
                    resp.data = {'id': room_id, 'name': 'QmVkcm9vbQ==', 'ptName': 'Bedroom', 'color': '11', 'icon': '12', 'type': 0,
                                 'shadeGroups': []}

            elif url.endswith('/home/activate') and url.rfind('/home/scenes/') > -1:  # V3
                a_match = re.search(r"/home/scenes/(\d+)/", url)
                if a_match is not None:
                    scene_id = a_match.group(1)
                    if scene_id:
                        resp.data = {"id": scene_id, "name": "RXZlbmluZyBTaGFkZXM=", "ptName": "Evening Shades", "networkNumber": 33076, "color": "3",
                                     "icon": "185", "roomIds": [1, 10, 30], "shadeIds": [1, 2, 3]},

            else:
                a_match = re.search(r"/home/scenes?sceneId=(\d+)", url)  # V3
                if a_match is not None:
                    s_id = a_match.group(1)
                    if s_id:
                        resp.data = {"colorId": 9, "iconId": 0, "id": s_id, "name": "U2NlbmUgbmFtZQ==", "networkNumber": 0, "order": 0,
                                     "roomIds": [1]}

    else:  # Check for V2 urls
        a_match = re.search(r"/api/shades/(\d+)", url)
        if a_match is not None:
            shade_id = a_match.group(1)
            if shade_id:
                resp.data = {'shade': {'id': shade_id,
                                       'name': 'TG93ZXIgTGVmdA==', 'roomId': 4102, 'groupId': 28514, 'order': 0, 'type': 6,
                                       'batteryStrength': 142, 'batteryStatus': 2, 'batteryKind': 'unassigned',
                                       'firmware': {'revision': 1, 'subRevision': 3, 'build': 1522}, 'signalStrength': 4,
                                       'motor': {'revision': 0, 'subRevision': 0, 'build': 223}, 'aid': 13, 'capabilities': 0,
                                       'positions': {'position1': 30146, 'posKind1': 1, 'position2': 16384, 'posKind2': 2},
                                       'smartPowerSupply': {'status': 0, 'id': 0, 'port': 0}}}
        elif url.endswith('/api/shades/'):
            resp.data = {'shadeIds': [1, 2, 3], 'shadeData': []}

        elif url.endswith('/api/rooms/'):
            resp.data = {'roomIds': [1, 2], 'roomData': [{'colorId': 15, 'iconId': 10, 'id': 1, 'name': 'Um9vbSBuYW1l', 'order': 0},
                                                         {'colorId': 15, 'iconId': 10, 'id': 2, 'name': 'Um9vbSBuYW1l', 'order': 0}]}

        elif url.endswith('/api/scenes/'):
            resp.data = {'sceneIds': [1, 2], 'sceneData': [{'colorId': 9, 'iconId': 0, 'id': 1, 'name': 'U2NlbmUgbmFtZQ==', 'networkNumber': 0,
                                                            'order': 0, 'roomId': 1},
                                                           {'colorId': 9, 'iconId': 0, 'id': 2, 'name': 'U2NlbmUgbmFtZQ==', 'networkNumber': 0,
                                                            'order': 0, 'roomId': 1}]}
        elif url.endswith('/api/scenecollections/'):
            resp.data = {'sceneCollectionIds': [1, 2], 'sceneCollectionData': [{'colorId': 15, 'iconId': 0, 'id': 1,
                                                                                'name': 'U2NlbmUgY29sbGVjdGlvbiBuYW1l', 'order': 0},
                                                                               {'colorId': 15, 'iconId': 0, 'id': 2,
                                                                                'name': 'U2NlbmUgY29sbGVjdGlvbiBuYW1l', 'order': 0}]}

        elif url.endswith('/api/fwversion'):
            resp.data = ""

        else:
            a_match = re.search(r"/api/rooms/(\d+)", url)
            if a_match is not None:
                room_id = a_match.group(1)
                if room_id:
                    resp.data = {'room': {'colorId': 15, 'iconId': 10, 'id': room_id, 'name': 'Um9vbSBuYW1l', 'order': 0}, 'roomData': []}
            else:
                a_match = re.search(r"/api/scenes?sceneId=(\d+)", url)
                if a_match is not None:
                    scene_id = a_match.group(1)
                    if scene_id:
                        resp.data = {'colorId': 9, 'iconId': 0, 'id': scene_id, 'name': 'U2NlbmUgbmFtZQ==', 'networkNumber': 0, 'order': 0,
                                     'roomId': 1}
    return resp


def mock_put(url: str, data=None, json=None, headers=None) -> MockResponse:
    global mock_put_called_
    mock_put_called_ = True
    resp = MockResponse()
    resp.url = url
    resp.data = data if data else json

    return resp


def hub_host2() -> str:
    global host_ip2
    if not host_ip2:
        local_ip = '127.0.0.1:82'  # localhost
        host_ip2 = os.getenv('POWERVIEW_GATEWAY_IP', default=local_ip)
        if host_ip2 == local_ip:
            logger.error("mock_powerview: No hub defined for testing, so using built-in tests. To test with a local V2 hub, define an "
                         "Environment Variable: POWERVIEW_GATEWAY_IP=<host IP or hostname>. Testing with a local hub will read information "
                         "from the hub but will make no changes.")
        else:
            logger.error("mock_powerview: Using v2 hub {}".format(host_ip2))
    return host_ip2


def hub_host3() -> str:
    global host_ip3
    if not host_ip3:
        local_ip = '127.0.0.1:83'  # localhost
        host_ip3 = os.getenv('POWERVIEW3_GATEWAY_IP', default=local_ip)
        if host_ip3 == local_ip:
            logger.error("mock_powerview: No hub defined for testing, so using built-in tests. To test with a local V3 gateway, define an "
                         "Environment Variable: POWERVIEW3_GATEWAY_IP=<host IP or hostname>. Testing with a local hub will read information "
                         "from the hub but will make no changes.")
        else:
            logger.error("mock_powerview: Using v3 gateway {}".format(host_ip3))
    return host_ip3


def hub_available(vers) -> bool:
    if vers == "V2":
        local_ip = '127.0.0.1:82'  # localhost
        return local_ip != hub_host2()

    elif vers == "V3":
        local_ip = '127.0.0.1:83'  # localhost
        return local_ip != hub_host3()

    else:
        logger.error("mock_powerview: Invalid call to hub_available() with parameter={}".format(vers))
