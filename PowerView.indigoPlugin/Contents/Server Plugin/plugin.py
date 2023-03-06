#!/usr/bin/env python
# coding: utf-8

import base64
import indigo
import requests

from powerview import *
from powerview3 import *


class Plugin(indigo.PluginBase):
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.DEBUG_SERVER_IP = "10.10.28.191"  # IP address of the Mac running PyCharm
        super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

        self.devices = {}
        self.debug = pluginPrefs.get('debug', False)
        self.powerview = None

    def getPV(self, hub_address):
        """ Detects and returns the correct powerview class, based on how the gateway responds."""

        if self.powerview is None:
            home = requests.get("http://{}/home".format(hub_address))
            if home.status_code == requests.codes.ok:
                self.powerview = PowerViewGen3(self.logger)
            else:
                home = requests.get("http://{}/api/fwversion".format(hub_address))
                if home.status_code == requests.codes.ok:
                    self.powerview = PowerView(self.logger)
                else:
                    raise KeyError("Invalid hub address ({})".format(hub_address))

        return self.powerview

    def activateScene(self, action):
        hub = indigo.devices[action.deviceId]
        sceneId = action.props['sceneId']

        self.debugLog('activate scene %s on hub %s' % (sceneId, hub.address))

        self.getPV(hub.address).activateScene(hub.address, sceneId)

    def activateSceneCollection(self, action):
        hub = indigo.devices[action.deviceId]
        sceneCollectionId = action.props['sceneCollectionId']

        self.debugLog('activate scene collection %s on hub %s' % (sceneCollectionId, hub.address))

        self.getPV(hub.address).activateSceneCollection(hub.address, sceneCollectionId)

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
        response = self.getPV(address).shades(address)
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

        data = self.getPV(hubHostname).shade(hubHostname, shadeId)
        data.pop('name')  # don't overwrite local changes

        # update the shade state for items in the device.
        # PV2 hubs have at least one additional data item
        # (signalStrengh) not in the device definition
        for key in data.keys():
            if key in shade.states:
                shade.updateStateOnServer(key, data[key])

    def createShade(self, hubHostname, shadeId):
        address = '%s:%s' % (hubHostname, shadeId)

        if self.findShade(address):
            self.debugLog('Shade %s already exists' % address)

            return

        self.debugLog('Creating shade %s' % address)

        data = self.getPV(hubHostname).shade(hubHostname, shadeId)
        name = data.pop('name')

        self.debugLog('Creating shade %s' % address)

        indigo.device.create(
            protocol=indigo.kProtocol.Plugin,
            address=address,
            deviceTypeId='PowerViewShade',
            name=name)

    def findShade(self, address):
        for device in indigo.devices.values():
            if device.deviceTypeId == 'PowerViewShade' and device.address == address:
                return device

        return None

    def calibrateShade(self, action):
        shade = indigo.devices[action.deviceId]

        self.debugLog('Calibrating shade %s' % (action.deviceId))

        hubHostname, shadeId = shade.address.split(':')

        self.getPV(hubHostname).calibrateShade(hubHostname, shadeId)

    def jogShade(self, action):
        shade = indigo.devices[action.deviceId]

        self.debugLog('Jogging shade %s' % action.deviceId)

        hubHostname, shadeId = shade.address.split(':')

        self.getPV(hubHostname).jogShade(hubHostname, shadeId)

    def listSceneCollections(self, filter="", valuesDict="", type="", targetId=0):
        hub = self.devices[targetId]

        data = self.getPV(hub.address).sceneCollections(hub.address)

        list = []

        for sceneCollection in data:
            list.append([sceneCollection['id'], sceneCollection['name']])

        list = sorted(list, key=lambda pair: pair[1])

        return list

    def listScenes(self, filter="", valuesDict="", type="", targetId=0):
        hub = self.devices[targetId]

        scenes = self.getPV(hub.address).scenes(hub.address)

        list = []

        for scene in scenes:
            list.append([scene['id'], scene['name']])

        list = sorted(list, key=lambda pair: pair[1])

        return list

    def setShadePosition(self, action):
        shade = indigo.devices[action.deviceId]
        top = action.props.get('top', '')
        bottom = action.props.get('bottom', '')

        self.debugLog('Setting position of %s top: %s, bottom: %s' % (action.deviceId, top, bottom))

        hubHostname, shadeId = shade.address.split(':')

        self.getPV(hubHostname).setShadePosition(hubHostname, shadeId, top, bottom)
