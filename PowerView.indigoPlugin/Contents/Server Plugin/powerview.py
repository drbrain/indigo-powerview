import base64
import simplejson as json
import urllib2

class PowerView:
    def activateScene(self, hubHostname, sceneId):
        activateSceneUrl = \
                'http://%s/api/scenes?sceneid=%s' % (hubHostname, sceneId)

        self.getJSON(activateSceneUrl)

    def activateSceneCollection(self, hubHostname, sceneCollectionId):
        activateSceneCollectionUrl = \
                'http://%s/api/scenecollections?scenecollectionid=%s' % (hubHostname, sceneCollectionId)

        self.getJSON(activateSceneCollectionUrl)

    def getJSON(self, url):
        try:
            f = urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            self.errorLog('Error fetching %s: %s' % (url, str(e)))
            return;

        response = json.load(f)

        f.close()

        return response

    def putJSON(self, url, data):
        body = json.dumps(data)

        request = urllib2.Request(url, data=body)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: "PUT"

        opener = urllib2.build_opener(urllib2.HTTPHandler)

        try:
            f = opener.open(request)
        except urllib2.HTTPError, e:
            self.errorLog('Error fetching %s: %s' % (url, str(e)))
            return;

        response = json.load(f)

        f.close()

        return response

    def roomData(self, hubHostname, roomId):
        roomUrl = 'http://%s/api/rooms/%s' % (hubHostname, roomId)

        data = self.getJSON(roomUrl)['room']

        data['name'] = base64.b64decode(data.pop('name'))

        return data

    def scenes(self, hubHostname):
        scenesURL = 'http://%s/api/scenes/' % (hubHostname)

        data = self.getJSON(scenesURL)['sceneData']

        for scene in data:
            name = base64.b64decode(scene.pop('name'))

            room = self.roomData(hubHostname, scene['roomId'])

            scene['name'] = '%s - %s' % (room['name'], name)

        return data

    def sceneCollections(self, hubHostname):
        sceneCollectionsUrl = \
                'http://%s/api/scenecollections/' % (hubHostname)

        data = self.getJSON(sceneCollectionsUrl)['sceneCollectionData']

        for sceneCollection in data:
            sceneCollection['name'] = \
                    base64.b64decode(sceneCollection.pop('name'))

        return data

    def shadeData(self, hubHostname, shadeId):
        shadeUrl = 'http://%s/api/shades/%s' % (hubHostname, shadeId)

        data = self.getJSON(shadeUrl)['shade']
        data.pop('id')

        data['name']         = base64.b64decode(data.pop('name'))
        data['batteryLevel'] = data.pop('batteryStrength')

        if 'positions' in data:
            shadePositions = data.pop('positions')

            data.update(shadePositions)

        return data

