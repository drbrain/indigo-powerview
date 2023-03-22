import base64
import requests

"""
Shade Capabilities:

Type 0 - Bottom Up 
Examples: Standard roller/screen shades, Duette bottom up 
Uses the “primary” control type

Type 1 - Bottom Up w/ 90° Tilt 
Examples: Silhouette, Pirouette 
Uses the “primary” and “tilt” control types

Type 2 - Bottom Up w/ 180° Tilt 
Example: Silhouette Halo 
Uses the “primary” and “tilt” control types

Type 3 - Vertical (Traversing) 
Examples: Skyline, Duette Vertiglide, Design Studio Drapery 
Uses the “primary” control type

Type 4 - Vertical (Traversing) w/ 180° Tilt 
Example: Luminette 
Uses the “primary” and “tilt” control types

Type 5 - Tilt Only 180° 
Examples: Palm Beach Shutters, Parkland Wood Blinds 
Uses the “tilt” control type

Type 6 - Top Down 
Example: Duette Top Down 
Uses the “primary” control type

Type 7 - Top-Down/Bottom-Up (can open either from the bottom or from the top) 
Examples: Duette TDBU, Vignette TDBU 
Uses the “primary” and “secondary” control types

Type 8 - Duolite (front and rear shades) 
Examples: Roller Duolite, Vignette Duolite, Dual Roller
Uses the “primary” and “secondary” control types 
Note: In some cases the front and rear shades are
controlled by a single motor and are on a single tube so they cannot operate independently - the
front shade must be down before the rear shade can deploy. In other cases, they are independent with
two motors and two tubes. Where they are dependent, the shade firmware will force the appropriate
front shade position when the rear shade is controlled - there is no need for the control system to
take this into account.

Type 9 - Duolite with 90° Tilt 
(front bottom up shade that also tilts plus a rear blackout (non-tilting) shade) 
Example: Silhouette Duolite, Silhouette Adeux 
Uses the “primary,” “secondary,” and “tilt” control types Note: Like with Type 8, these can be
either dependent or independent.

Type 10 - Duolite with 180° Tilt 
Example: Silhouette Halo Duolite 
Uses the “primary,” “secondary,” and “tilt” control types
"""


class PowerViewGen3:
    URL_ROOM_ = 'http://{h}/home/rooms/{id}'
    URL_SHADES_ = 'http://{h}/home/shades/{id}'
    URL_SHADES_MOTION_ = 'http://{h}/home/shades/{id}/motion'
    URL_SHADES_POSITIONS_ = 'http://{h}/home/shades/positions?ids={id}'
    URL_SHADES_STOP_ = 'http://{h}/home/shades/stop?ids={id}'
    URL_SCENES_ = 'http://{h}/home/scenes/{id}'
    URL_SCENES_ACTIVATE_ = 'http://{h}/home/scenes/{id}/activate'

    def __init__(self, logger):
        self.logger = logger

    def activateScene(self, hubHostname, sceneId):
        activateSceneUrl = self.URL_SCENES_ACTIVATE_.format(h=hubHostname, id=sceneId)

        self.__PUT(activateSceneUrl)

    def activateSceneCollection(self, hubHostname, sceneCollectionId):
        self.logger.error('Scene Collections are not available on Generation 3+ gateway. Use a Multi-Room Scene instead.')

    def calibrateShade(self, hubHostname, shadeId):
        self.logger.error('Calibrate Shade function is not available on Generation 3+ gateway.')

    def jogShade(self, hubHostname, shadeId):
        shadeUrl = self.URL_SHADES_MOTION_.format(h=hubHostname, id=shadeId)
        body = {
            "motion": "jog"
        }
        self.__PUT(shadeUrl, body)

    def stopShade(self, hubHostname, shadeId):
        shadeUrl = self.URL_SHADES_STOP_.format(h=hubHostname, id=shadeId)
        self.__PUT(shadeUrl)

    def room(self, hubHostname, roomId) -> dict:
        roomUrl = self.URL_ROOM_.format(h=hubHostname, id=roomId)

        data = self.__GET(roomUrl)

        data['name'] = base64.b64decode(data.pop('name')).decode()

        return data

    def setShadePosition(self, hubHostname, shadeId, positions):
        shadeUrl = self.URL_SHADES_POSITIONS_.format(h=hubHostname, id=shadeId)
        pos = {'positions':positions}

        self.__PUT(shadeUrl, pos)

    def scenes(self, hubHostname):
        scenesURL = self.URL_SCENES_.format(h=hubHostname, id='')

        data = self.__GET(scenesURL)

        for scene in data:
            name = base64.b64decode(scene.pop('name')).decode()

            if len(scene['roomIds']) == 1:
                room = self.room(hubHostname, scene['roomIds'][0])
                room_name = room['name']
            else:
                room_name = "Multi-Room"
            scene['name'] = '%s - %s' % (room_name, name)

        return data

    def sceneCollections(self, hubHostname):
        self.logger.error('Scene Collections are not available on Generation 3+ gateway. Use a Multi-Room Scene instead.')
        return []

    def shade(self, hubHostname, shadeId) -> dict:
        shadeUrl = self.URL_SHADES_.format(h=hubHostname, id=shadeId)

        data = self.__GET(shadeUrl)
        data['shadeId'] = data.pop('id')

        data['name'] = base64.b64decode(data.pop('name')).decode()
        data['generation'] = 3
        if 'roomId' in data:
            room_data = self.room(hubHostname, data['roomId'])
            data['room'] = room_data['name']
        if 'batteryStrength' in data:
            data['batteryLevel'] = data.pop('batteryStrength')
        else:
            data['batteryLevel'] = 'unk'

        return data

    def shadeIds(self, hubHostname) -> list:
        shadesUrl = self.URL_SHADES_.format(h=hubHostname, id='')

        data = self.__GET(shadesUrl)
        shadeIds = []
        for shade in data:
            shadeIds.append(shade['id'])

        return shadeIds

    def __GET(self, url) -> dict:
        try:
            f = requests.get(url)
        except requests.exceptions.RequestException as e:
            self.logger.error('Error fetching %s: %s' % (url, str(e)))
            return {}
        if f.status_code != requests.codes.ok:
            self.logger.error('Unexpected response fetching %s: %s' % (url, str(f.status_code)))
            return {}

        response = f.json()

        return response

    def __PUT(self, url, data=None) -> dict:

        try:
            if data:
                # data = {'positions':data}
                res = requests.put(url, json=data)
            else:
                res = requests.put(url)

        except requests.exceptions.RequestException as e:
            self.logger.error('Error in put %s: %s' % (url, str(e)))
            return {}
        if res.status_code != requests.codes.ok:
            self.logger.error('Unexpected response in put %s: %s' % (url, str(res.status_code)))
            return {}

        response = res.json()

        return response
