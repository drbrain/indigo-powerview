import base64
import logging
import requests

class PowerView:

    logger = logging.getLogger('Plugin')

    def activateScene(self, hubHostname, sceneId):
        activateSceneUrl = 'http://%s/api/scenes?sceneId=%s' % (hubHostname, sceneId)

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

    def stopShade(self, hubHostname, shadeId):
        self.logger.error('Stop Shade function is not available on Generation 2 gateway.')
        pass

    def room(self, hubHostname, roomId):
        roomUrl = 'http://%s/api/rooms/%s' % (hubHostname, roomId)

        data = self.__GET(roomUrl)['room']

        data['name'] = base64.b64decode(data.pop('name'))

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

        data = self.__GET(scenesURL)['sceneData']

        for scene in data:
            name = base64.b64decode(scene.pop('name'))

            room = self.room(hubHostname, scene['roomId'])

            scene['name'] = '%s - %s' % (room['name'], name)

        return data

    def sceneCollections(self, hubHostname):
        sceneCollectionsUrl = \
                'http://%s/api/scenecollections/' % (hubHostname)

        data = self.__GET(sceneCollectionsUrl)['sceneCollectionData']

        for sceneCollection in data:
            sceneCollection['name'] = \
                    base64.b64decode(sceneCollection.pop('name'))

        return data

    def shade(self, hubHostname, shadeId):
        shadeUrl = 'http://%s/api/shades/%s' % (hubHostname, shadeId)

        data = self.__GET(shadeUrl)['shade']
        data.pop('id')

        data['name'] = base64.b64decode(data.pop('name'))
        data['batteryLevel'] = data.pop('batteryStrength')
        data['capabilities'] = 7  # Gen3 property defaults to "Type 7 - Top-Down/Bottom-Up"
        if 'positions' in data:
            if 'posKind1' in data['positions']:
                data['positions'].update(primary=(data['positions']['position1']/65535),
                                      secondary=(data['positions']['position2']/65535), tilt=0.0, velocity=0.0)
        return data

    def shadeIds(self, hubHostname):
        shadesUrl = 'http://%s/api/shades/' % hubHostname

        data = self.__GET(shadesUrl)

        return data['shadeIds']

    def __GET(self, url) -> dict:
        try:
            f = requests.get(url)
        except requests.exceptions.RequestException as e:
            self.logger.exception('Error fetching %s: %s' % (url))
            return {}

        self.logger.debug("Get returned {} from '{}'".format(f.status_code, url))
        if f.status_code != requests.codes.ok:
            self.logger.error('Unexpected response fetching %s: %s' % (url, str(f.status_code)))
            return {}

        response = f.json()
        self.logger.debug("Get response body '{}'".format(response))

        return response

    def __PUT(self, url, data=None) -> dict:

        try:
            if data:
                # data = {'positions':data}
                res = requests.put(url, json=data)
            else:
                res = requests.put(url)

        except requests.exceptions.RequestException as e:
            self.logger.exception("Error in put {} with data {}:".format(url, data))
            return {}

        self.logger.debug("Put returned {} from '{}'".format(res.status_code, url))
        if res.status_code != requests.codes.ok:
            self.logger.error('Unexpected response in put %s: %s' % (url, str(res.status_code)))
            return {}

        response = res.json()
        self.logger.debug("Put response body '{}'".format(response))

        return response
