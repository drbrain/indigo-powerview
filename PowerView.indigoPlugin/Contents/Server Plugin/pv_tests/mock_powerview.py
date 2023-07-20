
import logging
import pv_runner as pv
import re
import requests

# DEV_ID_V2 = 1  # Device ID of Mocked V2 shade
# DEV_ID_V3 = 3  # Device ID of Mocked V3 shade
LOCAL_IP_V2 = 'localhost'
LOCAL_IP_V3 = '127.0.0.1'  # localhost

host_ip2 = ''
host_ip3 = ''
logger = logging.getLogger("wsgmac.com.test.powerview")
__mock_put_called = False
put_response = None

A_MOCKED_SHADE3 = {"id": 1,
                   "type": 5, "name": "RGF5dGltZSBTaGFkZXM=", "ptName": "Mock Bay Center", "motion": None, "capabilities": 0, "powerType": 0,
                   "batteryStatus": 3, "roomId": 10, "firmware": {"revision": 3, "subRevision": 0, "build": 359}, "shadeGroupIds": [],
                   "positions": {"primary": 0.46, "secondary": 0.25, "tilt": 0, "velocity": 0}, "signalStrength": -49,
                   "bleName": "R23:BA88"}
MOCKED_SHADES3 = [{"id": 1, "type": 5, "name": "RGF5dGltZSBTaGFkZXM=", "ptName": "Mock Bay  Center", "motion": None, "capabilities": 0, "powerType": 0,
                   "batteryStatus": 3, "roomId": 10, "firmware": {"revision": 3, "subRevision": 0, "build": 359}, "shadeGroupIds": [],
                   "positions": {"primary": 0.46, "secondary": 0, "tilt": 0, "velocity": 0}, "signalStrength": -49, "bleName": "R23:BA88"},
                  {"id": 2, "type": 5, "name": "QmF5ICBMZWZ0", "ptName": "Mock Bay  Left", "motion": None, "capabilities": 0, "powerType": 0,
                   "batteryStatus": 3, "roomId": 10, "firmware": {"revision": 3, "subRevision": 0, "build": 359}, "shadeGroupIds": [],
                   "positions": {"primary": 1, "secondary": 0, "tilt": 0, "velocity": 0}, "signalStrength": -62, "bleName": "R23:56E2"},
                  {"id": 3, "type": 5, "name": "QmF5ICBSaWdodA==", "ptName": "Mock Bay  Right", "motion": None, "capabilities": 0, "powerType": 0,
                   "batteryStatus": 3, "roomId": 10, "firmware": {"revision": 3, "subRevision": 0, "build": 359}, "shadeGroupIds": [],
                   "positions": {"primary": 0.36, "secondary": 0, "tilt": 0, "velocity": 0}, "signalStrength": -52, "bleName": "R23:3A59"},
                  {"id": 71, "type": 5, "name": "Tm9uLURldmljZSBTaGFkZSA3MQ==", "ptName": "Mock Bay  Center", "motion": None, "capabilities": 0,
                   "powerType": 0, "batteryStatus": 3, "roomId": 10, "firmware": {"revision": 3, "subRevision": 0, "build": 359}, "shadeGroupIds": [],
                   "positions": {"primary": 0.46, "secondary": 0, "tilt": 0, "velocity": 0}, "signalStrength": -49, "bleName": "R23:BA88"},
                  {"id": 72, "type": 5, "name": "Tm9uLURldmljZSBTaGFkZSA3Mg==", "ptName": "Mock Bay  Left", "motion": None, "capabilities": 0,
                   "powerType": 0, "batteryStatus": 3, "roomId": 10, "firmware": {"revision": 3, "subRevision": 0, "build": 359}, "shadeGroupIds": [],
                   "positions": {"primary": 1, "secondary": 0, "tilt": 0, "velocity": 0}, "signalStrength": -62, "bleName": "R23:56E2"}]
