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

        self.debug = pluginPrefs.get(u'debug', False)

        self.deviceList = []

    def deviceStartComm(self, device):
        if device.id not in self.deviceList:
            self.update(device)
            self.deviceList.append(device.id)

    def deviceStopComm(self, device):
        if device.id in self.deviceList:
            self.deviceList.remove(device.id)

    def update(self, device):
        if device.deviceTypeId == u'PowerViewHub':
            self.updateHub(device)
        elif device.deviceTypeId == u'PowerViewShade':
            self.updateShade(device)

    def updateHub(self, hub):
        state       = []
        hubHostname = hub.pluginProps[u'hubHostname']

        self.debugLog(u'Updating hub ' + hubHostname)

        apiUrl = u'http://' + hubHostname + u'/api/'

        roomsUrl            = apiUrl + u'rooms'
        scenesUrl           = apiUrl + u'scenes'
        scenecollectionsUrl = apiUrl + u'scenecollections'
        shadesUrl           = apiUrl + u'shades'

        response = self.getJSON(roomsUrl)

        roomIds = response[u'roomIds']

        state.append({u'key': 'roomCount', u'value': len(roomIds)})

        response = self.getJSON(scenesUrl)

        sceneIds = response[u'sceneIds']

        state.append({u'key': 'sceneCount', u'value': len(sceneIds)})

        response = self.getJSON(scenecollectionsUrl)

        sceneCollectionIds = response[u'sceneCollectionIds']

        state.append({u'key': 'sceneCollectionCount', u'value': len(sceneCollectionIds)})

        response = self.getJSON(shadesUrl)

        shadeIds = response[u'shadeIds']

        state.append({u'key': 'shadeCount', u'value': len(shadeIds)})

        hub.updateStatesOnServer(state)

        for shadeId in shadeIds:
            self.createShade(hubHostname, shadeId)

    def updateShade(self, shade):
        self.debugLog(u'Updating shade ' + shade.address)

        if shade.address == '':
            return

        hubHostname, shadeId = shade.address.split(':')

        shadeProps = self.getShadeData(hubHostname, str(shadeId))
        shadeProps.pop('name') # don't overwrite local changes

        shade.replacePluginPropsOnServer(shadeProps)

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
            self.errorLog(u'Error fetching %s: %s' % (url, str(e)))
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

        if 'positions' in shadeProps:
            shadePositions = shadeProps.pop('positions')

            shadeProps.update(shadePositions)

        return shadeProps
