#!/usr/bin/env python
# coding: utf-8

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
        state       = []
        hubHostname = device.pluginProps[u'hubHostname']

        self.debugLog(u'Updating ' + hubHostname)

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

        device.updateStatesOnServer(state)

    def getJSON(self, url):
        try:
            f = urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            self.errorLog(u'Error fetching %s: %s' % (url, str(e)))
            return;

        response = json.load(f)

        f.close()

        return response
