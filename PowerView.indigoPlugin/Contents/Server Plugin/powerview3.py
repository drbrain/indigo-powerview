
import base64
import math
import requests
try:
    import indigo
except ImportError:
    pass

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

    GENERATION = "V3"

    URL_ROOM_ = 'http://{h}/home/rooms/{id}'
    URL_SHADES_ = 'http://{h}/home/shades/{id}'
    URL_SHADES_MOTION_ = 'http://{h}/home/shades/{id}/motion'
    URL_SHADES_POSITIONS_ = 'http://{h}/home/shades/positions?ids={id}'
    URL_SHADES_STOP_ = 'http://{h}/home/shades/stop?ids={id}'
    URL_SCENES_ = 'http://{h}/home/scenes/{id}'
    URL_SCENES_ACTIVATE_ = 'http://{h}/home/scenes/{id}/activate'

    def __init__(self, prefs):
        super().__init__()
        self.logger = prefs.get('logger', None) # logging.getLogger(prefs.get('logger', "net.segment7.powerview"))

    def activateScene(self, hubHostname, sceneId):
        activateSceneUrl = self.URL_SCENES_ACTIVATE_.format(h=hubHostname, id=sceneId)
        self.put(activateSceneUrl)

    def activateSceneCollection(self, hubHostname, sceneCollectionId):
        indigo.server.log('Scene Collections are not available on Generation 3+ gateway. Use a Multi-Room Scene instead.')

    def calibrateShade(self, hubHostname, shadeId):
        indigo.server.log('Calibrate Shade function is not available on Generation 3+ gateway.')

    def jogShade(self, hubHostname, shadeId):
        shadeUrl = self.URL_SHADES_MOTION_.format(h=hubHostname, id=shadeId)
        body = {
            "motion": "jog"
        }
        self.put(shadeUrl, data=body)

    def stopShade(self, hubHostname, shadeId):
        shadeUrl = self.URL_SHADES_STOP_.format(h=hubHostname, id=shadeId)
        self.put(shadeUrl)

    def room(self, hubHostname, roomId) -> dict:
        roomUrl = self.URL_ROOM_.format(h=hubHostname, id=roomId)

        data = self.get(roomUrl)

        data['name'] = base64.b64decode(data.pop('name')).decode()

        return data

    def setShadePosition(self, hubHostname, shadeId, pos):
        # convert 0-100 values to 0-1.
        if pos.get('primary', '0') in range(0, 101) and \
                pos.get('secondary', '0') in range(0, 101) and \
                pos.get('tilt', '0') in range(0, 101) and \
                pos.get('velocity', '0') in range(0, 101):

            primary = float(pos.get('primary', '0')) / 100.0
            secondary = float(pos.get('secondary', '0')) / 100.0
            tilt = float(pos.get('tilt', '0')) / 100.0
            velocity = float(pos.get('velocity', '0')) / 100.0
            positions = {"primary": primary, "secondary": secondary, "tilt": tilt, "velocity": velocity}

            shade_url = self.URL_SHADES_POSITIONS_.format(h=hubHostname, id=shadeId)
            pos = {'positions': positions}
            self.put(shade_url, pos)
            return True
        else:
            indigo.server.log('Position sent to Set Shade Position must be values from 0 to 100.')
            return False

    def scenes(self, hubHostname):
        scenesURL = self.URL_SCENES_.format(h=hubHostname, id='')

        data = self.get(scenesURL)

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
        indigo.server.log('Scene Collections are not available on Generation 3+ gateway. Use a Multi-Room Scene instead.')
        return []

    def shade(self, hubHostname, shadeId, room=False) -> dict:
        shadeUrl = self.URL_SHADES_.format(h=hubHostname, id=shadeId)

        data = self.get(shadeUrl)
        if data:
            data['shadeId'] = data.pop('id')

            data['name'] = base64.b64decode(data.pop('name')).decode()
            data['generation'] = 3
            if room and 'roomId' in data:
                room_data = self.room(hubHostname, data['roomId'])
                data['room'] = room_data['name']
            if 'batteryStrength' in data:
                data['batteryLevel'] = data.pop('batteryStrength')
            else:
                data['batteryLevel'] = 'unk'

            if 'positions' in data:
                # Convert positions to integer percentages
                data['positions']['primary'] = self.to_percent(data['positions']['primary'])
                data['positions']['secondary'] = self.to_percent(data['positions']['secondary'])
                data['positions']['tilt'] = self.to_percent(data['positions']['tilt'])
                data['positions']['velocity'] = self.to_percent(data['positions']['velocity'])

        self.logger.debug("shade V3: Return data={}".format(data))
        return data

    def shadeIds(self, hubHostname) -> list:
        shadesUrl = self.URL_SHADES_.format(h=hubHostname, id='')

        data = self.get(shadesUrl)
        shadeIds = []
        for shade in data:
            shadeIds.append(shade['id'])

        return shadeIds

    def to_percent(self, pos, divr=1.0) -> int:
        self.logger.debug(f"to_percent: pos={pos}, becomes {math.trunc((float(pos) / divr * 100.0) + 0.5)}")
        return math.trunc((float(pos) / divr * 100.0) + 0.5)

    def do_get(self, url, *param, **kwargs):
        '''This method exists to make it easier to test the plugin.'''
        return requests.get(url, *param, **kwargs)

    def get(self, url) -> dict:
        try:
            res = self.do_get(url, headers={'accept': 'application/json'})
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"Error fetching {url}", exc_info=True)
            self.logger.debug(
                f"    Get from '{url}' returned {'n/a' if not res else res.status_code}, response body '{'n/a' if not res else res.text}'")
            return {}

        if res.status_code != requests.codes.ok:
            self.logger.error(f"Unexpected response fetching {url}: {res.status_code}")
            self.logger.debug(f"    Get from '{url}' returned {res.status_code}, response body '{res.text}'")
            return {}

        response = res.json()
        return response

    def put(self, url, data=None) -> dict:
        try:
            if data:
                res = requests.put(url, json=data, headers={'accept': 'application/json'})
            else:
                res = requests.put(url, headers={'accept': 'application/json'})

        except requests.exceptions.RequestException as e:
            self.logger.exception(f"Error in put {url} with data {data}:", exc_info=True)
            self.logger.debug(
                f"    Get from '{url}' returned {'n/a' if not res else res.status_code}, response body {'n/a' if not res else res.text}'")
            return False

        if res and res.status_code != requests.codes.ok:
            self.logger.error('Unexpected response in put %s: %s' % (url, str(res.status_code)))
            self.logger.debug(f"    Get from '{url}' returned {res.status_code}, response body '{res.text}'")
            return False

        response = res.json()
        return response
