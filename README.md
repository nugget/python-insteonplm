# insteonplm

[![Build Status](https://travis-ci.org/nugget/python-insteonplm.svg?branch=master)](https://travis-ci.org/nugget/python-insteonplm)
[![GitHub release](https://img.shields.io/github/release/nugget/python-insteonplm.svg)](https://github.com/nugget/python-insteonplm/releases)
[![PyPI](https://img.shields.io/pypi/v/insteonplm.svg)](https://pypi.python.org/pypi/insteonplm)

This is a Python package to interface with an Insteon Powerline Modem (formerly
called "PowerLinc").  It should work with either the USB or RS-232 serial based
devices such as the [2413U] and [2412S].  Other models have not been tested but
the underlying protocol is dusty and ancient and I wouldn't be surprised to
learned that this package works fine on some Bakelite X10 oddity from the
1980s.  If you find success with something, please let me know.

PowerLinc Modems are not telephony devices, they provide a Serial or USB
interface to an on-premisis Insteon IoT device network.  This is either
a powerline signalling protocol, an RF wireless protocol, ar a dual-band hybrid
network.

If you're looking for a library to work wtih the emulated PLM offered by an 
INSTEON [Hub] like the 2245 you might be able to use the [insteonlocal] package.

This package was created primarily to support an insteonplm platform
for the [Home Assistant] automation platform but it is structured to be
general-purpose and should be usable for other applications as well.

[Home Assistant]: https://home-assistant.io/
[2413U]: https://www.insteon.com/powerlinc-modem-usb
[2412S]: https://www.insteon.com/powerlinc-modem-serial
[Hub]: https://www.insteon.com/which-hub-are-you
[insteonlocal]: https://github.com/phareous/insteonlocal

## Requirements

- Python 3.4 or 3.5 with asyncio
- Some form of Insteon PLM
- At least one Insteon device

## Known Issues

- There's basically no documentation.
- 2412S support is untested and strictly theoretical.
- X10 protocol support is not implented yet.

## Installation

You can, of course, just install the most recent release of this package using
`pip`.  This will download the more rececnt version from [PyPI] and install it
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

### Device Permissions

Any user account that you want to be able to access the PLM will need
permissions to access the USB or Serial device in `/dev`.  In Linux, you'll
probably want to do something like this:

    sudo usermod -a -G dialout <username>

In FreeBSD, it'll be something like:

	sudo pw usermod <username> -G dialer

You may find that you have to log out and log back in as that user for the
change to take effect on existing sessions.

## Testing

The package installs a command-line tool which will connect to your receiver,
power it up, and then monitor all activity and changes that take place.  The
code for this console monitor is in `insteonplm/tools.py` and you can invoke it
by simply running this at the command line with the appropriate IP and port
number that matches your receiver and its configured port:

    insteonplm_monitor --device /dev/ttyUSB0

## Interesting Links

- [Project Home](https://github.com/nugget/python-insteonplm)
- [Why Nikola Tesla was the greatest geek who ever lived](http://theoatmeal.com/comics/tesla)

## Credits

- This package was written by David McNett.
  - https://github.com/nugget
  - https://keybase.io/nugget

- Many thanks to [Ryan Stanley](https://github.com/rstanley75) for his
  invaluable help with debugging and development.

## How can you help?

- First and foremost, you can help by forking this project and coding.  Features,
  bug fixes, documentation, and sample code will all add tremendously to the
  quality of this project.

- If you have a feature you'd love to see added to the project but you don't
  think that you're able to do the work, I'm someone is probably happy to
  perform the directed development in the form of a bug or feature bounty.

- If you're anxious for a feature but it's not actually worth money to you,
  please open an issue here on Github describing the problem or limitation.  If
  you never ask, it'll never happen

- If you just want to thank me for the work I've already done, I'm happy to
  accept your thanks, gratitude, pizza, or bitcoin.  My bitcoin wallet address
  can be on [Keybase](https://keybase.io/nugget) or you can send me a donation
  via [PayPal](https://www.paypal.me/macnugget).
  
- Or, if you're not comfortable sending me money directly, I'll be nearly as
  thrilled (really) if you donate to [the
  ACLU](https://action.aclu.org/donate-aclu),
  [EFF](https://supporters.eff.org/donate/), or [EPIC](https://epic.org) and
  let me know that you did.
