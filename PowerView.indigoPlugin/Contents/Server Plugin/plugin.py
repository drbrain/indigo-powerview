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

        self.powerview.activateScene(hub.address, sceneId)

    def activateSceneCollection(self, action):
        hub = indigo.devices[action.deviceId]
        sceneCollectionId = action.props['sceneCollectionId']

        self.debugLog('activate scene collection %s on hub %s' % (sceneCollectionId, hub.address))

        self.powerview.activateSceneCollection(hub.address, sceneCollectionId)

    def deviceStartComm(self, device):
        if device.id not in self.devices:
            self.devices[device.id] = device
            self.update(device)

    def deviceStopComm(self, device):
        if device.id in self.devices:
            self.devices.pop(device.id)

    def discoverShades(self, valuesDict, typeId, deviceId):
        address = valuesDict['address']

        self.debugLog('Discovering shades on %s' % address)

        response = self.powerview.shades(address)

        shadeIds = response['shadeIds']

        for shadeId in shadeIds:
            self.createShade(address, shadeId)

    def update(self, device):
        if device.deviceTypeId == 'PowerViewShade':
            self.updateShade(device)

    def updateShade(self, shade):
        self.debugLog('Updating shade %s' % shade.address)

        if shade.address == '':
            return

        hubHostname, shadeId = shade.address.split(':')

        data = self.powerview.shade(hubHostname, shadeId)
        data.pop('name') # don't overwrite local changes

        # update the shade state for items in the device.
        # PV2 hubs have at least one additional data item
        # (signalStrengh) not in the device definition
        for key, value in data.iteritems():
            if key in shade.states:
                shade.updateStateOnServer(key, value)

    def createShade(self, hubHostname, shadeId):
        address = '%s:%s' % (hubHostname, shadeId)

        if self.findShade(address):
            self.debugLog('Shade %s already exists' % address)

            return;

        self.debugLog('Creating shade %s' % address)

        data = self.powerview.shade(hubHostname, shadeId)
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

    def calibrateShade(self, action):
        shade = indigo.devices[action.deviceId]

        self.debugLog('Calibrating shade %s' % (action.deviceId))

        hubHostname, shadeId = shade.address.split(':')

        self.powerview.calibrateShade(hubHostname, shadeId)

    def jogShade(self, action):
        shade = indigo.devices[action.deviceId]

        self.debugLog('Jogging shade %s' % (action.deviceId))

        hubHostname, shadeId = shade.address.split(':')

        self.powerview.jogShade(hubHostname, shadeId)

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

        self.powerview.setShadePosition(hubHostname, shadeId, top, bottom)
