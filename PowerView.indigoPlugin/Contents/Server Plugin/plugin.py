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

        shadesUrl = apiUrl + 'shades'

        response = self.getJSON(shadesUrl)

        shadeIds = response['shadeIds']

        for shadeId in shadeIds:
            self.createShade(hub.address, shadeId)

        roomsUrl            = apiUrl + 'rooms'
        scenesUrl           = apiUrl + 'scenes'
        scenecollectionsUrl = apiUrl + 'scenecollections'

    def updateShade(self, shade):
        self.debugLog('Updating shade ' + shade.address)

        if shade.address == '':
            return

        hubHostname, shadeId = shade.address.split(':')

        data = self.getShadeData(hubHostname, str(shadeId))
        data.pop('name') # don't overwrite local changes

        for key, value in data.iteritems():
            shade.updateStateOnServer(key, value)

    def createShade(self, hubHostname, shadeId):
        address = hubHostname + ':' + str(shadeId)

        if self.findShade(address):
            return;

        data = self.getShadeData(hubHostname, str(shadeId))
        name = data.pop('name')

        self.debugLog('Creating shade ' + address)

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

    def getShadeData(self, hubHostname, shadeId):
        shadeUrl = 'http://' + hubHostname + '/api/shades/' + shadeId

        data = self.getJSON(shadeUrl)['shade']
        data.pop('id')

        data['name']    = base64.b64decode(data.pop('name'))
        data['batteryLevel'] = data.pop('batteryStrength')

        if 'positions' in data:
            shadePositions = data.pop('positions')

            data.update(shadePositions)

        return data

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
        deviceId = action.props.get('deviceId', None)
        top      = action.props.get('top',    '')
        bottom   = action.props.get('bottom', '')

        self.debugLog('Setting position of ' + deviceId +
                      ' top: ' + top + ', bottom: ' + bottom)

        shade   = indigo.devices[int(deviceId)]
        address = shade.address

        hubHostname, shadeId = address.split(':')

        shadeUrl = 'http://' + hubHostname + '/api/shades/' + shadeId

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
