#!/usr/bin/env python
# coding: utf-8

import indigo

class Plugin(indigo.PluginBase):
    def __init__(self, pluginId, pluginDisplayName, pluginVersion,
                 pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)
