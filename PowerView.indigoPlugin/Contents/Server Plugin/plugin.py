#!/usr/bin/env python
# coding: utf-8

import base64
import indigo
from powerview import *

class Plugin(indigo.PluginBase):
    def __init__(self, pluginId, pluginDisplayName, pluginVersion,
                 pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)

        self.debug = pluginPrefs.get('debug', False)

        self.devices = {}

        self.powerview = PowerView()

    def activateScene(self, action):
        hub = indigo.devices[action.deviceId]
        sceneId = action.props['sceneId']

        self.debugLog('activate scene %s on hub %s' % (sceneId, hub.address))

        activateSceneUrl = \
                'http://%s/api/scenes?sceneid=%s' % (hub.address, sceneId)

        self.powerview.getJSON(activateSceneUrl)

    def activateSceneCollection(self, action):
        hub = indigo.devices[action.deviceId]
        sceneCollectionId = action.props['sceneCollectionId']

        self.debugLog('activate scene collection %s on hub %s' % (sceneCollectionId, hub.address))

        activateSceneCollectionUrl = \
                'http://%s/api/scenecollections?scenecollectionid=%s' % (hub.address, sceneCollectionId)

        self.powerview.getJSON(activateSceneCollectionUrl)

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

        response = self.powerview.getJSON(shadesUrl)

        shadeIds = response['shadeIds']

        for shadeId in shadeIds:
            self.createShade(hub.address, shadeId)

    def updateShade(self, shade):
        self.debugLog('Updating shade %s' % shade.address)

        if shade.address == '':
            return

        hubHostname, shadeId = shade.address.split(':')

        data = self.powerview.shadeData(hubHostname, shadeId)
        data.pop('name') # don't overwrite local changes

        for key, value in data.iteritems():
            shade.updateStateOnServer(key, value)

    def createShade(self, hubHostname, shadeId):
        address = '%s:%s' % (hubHostname, shadeId)

        if self.findShade(address):
            self.debugLog('Shade %s already exists' % address)

            return;

        self.debugLog('Creating shade %s' % address)

        data = self.powerview.shadeData(hubHostname, shadeId)
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

    def listSceneCollections(self, filter="", valuesDict="", type="", targetId=0):
        hub = self.devices[targetId]

        data = self.powerview.sceneCollections(hub.address)

        list = []

        for sceneCollection in data:
            list.append([sceneCollection['id'], sceneCollection['name']])

        list = sorted(list, key=lambda pair: pair[1])

        return list

    def listScenes(self, filter="", valuesDict="", type="", targetId=0):
        hub = self.devices[targetId]

        scenes = self.powerview.scenes(hub.address)

        list = []

        for scene in scenes:
            list.append([scene['id'], scene['name']])

        list = sorted(list, key=lambda pair: pair[1])

        return list

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

        self.powerview.putJSON(shadeUrl, body)
