import base64
import ujson as json
import requests


# import simplejson as json -- replaced by ujson provided by indigo
# import requests2


class PowerViewGen3:
    URL_ROOM_ = 'http://{h}/home/rooms/{id}'
    URL_SHADES_ = 'http://{h}/home/shades/{id}'
    URL_SHADES_MOTION_ = 'http://{h}/home/shades/{id}/motion'
    URL_SHADES_POSITIONS_ = 'http://{h}/home/shades/positions?ids={id}'
    URL_SCENES_ = 'http://{h}/home/scenes/{id}'
    URL_SCENES_ACTIVATE = 'http://{h}/home/scenes/{id}/activate'

    # URL_SCENECOLLECTIONS_ = 'http://%s/home/scenecollections/'

    def __init__(self, logger):
        self.logger = logger

    def activateScene(self, hubHostname, sceneId):
        activateSceneUrl = self.URL_SCENES_.format(h=hubHostname, id=sceneId)

        self.__GET(activateSceneUrl)

    # def activateSceneCollection(self, hubHostname, sceneCollectionId):
    #     activateSceneCollectionUrl = self.URL_SCENECOLLECTIONS_ % (hubHostname, sceneCollectionId)
    #
    #     self.__GET(activateSceneCollectionUrl)

    def calibrateShade(self, hubHostname, shadeId):
        pass
        # shadeUrl = self.URL_SHADES_MOTION_.format(h=hubHostname, id=shadeId)
        # body = {
        #     "motion": "calibrate"
        # }
        # self.__PUT(shadeUrl, body)

    def jogShade(self, hubHostname, shadeId):
        shadeUrl = self.URL_SHADES_MOTION_.format(h=hubHostname, id=shadeId)

        body = {
            "motion": "jog"
        }

        self.__PUT(shadeUrl, body)

    def room(self, hubHostname, roomId):
        roomUrl = self.URL_ROOM_.format(h=hubHostname, id=roomId)

        data = self.__GET(roomUrl)

        data['name'] = base64.b64decode(data.pop('name'))

        return data

    def setShadePosition(self, hubHostname, shadeId, top, bottom):
        shadeUrl = self.URL_SHADES_POSITIONS_.format(h=hubHostname, id=shadeId)

        body = {
            "positions": {
                "primary": bottom,
                "secondary": top,
            }
        }

        self.__PUT(shadeUrl, body)

    def scenes(self, hubHostname):
        scenesURL = self.URL_SCENES_.format(h=hubHostname, id='')

        data = self.__GET(scenesURL)

        for scene in data:
            name = base64.b64decode(scene.pop('name'))
            room = self.room(hubHostname, scene['roomIds'][0])
            scene['name'] = '%s - %s' % (room['name'], name)

        return data

    # def sceneCollections(self, hubHostname):
    #     sceneCollectionsUrl = \
    #         self.URL_SCENECOLLECTIONS_ % (hubHostname)
    #
    #     data = self.__GET(sceneCollectionsUrl)['sceneCollectionData']
    #
    #     for sceneCollection in data:
    #         sceneCollection['name'] = \
    #                 base64.b64decode(sceneCollection.pop('name'))
    #
    #     return data

    def shade(self, hubHostname, shadeId):
        shadeUrl = self.URL_SHADES_.format(h=hubHostname, id=shadeId)

        data = self.__GET(shadeUrl)
        data.pop('id')

        data['name'] = base64.b64decode(data.pop('name'))
        if 'batteryStrength' in data:
            data['batteryLevel'] = data.pop('batteryStrength')
        else:
            data['batteryLevel'] = 'unk'

        if 'positions' in data:
            shadePositions = data.pop('positions')

            data.update(shadePositions)

        return data

    def shades(self, hubHostname):
        shadesUrl = self.URL_SHADES_.format(h=hubHostname, id='')

        data = self.__GET(shadesUrl)

        return data

    def __GET(self, url):
        try:
            f = requests.get(url)
        except requests.exceptions.RequestException as e:
            self.logger.error('Error fetching %s: %s' % (url, str(e)))
            return
        if f.status_code != requests.codes.ok:
            self.logger.error('Unexpected response fetching %s: %s' % (url, str(f.status_code)))
            return

        response = f.json()

        return response

    def __PUT(self, url, data):
        body = json.dumps(data)

        try:
            f = requests.put(url, json=data)
        except requests.exceptions.RequestException as e:
            self.logger.error('Error in put %s: %s' % (url, str(e)))
            return
        if f.status_code != requests.codes.ok:
            self.logger.error('Unexpected response in put %s: %s' % (url, str(f.status_code)))
            return

        response = f.json()

        return response
