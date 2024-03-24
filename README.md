# Hunter Douglas PowerView Shade Indigo Plugin

This plugin lets you control [Hunter Douglas PowerView][hd_powerview] shades
from the [Indigo Domotics][indigo] home control software.

## Getting Started

To use this plugin you will need PowerView motorized shades, the PowerView
hub, and the Indigo software. The plugin supports both Generation 3 (V3) and Generation 2 (V2) PowerView hubs.

First determine the hostname or IP address of your PowerView Hub.  To
determine this:

For PowerView mobile app version 2:
* Open the PowerView mobile app
* Tap on the house name in the top left
* Tap on the hub name above "Scene Controllers"
* Tap "Info"
* Tap "Network Info"
* Tap "Static IP"

For PowerView version 3.x:
* Open the PowerView mobile app
* Tap on "More"
* Tap on "Accessories"
* Tap on "Gateways"
* Tap on the name of your gateway
* Tap on "Info & Options"

For generation 2 hubs, you need the value from the "IP address" field even 
if you do not have a static IP configured.  If the plugin stops controlling 
your shades, and you find the IP Address has changed in the PowerView mobile 
app, you may need to set a static IP.  Consult your router or access point 
documentation as well.

For generation 3 gateways, you may use the IP address (not recommended) or the hostname of the
gateway: powerview-g3.local

Next create a new device with the PowerView type and PowerView Hub model.
Fill in the hostname or IP address from the previous step.  Use the "Discover shades" button
to create the PowerView Shade devices automatically, or save the Hub device and then create 
a device for each shade, if you want to perform the labor manually. Either way, to
control a shade an Indigo device must exist for that shade. 

The "Discover shades" button will create an Indigo device for any shade on the hub that 
does not already exist. So clicking this button multiple times will have no negative effect, 
the plugin won't create the same shade twice.

You can now create actions to control shades using the actions described
below.

Optionally you can edit each PowerView Shade device to fill in the heading of
the window each shade covers to open or close shades depending on the sun
angle.  Open the compass app on your phone, touch it to your window, and enter
the value the compass shows.

## Features

Automatic shade discovery for easy first-time setup.  This also makes it
easy to create new shades, or if the shade gets disconnected from the hub for some
reason.  You can run the discovery process again then transfer the PowerView
Hub ID in Indigo from the new shade device to the old shade device so all your
actions continue to work.

Adjust shade positions from Indigo-supported keypads using the Set Shade
Position, Activate Scene, or Activate Scene Collection actions.

Adjust shades based on criteria beyond schedules including:

* Window-open sensors to prevent shades from closing when a window is open,
  causing them to blow around.
* Interior or exterior temperature to keep heat out of rooms you aren't using
* Sun angle (from the [Cynical Weather][cynical_weather] plugin as trigger) using the
  heading field of the shade device for automatic shading
  based on season.

Multiple hub support.  You can control shades and activate scenes across
multiple hubs.

## Supported Actions

The following Indigo actions are supported:

### Activate Scene

Activate a scene you have created in the PowerView mobile app.  This allows
you to run your existing PowerView scenes without needing to recreate them in
Indigo.

### Activate Scene Collection

Activate a scene collection you have created in the PowerView mobile app.
This allows you to run your existing PowerView scenes collections without
having to recreate them in Indigo. Not available with Generation 3 – Use 
Activate Scene with a Multi-Room Scene instead.

### Calibrate Shade

Rediscovers the movement limits of the shade. Not available nor needed with 
Generation 3.

### Jog Shade

Moves the shade a tiny bit.  This helps you identify which shade the device is
interacting with and to update the shade's position.

### Set Shade Position

