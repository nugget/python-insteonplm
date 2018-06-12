# insteonplm

[![Build Status](https://travis-ci.org/nugget/python-insteonplm.svg?branch=master)](https://travis-ci.org/nugget/python-insteonplm)
[![GitHub release](https://img.shields.io/github/release/nugget/python-insteonplm.svg)](https://github.com/nugget/python-insteonplm/releases)
[![PyPI](https://img.shields.io/pypi/v/insteonplm.svg)](https://pypi.python.org/pypi/insteonplm)


This is a Python package to interface with an Insteon Modem. It has been tested
to work with most USB or RS-232 serial based devices such as the [2413U],
[2412S], and [2448A7].  Other models have not been tested but the underlying
protocol has not changed much over time so it would not be surprising if it
worked with a number of other models. If you find success with something,
please let us know.

Work on the Hub is underway but if you are looking for a library to work with
the emulated PLM offered by an INSTEON [Hub] like the 2245 you might be able to
use the [insteonlocal] package.

This **insteonplm** package was created primarily to support an INSTEON PLM
platform for the [Home Assistant] automation platform but it is structured
to be general-purpose and should be usable for other applications as well.

[Home Assistant]: https://home-assistant.io/
[2413U]: https://www.insteon.com/powerlinc-modem-usb
[2412S]: https://www.insteon.com/powerlinc-modem-serial
[2448A7]: http://www.insteon.com/usb-wireless-adapter
[Hub]: https://www.insteon.com/which-hub-are-you
[insteonlocal]: https://github.com/phareous/insteonlocal

## Contents
- [Requirements]
- [Installation]
    - [Device permissions]
    - [First Start]
- [Tools]
    - [Message Monitoring]
    - [Command Line Interface]
- [Known Issues]
- [How You Can Help]
    - [Development]
    - [Testing, Feature Requests and Issue Identification]
    - [Documentation]
- [Credits]
- [Interesting Links]

[Requirements]:#requirements
[Installation]:#installation
[Device permissions]:#device-permissions
[First Start]:#first-start
[Tools]:#tools
[Message Monitoring]:#message-monitoring
[Command Line Interface]:#command-line-interface
[Known Issues]:#known-issues
[How You Can Help]:#how-you-can-help
[Development]:#development
[Testing, Feature Requests and Issue Identification]:#testing-feature-requests-and-issue-identification
[Documentation]:#documentation
[Credits]:#credits
[Interesting Links]:#interesting-links

## Requirements

- Python 3.4, 3.5 or 3.6 with asyncio
- Posix based system (currently does not work on Windows due to a serial port issue)
- Some form of Insteon PLM or INSTEON USB Stick
- At least one Insteon device

## Installation

You can, of course, just install the most recent release of this package using
`pip`.  This will download the more recent version from [PyPI] and install it
to your host.

[PyPI]: https://pypi.python.org/pypi/insteonplm

    pip install insteonplm

If you want to grab the the development code, you can also clone this git
repository and install from local sources:

	cd python-insteonplm
    pip install .

And, as you probably expect, you can live the developer's life by working with
the live repo and edit to your heart's content:

    cd python-insteonplm
	pip install -e .

#### Device Permissions

Any user account that you want to be able to access the PLM will need
permissions to access the USB or Serial device in `/dev`.  In Linux, you'll
probably want to do something like this:

    sudo usermod -a -G dialout <username>

In FreeBSD, it'll be something like:

	sudo pw usermod <username> -G dialer

You may find that you have to log out and log back in as that user for the
change to take effect on existing sessions.

#### First Start

When the module starts it reads the IM's All-Link Database to find linked
devices. In order for this module to communicate with a device, it must be
linked to the IM. For help with linking please see the section on the
[Command Line Tool] below.

After the module loads the All-Link database it queries each device to identify
what type of device it is. This can take quite a while (5-15 sec per
device). Once it identifies the devices it saves them in the `WORKDIR` so that
future startups are faster. 

Currently there is an issue with the command line [Tools] not finding battery
operated devices since they don't respond to device information requests.
This is being addressed in future releases. This is not an issue if used with 
[Home Assistant] through the use of device overrides.

## Tools

The package installs a message monitor and a command line interface.   

#### Message Monitoring

You can monitor messages flowing across your INSTEON network with the monitor
command line tool. To invoke the monitor use the command:

    insteonplm_monitor --device /dev/ttyUSB0 --workdir /home/username

Command line options for the monitor are:

    -h, --help         show this help message and exit
    --device DEVICE    Path to PLM device
    --verbose, -v      Set logging level to verbose
    --workdir WORKDIR  Working directory for reading and saving device
                       information.

#### Command Line Interface

The command line tool creates an interactive session to allow certain functions
to be performed on the INSTEON devices. To invoke the command line tool use the
command:

    insteonplm_interactive --device /dev/ttyUSB0 --workdir /home/username_

Command line options for the interactive tool are:

    -h, --help        show this help message and exit
    --device DEVICE   Path to PLM device
    -v, --verbose     Set logging level to verbose
    --workdir WORKDIR  Working directory for reading and saving device
                      information.

Inside the command line tool use `help` to obtain a list of available commands.
The current list of available commands is:
```
 -  add_all_link        Add an All-Link record to the IM and a device.
 -  add_device_override Add a device override to the IM.
 -  add_x10_device      Add an X10 device to the IM
 -  connect             Connect to the IM
 -  del_all_link        Delete an all link record from the IM and a device
 -  exit                Exit the tool
 -  help                List available commands
 -  list_devices        Print a list of the available devices
 -  load_aldb           Read and load a device All-Link database
 -  on_off_test         Test a device with simple on/off commands
 -  print_aldb          Print the All-Link database for a device
 -  running_tasks       List tasks running in the background
 -  set_device          Set the IM device path
 -  set_log_level       Set the log message display level
 -  set_workdir         Set the WORKDIR to load and save device info
 -  write_aldb          Write a record to the device All-Link database
                            !!!! BE CAREFUL WITH THIS COMMAND !!!!!
```

For help with a specific command type `help command_name`.

## Known Issues

- The [documentation](https://github.com/nugget/python-insteonplm/wiki) is limited.
- Other issues are located in our [issues] list on GitHub.

[issues]: https://github.com/nugget/python-insteonplm/issues

## How You Can Help

#### Development

- First and foremost, you can help by forking this project and coding.  Features,
  bug fixes, documentation, and sample code will all add tremendously to the
  quality of this project.

- If you have a feature you'd love to see added to the project but you don't
  think that you're able to do the work, I'm someone is probably happy to
  perform the directed development in the form of a bug or feature bounty.

#### Testing, Feature Requests and Issue Identification

- If you're anxious for a feature but it's not actually worth money to you,
  please open an issue here on Github describing the problem or limitation.  If
  you never ask, it'll never happen

#### Documentation

Please see our [Wiki](https://github.com/nugget/python-insteonplm/wiki)
section for documentation. This documentation is limited. If
you would like to drive this effort please send a resume and a list of references
to... Honestly, we will take anyone.

PLEASE help. An [issue](https://github.com/nugget/python-insteonplm/issues/23)
has been opened so just post your interest there.

## Credits

- This package was written by David McNett.
  - https://github.com/nugget
  - https://keybase.io/nugget

- Significant updates were provided by Tom Harris
  - https://github.com/teharris1

- Many thanks to [Ryan Stanley](https://github.com/rstanley75) for his
  invaluable help with debugging and development.

## Interesting Links

- [Project Home](https://github.com/nugget/python-insteonplm)
- [Why Nikola Tesla was the greatest geek who ever lived](http://theoatmeal.com/comics/tesla)
