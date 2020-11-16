#!/usr/bin/env python
# coding: utf-8

import logging
import base64
import socket

from powerview import *

class Plugin(indigo.PluginBase):

    # delay between loop steps (in seconds)
    threadLoopDelay = 60

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

    def closedDeviceConfigUi(self, values, canceled, typeId, devId):
        if canceled: return

        dev = indigo.devices[devId]
        self.update(dev)

    def validateActionConfigUi(self, values, typeId, devId):
        errors = indigo.Dict()

        # TODO verify that values are the correct type and range

        if (typeId == 'setShadePosition'):
            shade = indigo.devices[devId]
            topPos = int(values.get('top', 0))
            bottomPos = int(values.get('bottom', 0))
            values['description'] = 'move %s to %d/%d' % (shade.name, topPos, bottomPos)

        return ((len(errors) == 0), values, errors)

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

    def update(self, device):
        if device.deviceTypeId == 'PowerViewHub':
            self.updateHub(device)
        elif device.deviceTypeId == 'PowerViewShade':
            self.updateShade(device)

    def updateHub(self, hub):
        self.logger.debug('Updating hub %s', hub.address)

        data = self.powerview.userdata(hub.address)

        if data is not None:
            hub.updateStateOnServer('active', True)
            hub.updateStateOnServer('status', 'Active')

            for key, value in data.iteritems():
                if key in hub.states:
                    hub.updateStateOnServer(key, value)
        else:
            hub.updateStateOnServer('active', False)
            hub.updateStateOnServer('status', 'Inactive')

    def updateShade(self, shade):
        hubId = shade.pluginProps.get('hubId')
        if hubId is None: return
        hub = indigo.devices[int(hubId)]

        self.logger.debug('Updating shade %s:%s', hub.address, shade.address)

        data = self.powerview.shade(hub.address, shade.address)
        if data is None: return

        data.pop('name') # don't overwrite local changes

        # update the shade state for items in the device.
        # PV2 hubs have at least one additional data item
        # (signalStrengh) not in the device definition
        for key, value in data.iteritems():
            if key in shade.states:
                shade.updateStateOnServer(key, value)

        # update battery level (3.0 is "max" status level)
        batt = data.get('batteryStatus')
        if batt is not None:
            batteryLevel = (int(batt) / 3.0) * 100
            shade.updateStateOnServer('batteryLevel', batteryLevel)

    def runConcurrentThread(self):
        self.logger.debug(u'Thread Started')

        try:
            while not self.stopThread:
                # devices are updated when the plugin first loads,
                # so start with a sleep then update all devices
                self.sleep(self.threadLoopDelay)
                self.refreshAllDevices()

        except self.StopThread:
            pass

        self.logger.debug(u'Thread Stopped')

    def refreshAllDevices(self):
        self.logger.debug(u'refreshing all devices')

        # update all enabled and configured devices
        for deviceId in self.devices:
            device = self.devices[deviceId]
            if (device.enabled and device.configured):
                self.update(device)

    def calibrateShade(self, action):
        shade = indigo.devices[action.deviceId]

        self.logger.info('Calibrating shade %s', action.deviceId)

        hubId = shade.pluginProps['hubId']
        hub = indigo.devices[int(hubId)]

        self.powerview.calibrateShade(hub.address, shade.address)

    def jogShade(self, action):
        shade = indigo.devices[action.deviceId]

        self.logger.info('Jogging shade %s', action.deviceId)

        hubId = shade.pluginProps['hubId']
        hub = indigo.devices[int(hubId)]

        self.powerview.jogShade(hub.address, shade.address)

    def nullConfigCallback(self, filter="", valuesDict="", type="", targetId=0):
        # this method triggers a callback from a config UI, which allows any dynamic
        # lists to repopulate - used mostly for selecting a hub / shade combo
        pass

    def listSceneCollections(self, filter="", valuesDict="", type="", targetId=0):
        hub = indigo.devices[targetId]

        data = self.powerview.sceneCollections(hub.address)

        list = []

        for sceneCollection in data:
            list.append([sceneCollection['id'], sceneCollection['name']])

        list = sorted(list, key=lambda pair: pair[1])

        return list

    def listWindowShades(self, filter="", valuesDict="", type="", targetId=0):
        list = []

        hubId = valuesDict.get('hubId')
        if hubId is None: return list

        hub = indigo.devices[int(hubId)]

        self.logger.debug("Querying shades from %s", hub.name)
        data = self.powerview.shades(hub.address)

        for shade in data:
            list.append([shade['id'], shade['name']])

        list = sorted(list, key=lambda pair: pair[1])

        return list

    def listScenes(self, filter="", valuesDict="", type="", targetId=0):
        hub = indigo.devices[targetId]

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

        hubId = shade.pluginProps['hubId']
        hub = indigo.devices[int(hubId)]

        self.powerview.setShadePosition(hub.address, shade.address, top, bottom)
