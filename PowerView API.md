## Hunter Douglas PowerView API

This document describes the Hunter Douglas PowerView API connecting to the
PowerView Hub on the local network.

The PowerView Hub API is accessible via HTTP.  This document assumes your have
given your hub a static IP address and a hostname of `powerview`.  If you
haven't done this you can swap `powerview` for the IP address of your hub.

Setting a static IP for your hub is beyond the scope of this document.  Consult
your router's manual for instructions.

All API request and response data uses the `application/json` content type.

This document uses `UPPERCASE` letters in URLs to indicate a variable field.
For example, in `GET http://powerview/api/shade/SHADE_ID` the `SHADE_ID` is the
variable field that would be filled in with a shade ID number.

### Hub discovery

The PowerView hub responds to a NetBios Name Service name query for a
`PBDU-Hub3.0` type NB (0x20) class IN (0x1), but seemingly only when the
transaction ID is 0x3e8.

### Shade

This is a shade object:

```
{
    "batteryStatus": 3,
    "batteryStrength": 159,
    "groupId": 5,
    "id": 7,
    "name": "U2hhZGUgbmFtZQ==",
    "order": 0,
    "positions": {
        "posKind1": 1,
        "posKind2": 2,
        "position1": 0,
        "position2": 0
    },
    "roomId": 11,
    "type": 8
}
```

* `batteryStrength` is the strength of the battery pack.
* `id` is the shade ID
* `name` is the base64 encoded shade name as a String
* `roomId` is the ID of the room the shade is in
* `positions` describes the position of the shade.  Sometimes this field is
  omitted in responses.
* `posKind1` refers to the bottom of the shade when equal to 1
* `posKind2` refers to the top of the shade when equal to 2
* `position1` is the offset of the shade.  0 is closed, 65535 is open
* `position2` is the offset of the shade.  0 is closed, 65535 is open

`GET http://powerview/api/shades`

Returns all shade data.  The response contains two top-level keys.  `shadeData`
contains an array of shade objects while the `shadeIds` contains an array of
shade IDs.

`GET http://powerview/api/shade/SHADE_ID`

Returns the shade object for a single shade in the `shade` key and all other
shades in the `shadeData` key.

`GET http://powerview/api/shade/SHADE_ID?updateBatteryLevel=true`

Updates the battery level of the shade.  This will jog the shade.

`PUT http://powerview/api/shade/SHADE_ID`

With a shade object with a `positions` object, sets the shade position.

```
{
    "shade": {
        "positions": {
            "posKind1": 1,
            "posKind2": 2,
            "position1": 32000,
            "position2": 32000
        }
    }
}
```

With a shade object with a `motion` key of `"jog"`, jogs the shade:

```
{
    "shade": {
        "motion": "jog"
    }
}
```

With a shade object with a `motion` key of `"calibrate"`, calibrates the shade:

```
{
    "shade": {
        "motion": "calibrate"
    }
}
```

### Room

This is a room object:

```
{
    "colorId": 15,
    "iconId": 10,
    "id": 11,
    "name": "Um9vbSBuYW1l",
    "order": 0
}
```

* `colorId` is the color for the room used in the mobile phone app
* `iconId` is the ID of the icon used in the mobile phone app
* `id` is the room ID
* `name` is the base64 encoded room name

`GET http://powerview/api/rooms`

Returns all room data.  The response contains two top-level keys.  `roomData`
contains an Array of room objects while `roomIds` contains an array of room
IDs.

`GET http://powerview/api/rooms/ROOM_ID`

Returns the room object for a single room in the `room` key.  The `roomData`
key may contain all other room objects.

### Scene

This is a scene object:

```
{
    "colorId": 9,
    "iconId": 0,
    "id": 13,
    "name": "U2NlbmUgbmFtZQ==",
    "networkNumber": 0,
    "order": 0,
    "roomId": 11
}
```

* `colorId` is the color for the scene used in the mobile phone app
* `iconId` is the ID of the icon used in the mobile phone app
* `id` is the scene ID
* `name` is the base64 encoded scene name
* `roomId` is the room the scene is in

`GET http://powerview/api/scenes`

Returns all scene data.  The response contains two top-level keys.  `sceneData`
contains an array of scene objects while the `sceneIds` contains an array of
scene IDs.

`GET http://poverview/api/scenes?sceneid=SCENE_ID`

Activate scene with the given scene id.

`GET http://powerview/api/scenes/SCENE_ID`

Returns the scene object for a single scene in the `scene` key.  The
`sceneData` key contains all other scenes.

### Scene Collection

This is a scene collection object:

```
{
    "colorId": 15,
    "iconId": 0,
    "id": 23771,
    "name": "U2NlbmUgY29sbGVjdGlvbiBuYW1l",
    "order": 0
}
```

* `colorId` is the color for the scene collection used in the mobile phone app
* `iconId` is the ID of the icon used in the mobile phone app
* `id` is the scene collection ID
* `name` is the base64 encoded scene collection name

`GET http://powerview/api/scenecollections`

Returns all scene collection data.  The response contains two top-level keys.
`sceneCollectionData` contains an array of scene collection objects while the
`sceneCollectionIds` contains an array of scene collection IDs.

`GET http://powerview/api/scenecollections?scenecollectionid=SCENE_COLLECTION_ID`

Activates the given scene collection id.

`GET http://powerview/api/scenecollections/SCENE_COLLECTION_ID`

Returns the scene collection object for a single scene collection in the
`sceneCollection` key.  The `sceneCollectionData` key contains all other scenes
collections.

### Hub information

`GET http://powerview/api/userdata/`

Returns hub information.

```
{
    "userData": {
        "accessPointCount": 0,
        "addressKind": "newPrimary",
        "dns": "192.0.2.1",
        "editingEnabled": true,
        "enableScheduledEvents": true,
        "gateway": "192.0.2.1",
        "groupCount": 2,
        "hubName": "aHVi",
        "ip": "192.0.2.2",
        "localTimeDataSet": true,
        "macAddress": "00:26:ff:ff:ff:ff",
        "mask": "255.255.255.0",
        "multiSceneCount": 3,
        "multiSceneMemberCount": 5,
        "remoteConnectEnabled": true,
        "rfID": "0x1234",
        "rfIDInt": 4660,
        "rfStatus": 0,
        "roomCount": 7,
        "sceneControllerCount": 0,
        "sceneControllerMemberCount": 0,
        "sceneCount": 11,
        "sceneMemberCount": 13,
        "scheduledEventCount": 17,
        "serialNumber": "0123456789ABCD",
        "setupCompleted": false,
        "shadeCount": 19,
        "staticIp": false,
        "unassignedShadeCount": 0,
        "undefinedShadeCount": 0
    }
}
```
