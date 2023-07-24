
import base64
import logging
import math
import requests
import requests.api
try:
    import indigo
except ImportError:
    pass


class PowerView:
    GENERATION = "V2"

    def __init__(self, prefs):
        super().__init__()
        self.logger = logging.getLogger(prefs.get('logger', "net.segment7.powerview"))

    def activateScene(self, hubHostname, sceneId):
        activateSceneUrl = 'http://%s/api/scenes?sceneId=%s' % (hubHostname, sceneId)

        self.get(activateSceneUrl)

    def activateSceneCollection(self, hubHostname, sceneCollectionId):
        activateSceneCollectionUrl = \
            'http://%s/api/scenecollections?scenecollectionid=%s' % (hubHostname, sceneCollectionId)

        self.get(activateSceneCollectionUrl)

    def calibrateShade(self, hubHostname, shadeId):
        shadeUrl = 'http://%s/api/shades/%s' % (hubHostname, shadeId)

        body = {
            'shade': {
                'motion': 'calibrate'
            }
        }

        self.put(shadeUrl, body)

    def jogShade(self, hubHostname, shadeId):
        shadeUrl = 'http://%s/api/shades/%s' % (hubHostname, shadeId)

        body = {
            'shade': {
                'motion': 'jog'
            }
        }

        self.put(shadeUrl, body)

    def stopShade(self, hubHostname, shadeId):
        indigo.server.log('Stop Shade function is not available on Generation 2 gateway.')
        pass

    def room(self, hubHostname, roomId):
        roomUrl = 'http://%s/api/rooms/%s' % (hubHostname, roomId)

        data = self.get(roomUrl)['room']

        data['name'] = base64.b64decode(data.pop('name')).decode()

        return data

    def setShadePosition(self, hubHostname, shadeId, pos):
        shadeUrl = 'http://%s/api/shades/%s' % (hubHostname, shadeId)

        # convert 0-100 values to 0-65535.
        primary = pos.get('primary', '0')
        secondary = pos.get('secondary', '0')

        if primary in range(101) and secondary in range(101):
            # New integer percentage 0 to 100 where 100% means fully open
            top = int((float(secondary) / 65535.0 * 100.0) + 0.5)
            bottom = int((float(primary) / 65535.0 * 100.0) + 0.5)
        else:
            # Assume Set Shade Position Action has not been edited since the plugin was updated and still uses the V2 position values.
            self.logger.warning(f"setShadePosition: Position uses V2 values 0-65k. Using bottom={primary} and top={secondary} as is.")
            top = secondary
            bottom = primary
        body = {
            'shade': {
                'positions': {
                    'position1': bottom,
                    'posKind1': 1,
                    'position2': top,
                    'posKind2': 2
                }
            }
        }

        self.put(shadeUrl, body)

    def scenes(self, hubHostname):
        scenesURL = 'http://%s/api/scenes/' % (hubHostname)

        data = self.get(scenesURL)['sceneData']

        for scene in data:
            name = base64.b64decode(scene.pop('name')).decode()
            room = self.room(hubHostname, scene['roomId'])
            scene['name'] = '%s - %s' % (room['name'], name)

        return data

    def sceneCollections(self, hubHostname):
        sceneCollectionsUrl = 'http://%s/api/scenecollections/' % (hubHostname)

        data = self.get(sceneCollectionsUrl)['sceneCollectionData']

        for sceneCollection in data:
            sceneCollection['name'] = base64.b64decode(sceneCollection.pop('name')).decode()

        return data

    def shade(self, hubHostname, shadeId, room=False):
        shadeUrl = 'http://%s/api/shades/%s' % (hubHostname, shadeId)

        data = self.get(shadeUrl)
        if data == '':
            return {}

        data = data.pop('shade')
        data['shadeId'] = data.pop('id')

        data['name'] = base64.b64decode(data.pop('name')).decode()
        data['batteryLevel'] = data.pop('batteryStrength')
        data['generation'] = 2
        if room and 'roomId' in data:
            room_data = self.room(hubHostname, data['roomId'])
            data['room'] = room_data['name']

        # convert positions to a range of 0 to 1
        positions = data.get('positions', [])
        if 'position1' in positions:
            if positions['posKind1'] == 1:
                positions['primary'] = positions['position1'] / 65535
            else:
                positions['secondary'] = positions['position1'] / 65535
        if 'position2' in positions:
            if positions['posKind2'] == 1:
                positions['primary'] = positions['position2'] / 65535
            else:
                positions['secondary'] = positions['position2'] / 65535
        if 'primary' not in positions:
            positions['primary'] = 0.0
        if 'secondary' not in positions:
            positions['secondary'] = 0.0

        positions['tilt'] = 0.0
        positions['velocity'] = 0.0
        data['positions'] = positions

        self.logger.debug("shade V2: Return data={}".format(data))
        return data

    def shadeIds(self, hubHostname):
        shadesUrl = 'http://%s/api/shades/' % hubHostname

        data = self.get(shadesUrl)
        if data == '':
            return []

        return data['shadeIds']

    @staticmethod
    def to_percent(pos, divr=1.0):
        return math.trunc((float(pos) / divr * 100.0) + 0.5)

    def do_get(self, url, *param, **kwargs) -> requests.Response:
        '''This method exists to make it easier to test the plugin.'''
        return requests.get(url, *param, **kwargs)

    def get(self, url) -> dict:
        try:
            res = self.do_get(url, headers={'accept': 'application/json'})
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"Error fetching {url}", exc_info=True)
            self.logger.debug(
                f"    Get from '{url}' returned {'n/a' if not res else res.status_code}, response body '{'n/a' if not res else res.text}'")
            return {}

        if res and res.status_code != requests.codes.ok:
            self.logger.error(f"Unexpected response fetching {url}: {res.status_code}")
            self.logger.debug(f"    Get from '{url}' returned {res.status_code}, response body '{res.text}'")
            return {}

        response = res.json()
        return response

    def put(self, url, data=None) -> dict:
        try:
            if data:
                res = requests.put(url, json=data, headers={'accept': 'application/json'})
            else:
                res = requests.put(url, headers={'accept': 'application/json'})

        except requests.exceptions.RequestException as e:
            self.logger.exception(f"Error in put {url} with data {data}:", exc_info=True)
            self.logger.debug(
                f"    Get from '{url}' returned {'n/a' if not res else res.status_code}, response body '{'n/a' if not res else res.text}'")
            return {}

        if res and res.status_code != requests.codes.ok:
            self.logger.error('Unexpected response in put %s: %s' % (url, str(res.status_code)))
            self.logger.debug(f"    Get from '{url}' returned {res.status_code}, response body '{res.text}'")
            return {}

        response = res.json()
        return response