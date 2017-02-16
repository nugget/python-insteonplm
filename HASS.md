# Beta installation into Home Assistant

As of v0.7.0 the platform is in good enough shape to be usable inside Home
Assistant.  If you want to experiment with the code, this should get you up
and running.

## Installation

First download this [tarball] and extract it into your `custom_components`
directory inside your base hass configuration location (usually
`~/.homeassistant/`)

[tarball]: https://macnugget.org/crud/insteon_plm_beta.tar.gz


Then incorporate the following elements into you `configuration.yaml` to
taste.  The logging will be extremely verbose, so you might want to omit that
unless you have problems and want to debug further.

The customize block can be used to give friendly names to the bare device names
that are exposed by the platform.  You'll probably want to add entities to this
block for each of your INSTEON devices.

    homeassistant:
        customize:
            - entity_id: light.4095e6
              friendly_name: Computer Room
            - entity_id: binary_sensor.395fa4
              friendly_name: Garage Door

    insteon_plm:
        port: /dev/ttyUSB0

    light:
        - platform: insteon_plm

    switch:
         - platform: insteon_plm

    binary_sensor:
         - platform: insteon_plm

    logger:
        default: info
        logs:
            homeassistant.components.insteon_plm: debug
            insteonplm.protocol: debug
