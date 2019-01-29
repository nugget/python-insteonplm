# Sample Thermostat controller.

## Overview:
This was written to automate my home thermostats as I couldn't get it to work in Home Assistant yet.  I wanted the ability to do things such as dynamic temperature controls, adjust for seasons, time of day, vacation, etc.  I also wanted to validate that the thermostat controls are working as intended.

## Basic flow:
1. This will create a connection to the PLM Controller.
1. Waits for devices to be discovered.
1. As devices are being discovered, it will add callbacks if they are thermostats declared in the config.
1. Once all thermostats in a zone are discovered and reporting in, it will start monitoring a zone.
1. There are 2 main monitor loops:
    1. logging and Update loop.
    1. forced refresh to ensure settings are correct.

## Why Zones?
This is really dependent on the building and how it was built.  Most people with 1 thermostat don't even have to think about this.  But if you have multiple thermostats, you need to know how they map to actual heaters and coolers, or you can damage your HVAC.
Simple rule of thumb, if you have multiple thermostats, but only 1 heater/cooler, they should be in the same zone, and should be set to the same mode (heat/cool).  If not, it can damage your equipment.  To achieve this, 1 thermostat should be set as is master, and the rest in the zone will ensure they are set not to conflict with it.

## Configuration Yaml
* cycletime: 30 *How many seconds to wait to do a logging/config loop.*
* cyclesperrefresh: 2 *cyclesperrefresh x cycletime is the wait time to force a config refresh.*
* device: /dev/ttyUSB0 *Path to the PLM device*
* zones: *A list of dictionaries that represent of areas of control.*
* thehouse: *Dictionary that is the name of the zone*
* daystart: "05:30" *Time of day to start the day cycle*
* nightstart: "22:00" *Time of day to start the night cycle*
* awaymode: false *Not used yet, would let us do vacation/away where temps can go lower/higher*
* controllmodelismode: true *Debating which mode is better, this will let you decide on if the temperature or the current mode is the basis of operation.*
* thermos: *List of dictionaries that represent thermostat devices to control*
* name: downstairs *Friendly name of the thermostat*
* ismain: true *Indicates which thermostat is the master thermostat in the zone others will follow*
* address: 1a2b3c *Insteon ID*
* dayheat: 72 *Target day time Heating*
* daycool: 72 *Target day time Cooling*
* nightheat: 70 *Target night time Heating*
* nightcool: 70 *Target night time Cooling*
* tempbuffer: 2 *How many degrees to buffer so it doesn't flop between modes to quickly.*

## Future Areas of Enhancement:
* Add Away Mode
* Handle temporary bumps up/down
* Split logging and setting into separate loops (set 1 time an hour if correct?)