MOCKED_DEVICES = [{'id': 1, 'folderId': 0, 'address': 'V2:1', 'deviceTypeId': 'PowerViewShade', 'name': 'Shade 1', 'generation': 2},
                  {'id': 10, 'folderId': 0, 'address': 'V2', 'deviceTypeId': 'PowerViewHub', 'name': 'V2 Hub 10', 'generation': 2},
                  {'id': 20, 'folderId': 0, 'address': 'V3', 'deviceTypeId': 'PowerViewHub', 'name': 'V3 Hub 20', 'generation': 3},
                  {'id': 201, 'folderId': 0, 'address': '201', 'deviceTypeId': 'SomeDev', 'name': 'A Device 201'},
                  {'id': 2, 'folderId': 0, 'address': "V3:2", 'deviceTypeId': 'PowerViewShade', 'name': 'Shade 2', 'generation': 3},
                  {'id': 202, 'folderId': 0, 'address': '202', 'deviceTypeId': 'SomeDev', 'name': 'A Device 202'},
                  {'id': 203, 'folderId': 0, 'address': '203', 'deviceTypeId': 'SomeDev', 'name': 'A Device 203'},
                  {'id': 3, 'folderId': 0, 'address': "V3:3", 'deviceTypeId': 'PowerViewShade', 'name': 'Shade 3', 'generation': 3}]


