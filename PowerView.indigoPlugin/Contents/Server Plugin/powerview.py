import logging
import base64
import simplejson as json
import urllib2
import threading

# TODO create a util method for getting a URL and return named element or None
# TODO implement a "sanitize" method for handling return data (e.g. B64 decoding)

class PowerView:

    def __init__(self):
        self.logger = logging.getLogger('Plugin.PowerView')
        self.hub_lock = threading.Lock()

    def userdata(self, hubHostname):
        userdataUrl = 'http://%s/api/userdata/' % (hubHostname)

        data = self.__GET(userdataUrl)
        if data is None: return None

        return data.get('userData')

    def activateScene(self, hubHostname, sceneId):
        activateSceneUrl = \
                'http://%s/api/scenes?sceneId=%s' % (hubHostname, sceneId)

        self.__GET(activateSceneUrl)

    def activateSceneCollection(self, hubHostname, sceneCollectionId):
        activateSceneCollectionUrl = \
                'http://%s/api/scenecollections?scenecollectionid=%s' % (hubHostname, sceneCollectionId)

        self.__GET(activateSceneCollectionUrl)

    def calibrateShade(self, hubHostname, shadeId):
        shadeUrl = 'http://%s/api/shades/%s' % (hubHostname, shadeId)

        body = {
            'shade': {
                'motion': 'calibrate'
            }
        }

        self.__PUT(shadeUrl, body)

    def jogShade(self, hubHostname, shadeId):
        shadeUrl = 'http://%s/api/shades/%s' % (hubHostname, shadeId)

        body = {
            'shade': {
                'motion': 'jog'
            }
        }

        self.__PUT(shadeUrl, body)

    def room(self, hubHostname, roomId):
        roomUrl = 'http://%s/api/rooms/%s' % (hubHostname, roomId)

        data = self.__GET(roomUrl)
        if data is None: return
        data = data.pop('room')

        encName = data.pop('name')
        data['name'] = base64.b64decode(encName)

        return data

    def setShadePosition(self, hubHostname, shadeId, top, bottom):
        shadeUrl = 'http://%s/api/shades/%s' % (hubHostname, shadeId)

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

        self.__PUT(shadeUrl, body)

    def scenes(self, hubHostname):
        scenesURL = 'http://%s/api/scenes/' % (hubHostname)

        data = self.__GET(scenesURL)
        if data is None: return
        data = data.pop('sceneData')

        for scene in data:
            encName = scene.pop('name')
            name = base64.b64decode(encName)

            room = self.room(hubHostname, scene['roomId'])

            scene['name'] = '%s - %s' % (room['name'], name)

        return data

    def sceneCollections(self, hubHostname):
        sceneCollectionsUrl = \
                'http://%s/api/scenecollections/' % (hubHostname)

        data = self.__GET(sceneCollectionsUrl)
        if data is None: return
        data = data.pop('sceneCollectionData')

        for sceneCollection in data:
            encName = sceneCollection.pop('name')
            sceneCollection['name'] = base64.b64decode(encName)

        return data

    def shade(self, hubHostname, shadeId):
        shadeUrl = 'http://%s/api/shades/%s' % (hubHostname, shadeId)

        data = self.__GET(shadeUrl)
        if data is None: return
        data = data.pop('shade')

        encName              = data.pop('name')
        data['name']         = base64.b64decode(encName)
        data['batteryLevel'] = data.pop('batteryStrength')

        if 'positions' in data:
            shadePositions = data.pop('positions')
            data.update(shadePositions)

        return data

    def shades(self, hubHostname):
        shadesUrl = 'http://%s/api/shades/' % hubHostname

        data = self.__GET(shadesUrl)
        if data is None: return
        data = data.pop('shadeData')

        for shade in data:
            encName = shade.pop('name')
            shade['name'] = base64.b64decode(encName)

        return data

    def __GET(self, url):
        self.logger.debug('GET %s', url)

        response = None

        with self.hub_lock:
            try:
                f = urllib2.urlopen(url)
                response = json.load(f)
                f.close()
            except urllib2.URLError as err:
                self.logger.error('Error connecting to %s: %s', url, err.reason)

        return response

    def __PUT(self, url, data):
        self.logger.debug('PUT %s', url)
        body = json.dumps(data)

        request = urllib2.Request(url, data=body)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: "PUT"

        response = None

        opener = urllib2.build_opener(urllib2.HTTPHandler)

        with self.hub_lock:
            try:
                f = opener.open(request)
                response = json.load(f)
                f.close()
            except urllib2.URLError as err:
                self.logger.error('Error connecting to %s: %s', url, err.reason)

        return response

