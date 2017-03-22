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

        self.deviceList = []

    def deviceStartComm(self, device):
        if device.id not in self.deviceList:
            self.update(device)
            self.deviceList.append(device.id)

    def deviceStopComm(self, device):
        if device.id in self.deviceList:
            self.deviceList.remove(device.id)

    def update(self, device):
        if device.deviceTypeId == 'PowerViewHub':
            self.updateHub(device)
        elif device.deviceTypeId == 'PowerViewShade':
            self.updateShade(device)

    def updateHub(self, hub):
        state       = []

        self.debugLog('Updating hub ' + hub.address)

        apiUrl = 'http://' + hub.address + '/api/'

        roomsUrl            = apiUrl + 'rooms'
        scenesUrl           = apiUrl + 'scenes'
        scenecollectionsUrl = apiUrl + 'scenecollections'
        shadesUrl           = apiUrl + 'shades'

        response = self.getJSON(roomsUrl)

        roomIds = response['roomIds']

        state.append({'key': 'roomCount', 'value': len(roomIds)})

        response = self.getJSON(scenesUrl)

        sceneIds = response['sceneIds']

        state.append({'key': 'sceneCount', 'value': len(sceneIds)})

        response = self.getJSON(scenecollectionsUrl)

        sceneCollectionIds = response['sceneCollectionIds']

        state.append({'key': 'sceneCollectionCount', 'value': len(sceneCollectionIds)})

        response = self.getJSON(shadesUrl)

        shadeIds = response['shadeIds']

        state.append({'key': 'shadeCount', 'value': len(shadeIds)})

        hub.updateStatesOnServer(state)

        for shadeId in shadeIds:
            self.createShade(hub.address, shadeId)

    def updateShade(self, shade):
        self.debugLog('Updating shade ' + shade.address)

        if shade.address == '':
            return

        hubHostname, shadeId = shade.address.split(':')

        shadeProps = self.getShadeData(hubHostname, str(shadeId))
        shadeProps.pop('name') # don't overwrite local changes

        batteryLevel = shadeProps.pop('batteryLevel')

        shade.replacePluginPropsOnServer(shadeProps)

        shade.updateStateOnServer('batteryLevel', batteryLevel)

    def createShade(self, hubHostname, shadeId):
        address = hubHostname + ':' + str(shadeId)

        props = self.getShadeData(hubHostname, str(shadeId))
        name = props.pop('name')

        self.debugLog('Creating shade ' + address)

        indigo.device.create(
                protocol = indigo.kProtocol.Plugin,
                address = address,
                deviceTypeId = 'PowerViewShade',
                name = name,
                props = props)

    def getJSON(self, url):
        try:
            f = urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            self.errorLog('Error fetching %s: %s' % (url, str(e)))
            return;

        response = json.load(f)

        f.close()

        return response

    def getShadeData(self, hubHostname, shadeId):
        shadeUrl = 'http://' + hubHostname + '/api/shades/' + shadeId

        shadeProps = self.getJSON(shadeUrl)['shade']
        shadeProps.pop('id')

        shadeProps['name']    = base64.b64decode(shadeProps.pop('name'))
        shadeProps['address'] = hubHostname + ':' + str(shadeId)
        shadeProps['batteryLevel'] = shadeProps.pop('batteryStrength')

        if 'positions' in shadeProps:
            shadePositions = shadeProps.pop('positions')

            shadeProps.update(shadePositions)

        return shadeProps