class MockPowerView:
    instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MockPowerView, cls).__new__(cls)
        return cls.instance

    # custom class to be the mocked return value that
    # will override the requests.Response object returned from requests.get and requests.put
    class MockResponse(requests.models.Response):

        def __init__(self):
            super().__init__()

            self.status_code = 0  # mock status code is always 200 Success
            self.data = None
            self.url = ''

        def __repr__(self):
            return "Status = {} Data={}".format(self.status_code, self.data)

        # mock json() method always returns a specific testing dictionary
        def json(self, *args, **kwds):
            return self.data

        def set_json(self, value):
            self.data = value

        @property
        def text(self) -> str:
            return str(self.data)

    class DevicesMock:
        def __init__(self):
            self.last_item = None

        def __getitem__(self, param=None):
            if param:
                for item in MOCKED_DEVICES:
                    if param == item['id']:
                        # logger.debug(f"devices[{param}]: Returning device={item}")
                        return self.MockedDevice(item)
                # logger.debug(f"No id={param} in last_item={MOCKED_DEVICES}")
            raise KeyError

        class MockedDevice:
            def __init__(self, data):
                self.device_data = data
                self.deviceTypeId = data.get('deviceTypeId', 'PowerViewShade')
                self.pluginProps = {}

            def __getitem__(self, key=None):
                if key:
                    return self.device_data[key]
                else:
                    return self.device_data

            def __repr__(self):
                return "MockedDevice={}".format(self.device_data)

            @property
            def address(self):
                if self.device_data and 'address' in self.device_data:
                    return self.device_data['address']
                raise KeyError('address')

            @property
            def folderId(self):
                if self.device_data and 'folderId' in self.device_data:
                    return self.device_data['folderId']
                else:
                    return None

            @property
            def id(self):
                if self.device_data and 'id' in self.device_data:
                    return self.device_data['id']
                raise KeyError('id')

            @property
            def name(self):
                if self.device_data and 'name' in self.device_data:
                    return self.device_data['name']
                raise KeyError('name')

            def replacePluginPropsOnServer(self, props):
                logger.debug("In mocked replacePluginPropsOnServer")
                pass

            def stateListOrDisplayStateIdChanged(self):
                pass

            def updateStateOnServer(self, key=None, value=None):
                pass

            @property
            def states(self):
                if self.device_data:
                    # logger.debug("MockedDevice.states: shade={}".format(self.device_data))
                    if 'address' in self.device_data and (self.device_data['address'].startswith(host_ip2)):
                        # logger.debug("MockedDevice.states: gen=2")
                        return {"generation": 2}
                    elif 'address' in self.device_data and (self.device_data['address'].startswith(host_ip3)):
                        # logger.debug("MockedDevice.states: gen=3")
                        return {"generation": 3}
                raise KeyError('states')

        @property
        def id(self):
            # logger.debug("id: ")
            if self.last_item and 'id' in self.last_item:
                return self.last_item['id']
            raise KeyError('id')

        def iter(self, it_filter=None):
            # logger.debug("DeviceMock.iter: self={}, filter={}".format(self, it_filter))
            self.last_item = []
            item_list = []
            for item in MOCKED_DEVICES:
                if item['address']:
                    if item['address'].find(':') > -1:
                        ip, node = item['address'].split(':')
                        new_address = f"{host_ip3}:{node}" if ip == 'V3' else (f"{host_ip2}:{node}" if ip == 'V2' else f"{ip}:{node}")
                    else:
                        ip = item['address']
                        new_address = f"{host_ip3}" if ip == 'V3' else (f"{host_ip2}" if ip == 'V2' else ip)
                    # logger.debug("iter: Address was {} converted to {} for {}".format(item['address'], new_address, item))
                    item['address'] = new_address
                item_list.append(item)
                # logger.debug("DeviceMock.iter: item_list={}".format(str(item_list)))

            if (not it_filter) or it_filter.endswith("self") or it_filter.endswith("net.segment7.powerview"):
                for item in item_list:
                    self.last_item.append(self.MockedDevice(item))
                # logger.debug("DeviceMock.iter: last_item={}".format(str(self.last_item)))
                return self.last_item

            elif it_filter.endswith("Hub"):
                for item in item_list:
                    if item['deviceTypeId'] == 'PowerViewHub':
                        self.last_item.append(self.MockedDevice(item))
                # logger.debug("DeviceMock.iter: Hub last_item={}".format(str(self.last_item)))
                return self.last_item

            elif it_filter.endswith("Shade"):
                for item in item_list:
                    if item['deviceTypeId'] == 'PowerViewShade':
                        self.last_item.append(self.MockedDevice(item))
                # logger.debug("DeviceMock.iter: Shade last_item={}".format(str(self.last_item)))
                return self.last_item

    @staticmethod
    def mock_put_called():
        global __mock_put_called
        rtn_val = __mock_put_called
        __mock_put_called = False
        return rtn_val

    @staticmethod
    def mock_replacePluginPropsOnServer(self, props):
        pass

    @staticmethod
    def mock_do_get(self, url: str, *param, **kwargs):
        global __mock_put_called
        __mock_put_called = False

        if url.rfind(LOCAL_IP_V2) > -1 or url.rfind(LOCAL_IP_V3) > -1:
            return MockPowerView.mock_get(self, url, *param, **kwargs)
        return requests.get(url, *param, **kwargs)

    def mock_get(self, url, *param, **kwargs) -> MockResponse:
        resp = MockPowerView.MockResponse()
        resp.url = url

        if url.rfind(LOCAL_IP_V3) >= 0 and url.rfind('/home') >= 0:  # if url contains "/home/" it is V3
            a_match = re.search(r"/home/shades/(\d+)", url)
            if a_match is not None:
                shade_id = a_match.group(1)
                if shade_id:  # V3
                    resp.data = A_MOCKED_SHADE3.copy()
                    resp.data['address'] = f"{host_ip2}:{shade_id}" if shade_id == 1 else f"{host_ip3}:{shade_id}"
                    resp.data['id'] = shade_id

            elif url.endswith('/home/shades/'):  # V3
                resp.data = MOCKED_SHADES3.copy()

            elif url.endswith('/home/rooms/'):  # V3
                resp.data = [{'id': 1, 'name': 'QmVkcm9vbQ==', 'ptName': 'Mock Bedroom', 'color': '11', 'icon': '12', 'type': 0, 'shadeGroups': []},
                             {'id': 10, 'name': 'TGl2aW5nIFJvb20=', 'ptName': 'Mock Living Room', 'color': '7', 'icon': '54', 'type': 0,
                              'shadeGroups': []},
                             {'id': 30, 'name': 'T2ZmaWNl', 'ptName': 'Mock Office', 'color': '13', 'icon': '123', 'type': 0, 'shadeGroups': []}]

            elif url.endswith('/home/scenes/'):  # V3
                resp.data = [{"id": 58, "name": "RGF5dGltZSBTaGFkZXM=", "ptName": "Mock Daytime Shades", "networkNumber": 64540, "color": "3",
                              "icon": "183", "roomIds": [1, 10, 30], "shadeIds": [1, 2, 3]},
                             {"id": 80, "name": "U2hhZHkgQ291Y2g=", "ptName": "Mock Shady Couch", "networkNumber": 58656, "color": "15",
                              "icon": "184", "roomIds": [10], "shadeIds": [2]},
                             {"id": 12, "name": "TGl2aW5nIFJvb20gT3Blbg==", "ptName": "Mock Living Room Open", "networkNumber": 457, "color": "7",
                              "icon": "183", "roomIds": [10], "shadeIds": [2, 3]},
                             {"id": 14, "name": "TGl2aW5nIFJvb20gQ2xvc2U=", "ptName": "Mock Living Room Close", "networkNumber": 458, "color": "7",
                              "icon": "183", "roomIds": [10], "shadeIds": [2, 3]}]

            elif url.endswith('/home/scenecollections/'):  # V3
                resp.data = 'OK'

            elif url.endswith('/home'):  # V3
                logger.debug("Getting OK result for /home")
                resp.data = "OK"

            else:
                a_match = re.search(r"/home/rooms/(\d+)", url)  # V3
                if a_match is not None:
                    room_id = a_match.group(1)
                    if room_id:
                        resp.data = {'id': room_id, 'name': 'QmVkcm9vbQ==', 'ptName': 'Mock Bedroom', 'color': '11', 'icon': '12', 'type': 0,
                                     'shadeGroups': []}

                elif url.endswith('/home/activate') and url.rfind('/home/scenes/') > -1:  # V3
                    a_match = re.search(r"/home/scenes/(\d+)/", url)
                    if a_match is not None:
                        scene_id = a_match.group(1)
                        if scene_id:
                            resp.data = {"id": scene_id, "name": "RXZlbmluZyBTaGFkZXM=", "ptName": "Mock Evening Shades", "networkNumber": 33076,
                                         "color": "3",
                                         "icon": "185", "roomIds": [1, 10, 30], "shadeIds": [1, 2, 3]},

                else:
                    a_match = re.search(r"/home/scenes\?sceneId=(\d+)", url)  # V3
                    if a_match is not None:
                        s_id = a_match.group(1)
                        if s_id:
                            resp.data = {"colorId": 9, "iconId": 0, "id": s_id, "name": "U2NlbmUgbmFtZQ==", "networkNumber": 0, "order": 0,
                                         "roomIds": [1]}

        elif url.rfind(LOCAL_IP_V2) >= 0 and url.rfind('/api/') >= 0:  # Check for V2 urls
            a_match = re.search(r"/api/shades/(\d+)", url)
            if a_match is not None:
                shade_id = a_match.group(1)
                if shade_id:
                    resp.data = {'shadeIds': [shade_id],
                                 'shade': {'id': shade_id,
                                           'name': 'RG91YmxlIFRyYW5zb20=', 'roomId': 4102, 'groupId': 28514, 'order': 0, 'type': 6,
                                           'batteryStrength': 142, 'batteryStatus': 2, 'batteryKind': 'Mock unassigned',
                                           'firmware': {'revision': 1, 'subRevision': 3, 'build': 1522}, 'signalStrength': 4,
                                           'motor': {'revision': 0, 'subRevision': 0, 'build': 223}, 'aid': 13, 'capabilities': 0,
                                           'positions': {'position1': 30146, 'posKind1': 1, 'position2': 16384, 'posKind2': 2},
                                           'smartPowerSupply': {'status': 0, 'id': 0, 'port': 0}}}
            elif url.endswith('/api/shades/'):
                resp.data = {'shadeIds': [1, 2, 3, 71, 72], 'shadeData': []}

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

            elif (url.find(LOCAL_IP_V2) > -1) and (url.endswith('/api/fwversion')):
                logger.debug("Getting OK result for /api/fwversion")
                resp.data = "OK"

            else:
                a_match = re.search(r"/api/rooms/(\d+)", url)
                if a_match is not None:
                    room_id = a_match.group(1)
                    if room_id:
                        resp.data = {'room': {'colorId': 15, 'iconId': 10, 'id': room_id, 'name': 'Um9vbSBuYW1l', 'order': 0}, 'roomData': []}
                else:
                    a_match = re.search(r"/api/scenes\?sceneId=(\d+)", url)
                    if a_match is not None:
                        scene_id = a_match.group(1)
                        if scene_id:
                            resp.data = {'colorId': 9, 'iconId': 0, 'id': scene_id, 'name': 'U2NlbmUgbmFtZQ==', 'networkNumber': 0, 'order': 0,
                                         'roomId': 1}
                    else:
                        a_match = re.search(r"/api/scenecollections\?scenecollectionid=(\d+)", url)
                        if a_match is not None:
                            scene_id = a_match.group(1)
                            if scene_id:
                                resp.data = {'colorId': 15, 'iconId': 0, 'id': 1, 'name': 'U2NlbmUgY29sbGVjdGlvbiBuYW1l', 'order': 0}
        else:
            resp.data = None  # Flag invalid url

        resp.status_code = requests.codes.ok if resp.data else requests.codes.forbidden
        logger.debug(f'get url={url} response={resp}')
        return resp

    @staticmethod
    def mock_put(url: str, data=None, json=None, headers=None) -> MockResponse:
        global __mock_put_called
        global put_response

        __mock_put_called = True
        resp = MockPowerView.MockResponse()
        resp.status_code = requests.codes.ok
        resp.url = url
        resp.data = data if data else json
        put_response = resp

        return resp

    @staticmethod
    def hub_host2() -> str:
        global host_ip2
        global host_ip3

        if not host_ip2:
            host_ip2 = pv.get_default_hubs().get("hub2", LOCAL_IP_V2)
            # host_ip3 = pv.get_default_hubs().get("hub3", LOCAL_IP_V3)
            if host_ip2 == LOCAL_IP_V2:
                logger.debug(
                    "mock_powerview: No hub defined for testing, so using built-in tests. Testing with a local hub will read information "
                    "from the hub but will make no changes.")
                logger.debug("mock_powerview: pv.get_default_hubs={}".format(pv.get_default_hubs()))
            else:
                logger.debug("mock_powerview: Using v2 hub {}".format(host_ip2))
        return host_ip2

    @staticmethod
    def hub_host3() -> str:
        global host_ip2
        global host_ip3

        if not host_ip3:
            # host_ip2 = pv.get_default_hubs().get("hub2", LOCAL_IP_V2)
            host_ip3 = pv.get_default_hubs().get("hub3", LOCAL_IP_V3)
            if host_ip3 == LOCAL_IP_V3:
                logger.debug(
                    "mock_powerview: No hub defined for testing, so using built-in tests. Testing with a local hub will read information "
                    "from the hub but will make no changes. {}")
                logger.debug("mock_powerview: pv.get_default_hubs={}".format(pv.get_default_hubs()))
            else:
                logger.debug("mock_powerview: Using v3 gateway {}".format(host_ip3))
        return host_ip3

    @staticmethod
    def hub_available(vers) -> bool:
        rtn = False
        if vers == "V2":
            rtn = LOCAL_IP_V2 != MockPowerView.hub_host2()

        elif vers == "V3":
            rtn = LOCAL_IP_V3 != MockPowerView.hub_host3()

        else:
            logger.debug("hub_available: Invalid call to hub_available() with parameter={}".format(vers))
        # logger.debug(f"hub_available: {vers} hub returned {rtn}")
        return rtn
