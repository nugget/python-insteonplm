# How to Install as a Service

## What we are making
I wanted the thermo script to run all of the time, and start automatically even after a reboot from patching or power outage.

## How I set it up
1. Install latest Rasbian Lite (I used Stretch for this) using Etcher.
1. Enable SSH
   1. On windows
      1. Look for the volume labeled "boot", on my machine it was K:
   1. On Linux or Mac
      1. You may have to find the device and mount it. (Instructions to come later)
   1. Add a blank file of "ssh" to the root of the folder.
1. For the rest of this, I boot up the pi and do it via SSH.
   1. It will default to a random IP via DHCP.  You may have to log in to your router to find it's IP.
1. Reset the default password to anything but "raspberry"
   1. Type passwd and follow the prompts to set the new password.
1. Run raspi-config to update various settings on your Pi.
   1. I update my locals, keyboard layout, timezone, cpu overclock, etc.
1. Install the latest updates
    ```
    sudo apt-get update
    sudo apt-get upgrade
    ```
1. Update the IP to be static. There are multiple ways to do it, I did the following:
   1. Edit the /etc/dhcpcd.conf with the following:
   ```
   interface eth0
   static ip_address=192.168.0.55/24
   static routers=192.168.0.1
   ```
1. Add the Thermo User
   1. `sudo useradd -rm thermouser -G fialout`
1. Build your Python 3 Virtual Environment
   1. Install Python and required packages.
      ```
      sudo apt-get install python3 python3-venv python3-pip
      ```
   1. Build your virtual environment.
      1. Create the folder and set the permissions
         ```
         sudo mkdir /srv/thermo
         sudo chown thermouser:thermouser /srv/thermo
         ```
      1. Create the virtual environment.
         ```
         sudo -u thermouser -H -s
         python3 -m venv /srv/thermo
         source /srv/thermo/bin/activate
         ```
   1. Install Python Modules
      ```
      pip install insteonplm
      pip install pyyaml
      ```
1. Install and test the script
   1. Copy the script and config yaml somewhere on the pi.  I put mine in `/home/thermouser/thermo`.
   1. Run the script to make sure it's working.
      ```
      python thermo.py -c thermocfg.yaml
      ```
   1. If you get an error saying:
      ```
      WARNING:insteonplm:Connection failed, retry in 1 seconds: /dev/ttyUSB0
      INFO:insteonplm:Connecting to PLM on /dev/ttyUSB0
      ```
      It means you forgot to add dialup permissions to the user.  You can fix it by running:
      ```
      sudo usermod thermouser -G dialout
      ```
1. Set it up to run as a service after reboot.
   1. Create the file `/etc/systemd/system/thermo@thermouser.service`
      1. It should have the following in it:
         ```
         [Unit]
         Description=Thermo Script
         After=network-online.target

         [Service]
         Type=simple
         User=%i
         WorkingDirectory=/home/thermouser/thermo
         ExecStart=/srv/thermo/bin/python3 thermo.py -c thermocfg.yaml -l thermolog.log

         [Install]
         WantedBy=multi-user.target
         ```
   1. Register the Service.
      ```
      sudo systemctl --system daemon-reload
      sudo systemctl enable thermo@thermouser.service
      ```
   1. Start the Service
      ```
      sudo systemctl start thermo@thermouser.service
      ```