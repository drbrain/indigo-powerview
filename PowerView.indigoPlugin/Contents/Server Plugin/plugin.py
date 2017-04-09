#!/usr/bin/env python
# coding: utf-8

import base64
import indigo
import simplejson as json
import urllib2

class Plugin(indigo.PluginBase):
    def __init__(self, pluginId, pluginDisplayName, pluginVersion,
                 pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)

        self.debug = pluginPrefs.get('debug', False)

        self.devices = {}

    def activateScene(self, action):
        hub = indigo.devices[action.deviceId]
        sceneId = action.props['sceneId']

        self.debugLog('activate scene %s on hub %s' % (sceneId, hub.address))

        activateSceneUrl = \
                'http://%s/api/scenes?sceneid=%s' % (hub.address, sceneId)

        self.getJSON(activateSceneUrl)

    def activateSceneCollection(self, action):
        hub = indigo.devices[action.deviceId]
        sceneCollectionId = action.props['sceneCollectionId']

        self.debugLog('activate scene collection %s on hub %s' % (sceneCollectionId, hub.address))

        activateSceneCollectionUrl = \
                'http://%s/api/scenecollections?scenecollectionid=%s' % (hub.address, sceneCollectionId)

        self.getJSON(activateSceneCollectionUrl)

    def deviceStartComm(self, device):
        if device.id not in self.devices:
            self.devices[device.id] = device
            self.update(device)

    def deviceStopComm(self, device):
        if device.id in self.devices:
            self.devices.pop(device.id)

    def update(self, device):
        if device.deviceTypeId == 'PowerViewHub':
            self.updateHub(device)
        elif device.deviceTypeId == 'PowerViewShade':
            self.updateShade(device)

    def updateHub(self, hub):
        state       = []

        self.debugLog('Updating hub %s' % hub.address)

        shadesUrl = 'http://%s/api/shades/' % hub.address

        response = self.getJSON(shadesUrl)

        shadeIds = response['shadeIds']

        for shadeId in shadeIds:
            self.createShade(hub.address, shadeId)

    def updateShade(self, shade):
        self.debugLog('Updating shade %s' % shade.address)

        if shade.address == '':
            return

        hubHostname, shadeId = shade.address.split(':')

        data = self.getShadeData(hubHostname, str(shadeId))
        data.pop('name') # don't overwrite local changes

        for key, value in data.iteritems():
            shade.updateStateOnServer(key, value)

    def createShade(self, hubHostname, shadeId):
        address = '%s:%s' % (hubHostname, shadeId)

        if self.findShade(address):
            return;

        data = self.getShadeData(hubHostname, str(shadeId))
        name = data.pop('name')

        self.debugLog('Creating shade %s' % address)

        indigo.device.create(
                protocol = indigo.kProtocol.Plugin,
                address = address,
                deviceTypeId = 'PowerViewShade',
                name = name)

    def findShade(self, address):
        for device in indigo.devices.itervalues():
            if device.deviceTypeId == 'PowerViewShade' and device.address == address:
               return device

        return None

    def getJSON(self, url):
        try:
            f = urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            self.errorLog('Error fetching %s: %s' % (url, str(e)))
            return;

        response = json.load(f)

        f.close()

        return response

    def getRoomData(self, hubHostname, roomId):
        roomUrl = 'http://%s/api/rooms/%s' % (hubHostname, roomId)

        data = self.getJSON(roomUrl)['room']

        return data

    def getShadeData(self, hubHostname, shadeId):
        shadeUrl = 'http://%s/api/shades/%s' % (hubHostname, shadeId)

        data = self.getJSON(shadeUrl)['shade']
        data.pop('id')

        data['name']    = base64.b64decode(data.pop('name'))
        data['batteryLevel'] = data.pop('batteryStrength')

        if 'positions' in data:
            shadePositions = data.pop('positions')

            data.update(shadePositions)

        return data

    def listSceneCollections(self, filter="", valuesDict="", type="", targetId=0):
        hub = self.devices[targetId]

        sceneCollectionsUrl = \
                'http://%s/api/scenecollections/' % (hub.address)

        data = self.getJSON(sceneCollectionsUrl)['sceneCollectionData']

        list = []

        for sceneCollection in data:
            name = base64.b64decode(sceneCollection['name'])

            list.append([sceneCollection['id'], name])

        list = sorted(list, key=lambda pair: pair[1])

        return list

    def listScenes(self, filter="", valuesDict="", type="", targetId=0):
        hub = self.devices[targetId]

        scenesURL = 'http://%s/api/scenes/' % (hub.address)

        data = self.getJSON(scenesURL)['sceneData']

        list = []

        for scene in data:
            room = self.getRoomData(hub.address, scene['roomId'])

            roomName  = base64.b64decode(room['name'])
            sceneName = base64.b64decode(scene['name'])

            list.append([scene['id'], '%s - %s' % (roomName, sceneName)])

        list = sorted(list, key=lambda pair: pair[1])

        return list

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

    def setShadePosition(self, action):
        shade  = indigo.devices[action.deviceId]
        top    = action.props.get('top',    '')
        bottom = action.props.get('bottom', '')

        self.debugLog('Setting position of %s top: %s, bottom: %s' % (action.deviceId, top, bottom))

        hubHostname, shadeId = shade.address.split(':')

        shadeUrl = 'http://%s/api/shades/%s' % (hubHostname, shadeId)

        body = {
            'shade': {
                'id': shadeId,
                'positions': {
                    'position1': bottom,
                    'posKind1': 1,
                    'position2': top,
                    'posKind2': 2
                }
            }
        }

        self.putJSON(shadeUrl, body)
