#!/usr/bin/env python
# coding: utf-8

import logging
import base64
import socket

from powerview import *

class Plugin(indigo.PluginBase):
    def __init__(self, pluginId, pluginDisplayName, pluginVersion,
                 pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)

        self.loadPluginPrefs(pluginPrefs)

        self.devices = {}

        self.powerview = PowerView()

    def closedPrefsConfigUi(self, prefs, canceled):
        if canceled: return
        self.loadPluginPrefs(prefs)

    def loadPluginPrefs(self, prefs):
        self.logLevel = int(prefs.get('logLevel', 20))
        self.indigo_log_handler.setLevel(self.logLevel)

        sockTimeout = int(prefs.get('connectionTimeout', 5))
        socket.setdefaulttimeout(sockTimeout)

    def activateScene(self, action):
        hub = indigo.devices[action.deviceId]
        sceneId = action.props['sceneId']

        self.logger.debug('activate scene %s on hub %s', sceneId, hub.address)

        self.powerview.activateScene(hub.address, sceneId)

    def activateSceneCollection(self, action):
        hub = indigo.devices[action.deviceId]
        sceneCollectionId = action.props['sceneCollectionId']

        self.logger.debug('activate scene collection %s on hub %s', sceneCollectionId, hub.address)

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

        self.logger.debug('Discovering shades on %s', address)

        response = self.powerview.shades(address)

        shadeIds = response['shadeIds']

        for shadeId in shadeIds:
            self.createShade(address, shadeId)

    def update(self, device):
        if device.deviceTypeId == 'PowerViewShade':
            self.updateShade(device)

    def updateShade(self, shade):
        self.logger.debug('Updating shade %s', shade.address)

        if shade.address == '':
            return

        hubHostname, shadeId = shade.address.split(':')

        data = self.powerview.shade(hubHostname, shadeId)
        data.pop('name') # don't overwrite local changes

        for key, value in data.iteritems():
            shade.updateStateOnServer(key, value)

    def createShade(self, hubHostname, shadeId):
        address = '%s:%s' % (hubHostname, shadeId)

        if self.findShade(address):
            self.logger.debug('Shade %s already exists', address)
            return;

        data = self.powerview.shade(hubHostname, shadeId)
        name = data.pop('name')

        self.logger.debug('Creating shade %s [%s]', name, address)

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

        self.logger.info('Calibrating shade %s', action.deviceId)

        hubHostname, shadeId = shade.address.split(':')

        self.powerview.calibrateShade(hubHostname, shadeId)

    def jogShade(self, action):
        shade = indigo.devices[action.deviceId]

        self.logger.info('Jogging shade %s', action.deviceId)

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

        self.logger.info('Moving shade - %s [%s | %s]', shade.name, top, bottom)

        hubHostname, shadeId = shade.address.split(':')

        self.powerview.setShadePosition(hubHostname, shadeId, top, bottom)