Sets the shade position of an individual shade.  This allows you to set the top
and bottom positions of a shade for a top-down, bottom-up shade or the shade
position for a single-direction shade. For Generation 3 systems, setting the 
top, bottom, tilt, and velocity are supported. See 
[Shade Capabilities](#shade-capabilities) below for a description of how these 
values are used. Set each value as an integer percentage from 0 (closed) to 
100 (fully open).

The Current Position button will fill in the current position values. An easy 
way to create an Action to set a specific position is to move the shade with 
the remote to the desired position, then use the Current Position button to 
fill in the values when you create the Action.

### Stop Shade

Stops the shade if it is moving. To set the shade to a new position, start to 
open or close the shade, then stop it as it reaches the desired point. You can 
then easily create a new Action to move the shade to that position. Just use 
the Set Shade Position Action and click the "Current Position" button.

## Shade Capabilities

The shade capability describes the Hunter Douglas Shade's capabilities. In 
PowerView Gen 3, there are over 20 different types of Hunter Douglas Shades 
available. These Shade have a variety of different motion capabilities. While 
each Shade has its own set of unique properties, all can be represented by the 
following motion type capabilities:
 - Capability 0 - Bottom Up.
	* Examples: Standard roller/screen shades, Duette bottom up.
	* Uses the “primary” control type.

 - Capability 1 - Bottom Up w/ 90° Tilt. 
	* Examples: Silhouette, Pirouette.
	* Uses the “primary” and “tilt” control types.

 - Capability 2 - Bottom Up w/ 180° Tilt.
	* Example: Silhouette Halo.
	* Uses the “primary” and “tilt” control types.

 - Capability 3 - Vertical (Traversing).
	* Examples: Skyline, Duette Vertiglide, Design Studio Drapery.
	* Uses the “primary” control type.

 - Capability 4 - Vertical (Traversing) w/ 180° Tilt.
	* Example: Luminette.
	* Uses the “primary” and “tilt” control types.

 - Capability 5 - Tilt Only 180°.
	* Examples: Palm Beach Shutters, Parkland Wood Blinds.
	* Uses the “tilt” control type.

 - Capability 6 - Top Down.
	* Example: Duette Top Down.
	* Uses the “primary” control type.

 - Capability 7 - Top-Down/Bottom-Up (can open either from the bottom or from the top).
	* Examples: Duette TDBU, Vignette TDBU.
	* Uses the “primary” and “secondary” control types.

 - Capability 8 - Duolite (front and rear shades).
	* Examples: Roller Duolite, Vignette Duolite, Dual Roller.
	* Uses the “primary” and “secondary” control types.
	* Note: In some cases the front and rear shades are
controlled by a single motor and are on a single tube, so they cannot operate independently — the
front shade must be down before the rear shade can deploy. In other cases, they are independent with
two motors and two tubes. Where they are dependent, the shade firmware will force the appropriate
front shade position when the rear shade is controlled — there is no need for the control system to
take this into account.

 - Capability 9 - Duolite with 90° Tilt. (front bottom up shade that also tilts plus a rear blackout (non-tilting) shade).
	* Example: Silhouette Duolite, Silhouette Adeux.
	* Uses the “primary,” “secondary,” and “tilt” control types Note: Like with Capability 8, these can be
either dependent or independent.

 - Capability 10 - Duolite with 180° Tilt.
	* Example: Silhouette Halo Duolite.
	* Uses the “primary,” “secondary,” and “tilt” control types

 **Notes** 
 * The PowerView Plugin has no support for the "tilt" control type *when running with a 
 V2 or earlier hub*. Also with V2, the Plugin always treates the shades as if they were 
 Capability 7, so both "primary" and "secondary" are supported. Use "primary" for the bottom 
 setting, and "secondary" for the top for those shades that can move at top. Always set "secondary" to zero or blank if your 
 shade does not move at the top.
 * The plugin will show the current state of the shade, including its position, in the list 
of custom states of the device. However, if the shade is moved using the manual controls or
the PowerView mobile app, the shade can get out of sync with what is shown in Indigo.



## Usage Notes

The plugin does not poll the hub, so triggers based on the position (or any
other attribute) of shades or the hub will not execute when you expect.

Polling the hub does not solve this as the hub does not have a long-term
memory of shade positions.  To reliably know the shade positions you need to
move the shade somehow (at least jog it) which shortens the battery life of
the shades.

## See also

Hunter Douglas doesn't seem to have documentation for the hub API so for Generation 2 hubs, 
please see the unofficial [PowerView Hub API][hub_api]. 

For Generation 3 hubs, the API can be generated by your hub:
* Enable Swagger on your hub: http://powerview-g3.local/gateway/swagger?enable=true
* Get the Swagger results: http://powerview-g3.local:3002

[hd_powerview]: https://www.hunterdouglas.com/operating-systems/powerview-motorization
[indigo]: http://www.indigodomo.com
[cynical_weather]: http://www.cynic.org/indigo/plugins/online/weather.html
[hub_api]: PowerView%20API.md
