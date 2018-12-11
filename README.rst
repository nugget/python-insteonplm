insteonplm
==========

|Build Status| |GitHub release| |PyPI|

This is a Python package to interface with an Insteon Modem. It has been
tested to work with most USB or RS-232 serial based devices such as the
`2413U <https://www.insteon.com/powerlinc-modem-usb>`__,
`2412S <https://www.insteon.com/powerlinc-modem-serial>`__,
`2448A7 <http://www.insteon.com/usb-wireless-adapter>`__ and Hub models
`2242 <https://www.insteon.com/support-knowledgebase/2014/9/26/insteon-hub-owners-manual>`__
and `2245 <https://www.insteon.com/insteon-hub/>`__. Other models have
not been tested but the underlying protocol has not changed much over
time so it would not be surprising if it worked with a number of other
models. If you find success with something, please let us know.

This **insteonplm** package was created primarily to support an INSTEON
platform for the `Home Assistant <https://home-assistant.io/>`__
automation platform but it is structured to be general-purpose and
should be usable for other applications as well.

Requirements
------------

-  Python 3.5.3 or higher, 3.6 or 3.7
-  Posix or Windows based system
-  Some form of Insteon PLM or Hub
-  At least one Insteon device

Installation
------------

You can, of course, just install the most recent release of this package
using ``pip``. This will download the more recent version from
`PyPI <https://pypi.python.org/pypi/insteonplm>`__ and install it to
your host.

::

    pip install insteonplm

If you want to grab the the development code, you can also clone this
git repository and install from local sources:

::

    cd python-insteonplm
    pip install .

And, as you probably expect, you can live the developer's life by
working with the live repo and edit to your heart's content:

::

    cd python-insteonplm
    pip install -e .

Device Permissions
^^^^^^^^^^^^^^^^^^

Any user account that you want to be able to access the PLM will need
permissions to access the USB or Serial device in ``/dev``. In Linux,
you'll probably want to do something like this:

::

    sudo usermod -a -G dialout <username>

In FreeBSD, it'll be something like:

::

    sudo pw usermod <username> -G dialer

You may find that you have to log out and log back in as that user for
the change to take effect on existing sessions.

First Start
^^^^^^^^^^^

When the module starts it reads the IM's All-Link Database to find
linked devices. In order for this module to communicate with a device,
it must be linked to the IM. For help with linking please see the
section on the `Command Line Interface` below.

After the module loads the All-Link database it queries each device to
identify what type of device it is. This can take quite a while (5-15
sec per device). Once it identifies the devices it saves them in the
``WORKDIR`` so that future startups are faster.

Currently there is an issue with the command line `Tools` not
finding battery operated devices since they don't respond to device
information requests. This is being addressed in future releases. This
is not an issue if used with `Home
Assistant <https://home-assistant.io/>`__ through the use of device
overrides.

Tools
-----

The package installs a message monitor and a command line interface.

Message Monitoring
^^^^^^^^^^^^^^^^^^

You can monitor messages flowing across your INSTEON network with the
monitor command line tool. To invoke the monitor use the command:

::

    insteonplm_monitor --device /dev/ttyUSB0 --workdir /home/username

Command line options for the monitor are:

::

    -h, --help         show this help message and exit
    --device DEVICE    Path to PLM device
    --verbose, -v      Set logging level to verbose
    --workdir WORKDIR  Working directory for reading and saving device
                       information.

Command Line Interface
^^^^^^^^^^^^^^^^^^^^^^

The command line tool creates an interactive session to allow certain
functions to be performed on the INSTEON devices. To invoke the command
line tool use the command:

::

    `insteonplm_interactive --device /dev/ttyUSB0 --workdir /home/username`

Command line options for the interactive tool are:

::

    -h, --help        show this help message and exit
    --device DEVICE   Path to PLM device
    -v, --verbose     Set logging level to verbose
    --workdir WORKDIR  Working directory for reading and saving device
                      information.

Inside the command line tool use ``help`` to obtain a list of available
commands. The current list of available commands is:

::

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

For help with a specific command type ``help command_name``.

Known Issues
------------

-  The
   `documentation <https://github.com/nugget/python-insteonplm/wiki>`__
   is limited.
-  Other issues are located in our
   `issues <https://github.com/nugget/python-insteonplm/issues>`__ list
   on GitHub.

How You Can Help
----------------

Development
^^^^^^^^^^^

-  First and foremost, you can help by forking this project and coding.
   Features, bug fixes, documentation, and sample code will all add
   tremendously to the quality of this project.

-  If you have a feature you'd love to see added to the project but you
   don't think that you're able to do the work, I'm someone is probably
   happy to perform the directed development in the form of a bug or
   feature bounty.

Testing, Feature Requests and Issue Identification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  If you're anxious for a feature but it's not actually worth money to
   you, please open an issue here on Github describing the problem or
   limitation. If you never ask, it'll never happen

Documentation
^^^^^^^^^^^^^

Please see our
`Wiki <https://github.com/nugget/python-insteonplm/wiki>`__ section for
documentation. This documentation is limited. If you would like to drive
this effort please send a resume and a list of references to...
Honestly, we will take anyone.

PLEASE help. An
`issue <https://github.com/nugget/python-insteonplm/issues/23>`__ has
been opened so just post your interest there.

Credits
-------

-  This package was written by David McNett.
-  https://github.com/nugget
-  https://keybase.io/nugget

-  Significant updates were provided by Tom Harris
-  https://github.com/teharris1

-  Many thanks to `Ryan Stanley <https://github.com/rstanley75>`__ for
   his invaluable help with debugging and development.

Interesting Links
-----------------

-  `Project Home <https://github.com/nugget/python-insteonplm>`__
-  `Why Nikola Tesla was the greatest geek who ever
   lived <http://theoatmeal.com/comics/tesla>`__

.. |Build Status| image:: https://travis-ci.org/nugget/python-insteonplm.svg?branch=master
   :target: https://travis-ci.org/nugget/python-insteonplm
.. |GitHub release| image:: https://img.shields.io/github/release/nugget/python-insteonplm.svg
   :target: https://github.com/nugget/python-insteonplm/releases
.. |PyPI| image:: https://img.shields.io/pypi/v/insteonplm.svg
   :target: https://pypi.python.org/pypi/insteonplm
