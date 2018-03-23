"""Embodies the INSTEON Product Database static data and access methods."""
import logging
import collections

from insteonplm.devices.unknowndevice import UnknownDevice
from insteonplm.devices.generalController import GeneralController
from insteonplm.devices.dimmableLightingControl import DimmableLightingControl
from insteonplm.devices.dimmableLightingControl import DimmableLightingControl_2475F
from insteonplm.devices.switchedLightingControl import SwitchedLightingControl
from insteonplm.devices.switchedLightingControl import SwitchedLightingControl_2663_222
from insteonplm.devices.securityHealthSafety import (SecurityHealthSafety,
                                   SecurityHealthSafety_2421,
                                   SecurityHealthSafety_2842_222,
                                   SecurityHealthSafety_2852_222,
                                   SecurityHealthSafety_2845_222,
                                   SecurityHealthSafety_2982_222)

from insteonplm.devices.sensorsActuators import SensorsActuators
from insteonplm.devices.sensorsActuators import SensorsActuators_2450

# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods

Product = collections.namedtuple('Product', 'cat subcat product_key description model deviceclass')

# flake8: noqa
class IPDB(object):
    """Embodies the INSTEON Product Database static data and access methods."""

    # pylint disable=line-too-long
    products = [
        Product(None, None, None, 'Unknown Device', '', UnknownDevice),

        Product(0x00, None, None, 'Generic General Controller', '', GeneralController),
        Product(0x00, 0x04, None, 'ControLinc', '2430', GeneralController),
        Product(0x00, 0x05, 0x000034, 'RemoteLinc', '2440', GeneralController),
        Product(0x00, 0x06, None, 'ICON Tabletop Controller', '2830', GeneralController),
        Product(0x00, 0x08, None, 'EZBridge/EZServer', '', GeneralController),
        Product(0x00, 0x09, None, 'SignaLinc', '2442', GeneralController),
        Product(0x00, 0x0A, 0x000007, 'Poolux LCD Controller', '', GeneralController),
        Product(0x00, 0x0B, 0x000022, 'Range Extender', '2443', GeneralController),
        Product(0x00, 0x0C, 0x000028, 'IES Color Touchscreen', '', GeneralController),
        Product(0x00, 0x10, None, 'Mini Remote - 4 Scene', '2444A2WH4', GeneralController),
        Product(0x00, 0x11, None, 'Mini Remote - Switch', '2444A3', GeneralController),
        Product(0x00, 0x12, None, 'Mini Remote - 8 Scene', '2444A2WH8', GeneralController),
        Product(0x00, 0x14, None, 'Mini Remote - 4 Scene', '2342-432', GeneralController),
        Product(0x00, 0x15, None, 'Mini Remote - Switch', '2342-442', GeneralController),
        Product(0x00, 0x16, None, 'Mini Remote - 8 Scene', '2342-422', GeneralController),
        Product(0x00, 0x17, None, 'Mini Remote - 4 Scene', '2342-532', GeneralController),
        Product(0x00, 0x18, None, 'Mini Remote - 8 Scene', '2342-522', GeneralController),
        Product(0x00, 0x19, None, 'Mini Remote - Switch', '2342-542', GeneralController),
        Product(0x00, 0x1A, None, 'Mini Remote - 4 Scene', '2342-222', GeneralController),
        Product(0x00, 0x1B, None, 'Mini Remote - 8 Scene', '2342-232', GeneralController),
        Product(0x00, 0x1C, None, 'Mini Remote - Switch', '2342-242', GeneralController),
        Product(0x00, 0x1D, 0x000022, 'Range Extender', '2992-222', GeneralController),

        Product(0x01, None, None, 'Generic Dimmable Lighting Control', '', DimmableLightingControl),
        Product(0x01, 0x00, None, 'LampLinc Dimmer', '2456D3', DimmableLightingControl),
        Product(0x01, 0x01, None, 'SwitchLinc Dimmer', '2476D', DimmableLightingControl),
        Product(0x01, 0x02, None, 'In-LineLinc Dimmer', '2475D', DimmableLightingControl),
        Product(0x01, 0x03, None, 'ICON Dimmer Switch', '2876D', DimmableLightingControl),
        Product(0x01, 0x04, None, 'SwitchLinc Dimmer', '2476DH', DimmableLightingControl),
        Product(0x01, 0x05, 0x000041, 'Keypad Countdown Timer', '2484DWH8', DimmableLightingControl),
        Product(0x01, 0x06, None, 'LampLinc', '2456D2', DimmableLightingControl),
        Product(0x01, 0x07, None, 'ICON LampLinc', '2856D2', DimmableLightingControl),
        Product(0x01, 0x07, None, 'ICON LampLinc', '2856D2B', DimmableLightingControl),
        Product(0x01, 0x09, 0x000037, 'KeypadLinc Dimmer', '2486DWH6', DimmableLightingControl),
        Product(0x01, 0x0A, None, 'ICON In-Wall Controller', '', DimmableLightingControl),
        Product(0x01, 0x0B, None, 'Dimmer Module', '2632-422', DimmableLightingControl),
        Product(0x01, 0x0C, 0x00001D, 'KeypadLinc Dimmer', '2486DWH8', DimmableLightingControl),
        Product(0x01, 0x0D, None, 'SocketLinc', '2454D', DimmableLightingControl),
        Product(0x01, 0x0E, None, 'LampLinc Dimmer', '2457D2', DimmableLightingControl),
        Product(0x01, 0x0F, None, 'Dimmer Module', '2632-432', DimmableLightingControl),
        Product(0x01, 0x11, None, 'Dimmer Module', '2632-442', DimmableLightingControl),
        Product(0x01, 0x12, None, 'Dimmer Module', '2632-522', DimmableLightingControl),
        Product(0x01, 0x13, 0x000032, 'SwitchLinc Dimmer (Lixar)', '2676D-B', DimmableLightingControl),
        Product(0x01, 0x17, None, 'ToggleLinc Dimmer', '2466DW', DimmableLightingControl),
        Product(0x01, 0x18, None, 'ICON SwitchLinc Dimmer In-line Companion', '2474D', DimmableLightingControl),
        Product(0x01, 0x19, None, 'SwitchLinc Dimmer', '2476D', DimmableLightingControl),
        Product(0x01, 0x1A, None, 'In-LineLinc Dimmer', '2475D', DimmableLightingControl),
        Product(0x01, 0x1B, None, 'KeypadLinc Dimmer', '2486DWH6', DimmableLightingControl),
        Product(0x01, 0x1B, 0x00001D, 'KeypadLinc Dimmer', '2486DWH6', DimmableLightingControl),
        Product(0x01, 0x1C, None, 'KeypadLinc Dimmer', '2486DWH8', DimmableLightingControl),
        Product(0x01, 0x1D, None, 'SwitchLinc Dimmer', '2476DH', DimmableLightingControl),
        Product(0x01, 0x1E, None, 'ICON Dimmer Switch', '2876D', DimmableLightingControl),
        Product(0x01, 0x1F, 0x0000000, 'ToggleLinc Dimmer', '2466DW', DimmableLightingControl),
        Product(0x01, 0x20, None, 'SwitchLinc Dimmer', '2477D', DimmableLightingControl),
        Product(0x01, 0x20, 0x00006B, 'SwitchLinc Dimmer', '2477D', DimmableLightingControl),
        Product(0x01, 0x21, None, 'OutletLinc Dimmer', '2472DWH', DimmableLightingControl),
        Product(0x01, 0x22, None, 'LampLinc Dimmer', '2457D2X', DimmableLightingControl),
        Product(0x01, 0x23, None, 'LampLinc EZ', '2457D2', DimmableLightingControl),
        Product(0x01, 0x24, None, 'SwitchLinc 2-Wire Dimmer', '2474DWH', DimmableLightingControl),
        Product(0x01, 0x25, None, 'INSTEON Ballast Dimmer', '2475DA2', DimmableLightingControl),
        Product(0x01, 0x27, 0x000087, 'Wall Dimmer', '4701', DimmableLightingControl),
        Product(0x01, 0x29, 0x000089, 'Wall Keypad Dimmer', '4703', DimmableLightingControl),
        Product(0x01, 0x2A, 0x00008B, 'Plug-in Dimmer', '4705', DimmableLightingControl),
        Product(0x01, 0x2B, 0x000091, 'Wall Dimmer - 1000W', '4711', DimmableLightingControl),
        Product(0x01, 0x2C, 0x000092, 'In-Line Dimmer', '4712', DimmableLightingControl),
        Product(0x01, 0x2D, 0x00009E, 'SwitchLinc Dimmer', '2477DH', DimmableLightingControl),
        Product(0x01, 0x2E, None, 'FanLinc', '2475F',  DimmableLightingControl_2475F),
        Product(0x01, 0x2F, None, 'KeypadLinc Schedule Timer with Dimmer', '2484DST6', DimmableLightingControl),
        Product(0x01, 0x30, None, 'SwitchLinc Dimmer', '2476D', DimmableLightingControl),
        Product(0x01, 0x31, None, 'SwitchLinc Dimmer', '2478D', DimmableLightingControl),
        Product(0x01, 0x31, None, 'SwitchLinc Dimmer', '2478D', DimmableLightingControl),
        Product(0x01, 0x32, None, 'In-LineLinc Dimmer', '2475DA1', DimmableLightingControl),
        Product(0x01, 0x34, None, 'DIN Rail Dimmer', '2252-222', DimmableLightingControl),
        Product(0x01, 0x34, None, 'DIN Rail Dimmer', '2452-222', DimmableLightingControl),
        Product(0x01, 0x35, None, 'Micro Dimmer', '2442-222', DimmableLightingControl),
        Product(0x01, 0x36, None, 'DIN Rail Dimmer', '2452-422', DimmableLightingControl),
        Product(0x01, 0x37, None, 'DIN Rail Dimmer', '2452-522', DimmableLightingControl),
        Product(0x01, 0x38, None, 'Micro Dimmer', '2442-422', DimmableLightingControl),
        Product(0x01, 0x39, None, 'Micro Dimmer', '2442-522', DimmableLightingControl),
        Product(0x01, 0x3A, None, 'LED Bulb', '2672-222', DimmableLightingControl),
        Product(0x01, 0x3B, None, 'LED Bulb', '2672-422', DimmableLightingControl),
        Product(0x01, 0x3C, None, 'LED Bulb', '2672-522', DimmableLightingControl),
        Product(0x01, 0x3D, None, 'Ballast Dimmer', '2446-422', DimmableLightingControl),
        Product(0x01, 0x3E, None, 'Ballast Dimmer', '2446-522', DimmableLightingControl),
        Product(0x01, 0x3F, None, 'Fixture Dimmer', '2447-422', DimmableLightingControl),
        Product(0x01, 0x40, None, 'Fixture Dimmer', '2447-522', DimmableLightingControl),
        Product(0x01, 0x41, None, 'Keypad Dimmer', '2334-222', DimmableLightingControl),
        Product(0x01, 0x42, None, 'Keypad Dimmer', '2334-232', DimmableLightingControl),
        Product(0x01, 0x42, None, 'Keypad with Dimmer', '2334-232', DimmableLightingControl),
        Product(0x01, 0x49, None, 'LED PAR38 Bulb', '2674-222', DimmableLightingControl),
        Product(0x01, 0x4A, None, 'LED PAR38 Bulb', '2674-422', DimmableLightingControl),
        Product(0x01, 0x4B, None, 'LED PAR38 Bulb', '2672-522', DimmableLightingControl),
        Product(0x01, 0x4C, None, 'LED Bulb', '2672-522', DimmableLightingControl),
        Product(0x01, 0x4D, None, 'LED Bulb', '2672-522', DimmableLightingControl),
        Product(0x01, 0x4E, None, 'LED PAR38 Bulb', '2674-422', DimmableLightingControl),
        Product(0x01, 0x4F, None, 'LED PAR38 Bulb', '2672-522', DimmableLightingControl),

        Product(0x02, None, None, 'Generic Switched Lighting Control', '', SwitchedLightingControl),
        Product(0x02, 0x06, None, 'Outdoor ApplianceLinc', '2456S3E', SwitchedLightingControl),
        Product(0x02, 0x07, None, 'TimerLinc', '2456S3T', SwitchedLightingControl),
        Product(0x02, 0x08, 0x000023, 'OutletLinc Relay', '2473SWH', SwitchedLightingControl),
        Product(0x02, 0x09, None, 'ApplianceLinc', '2456S3', SwitchedLightingControl),
        Product(0x02, 0x0A, None, 'SwitchLinc Relay', '2476S', SwitchedLightingControl),
        Product(0x02, 0x0B, None, 'ICON On/Off Switch', '2876S', SwitchedLightingControl),
        Product(0x02, 0x0C, None, 'ICON Appliance Module', '2856S3B', SwitchedLightingControl),
        Product(0x02, 0x0D, None, 'ToggleLinc On/Off', '2466SW', SwitchedLightingControl),
        Product(0x02, 0x0E, None, 'SwitchLinc Relay Countdown Timer', '2476ST', SwitchedLightingControl),
        Product(0x02, 0x0F, None, 'KeypadLinc On/Off', '2486SWH6', SwitchedLightingControl),
        Product(0x02, 0x0F, 0x000036, 'KeypadLinc On/Off', '2486SWH6', SwitchedLightingControl),
        Product(0x02, 0x10, 0x00001B, 'In-LineLinc Relay', '2475S', SwitchedLightingControl),
        Product(0x02, 0x11, None, 'EZSwitch30', '', SwitchedLightingControl),
        Product(0x02, 0x12, 0x00003E, 'ICON In-LineLinc Relay', '2474S', SwitchedLightingControl),
        Product(0x02, 0x13, None, 'Icon SwitchLinc Relay (Lixar)', '2676R-B', SwitchedLightingControl),
        Product(0x02, 0x14, None, 'In-LineLinc Relay with Sense', '2475S2', SwitchedLightingControl),
        Product(0x02, 0x15, None, 'SwitchLinc Relay with Sense', '2476S', SwitchedLightingControl),
        Product(0x02, 0x16, None, 'ICON On/Off Switch', '2876S', SwitchedLightingControl),
        Product(0x02, 0x17, None, 'ICON Appliance Module', '2856S3B', SwitchedLightingControl),
        Product(0x02, 0x18, 0x000060, 'SwitchLinc 220V Relay', '2494S220', SwitchedLightingControl),
        Product(0x02, 0x19, None, 'SwitchLinc 220V Relay', '2494S220', SwitchedLightingControl),
        Product(0x02, 0x1A, 0x0000000, 'ToggleLinc On/Off', '2466SW', SwitchedLightingControl),
        Product(0x02, 0x1C, None, 'SwitchLinc Relay', '2476S', SwitchedLightingControl),
        Product(0x02, 0x1E, None, 'KeypadLinc On/Off', '2487S', SwitchedLightingControl),
        Product(0x02, 0x1F, None, 'In-LineLinc On/Off', '2475SDB', SwitchedLightingControl),
        Product(0x02, 0x20, 0x00008A, 'Wall Keypad Switch', '4704', SwitchedLightingControl),
        Product(0x02, 0x21, 0x00008C, 'Outlet Switch', '4707', SwitchedLightingControl),
        Product(0x02, 0x22, 0x000093, 'In-Line Switch', '4713', SwitchedLightingControl),
        Product(0x02, 0x23, 0x000088, 'Wall Switch', '4702', SwitchedLightingControl),
        Product(0x02, 0x24, 0x0000A1, 'Wall Keypad Switch 277V', '4102', SwitchedLightingControl),
        Product(0x02, 0x25, None, 'Keypad Countdown Timer 8-button', '2484SWH8', SwitchedLightingControl),
        Product(0x02, 0x26, None, 'KeypadLinc Schedule Timer On/Off Switch', '2485SWH6', SwitchedLightingControl),
        Product(0x02, 0x29, None, 'SwitchLinc Relay Countdown Timer', '2476ST', SwitchedLightingControl),
        Product(0x02, 0x2A, None, 'SwitchLinc Relay (Dual-Band)', '2477S', SwitchedLightingControl),
        Product(0x02, 0x2B, None, 'In-LineLinc On/Off', '2475SDB-50', SwitchedLightingControl),
        Product(0x02, 0x2B, None, 'In-LineLinc On/Off)', '2475SDB-50', SwitchedLightingControl),
        Product(0x02, 0x2C, None, 'KeypadLinc On/Off', '2487S', SwitchedLightingControl),
        Product(0x02, 0x2C, None, 'KeypadLinc On/Off', '2487S-50', SwitchedLightingControl),
        Product(0x02, 0x2D, None, 'On/Off Module', '2633-422', SwitchedLightingControl),
        Product(0x02, 0x2E, None, 'DIN Rail On/Off', '2453-222', SwitchedLightingControl),
        Product(0x02, 0x2F, None, 'Micro On/Off', '2443-222', SwitchedLightingControl),
        Product(0x02, 0x30, None, 'On/Off Module', '2633-432', SwitchedLightingControl),
        Product(0x02, 0x31, None, 'Micro On/Off', '2443-422', SwitchedLightingControl),
        Product(0x02, 0x32, None, 'Micro On/Off', '2443-522', SwitchedLightingControl),
        Product(0x02, 0x33, None, 'DIN Rail On/Off', '2453-422', SwitchedLightingControl),
        Product(0x02, 0x34, None, 'DIN Rail On/Off', '2453-522', SwitchedLightingControl),
        Product(0x02, 0x35, None, 'On/Off Module', '2633-442', SwitchedLightingControl),
        Product(0x02, 0x36, None, 'On/Off Module', '2633-522', SwitchedLightingControl),
        Product(0x02, 0x37, None, 'On/Off Module', '2635-222', SwitchedLightingControl),
        Product(0x02, 0x38, None, 'On/Off Outdoor Module', '2634-222', SwitchedLightingControl),
        Product(0x02, 0x39, None, 'On/Off Outlet', '2663-222', SwitchedLightingControl_2663_222),

        Product(0x03, None, None, 'Generic Network Bridge Controller', '', None),
        Product(0x03, 0x01, None, 'PowerLinc Serial', '2414S', None),
        Product(0x03, 0x02, None, 'PowerLinc USB', '2414U', None),
        Product(0x03, 0x03, None, 'ICON PLC Serial', '', None),
        Product(0x03, 0x04, None, 'ICON PLC USB', '', None),
        Product(0x03, 0x05, 0x00000C, 'PowerLinc Serial Modem', '2412S', None),
        Product(0x03, 0x06, None, 'IRLinc Receiver', '2411R', None),
        Product(0x03, 0x07, None, 'IRLinc Transmitter', '2411T', None),
        Product(0x03, 0x0B, 0x000030, 'PowerLinc USB Modem', '2412U', None),
        Product(0x03, 0x0D, 0x000035, 'SimpleHomeNet EZX10RF', '', None),
        Product(0x03, 0x0F, 0x00003B, 'EZX10IR', '', None),
        Product(0x03, 0x10, None, 'SmartLinc', '2412N', None),
        Product(0x03, 0x10, None, 'SmartLinc', '2412N', None),
        Product(0x03, 0x11, None, 'PowerLinc Serial Modem', '2413S', None),
        Product(0x03, 0x13, 0x000030, 'PowerLinc USB Modem', '2412UH', None),
        Product(0x03, 0x14, 0x00000C, 'PowerLinc Serial Modem', '2412SH', None),
        Product(0x03, 0x15, None, 'PowerLinc USB Modem', '2413U', None),
        Product(0x03, 0x18, None, 'Central Controller', '2243-222', None),
        Product(0x03, 0x19, None, 'PowerLinc Serial Modem', '2413SH', None),
        Product(0x03, 0x1A, None, 'PowerLinc USB Modem', '2413UH', None),
        Product(0x03, 0x1B, None, 'iGateway', '2423A4', None),
        Product(0x03, 0x1F, 0x00007E, 'USB Adapter', '2448A7', None),
        Product(0x03, 0x20, 0x00007E, 'USB Adapter', '2448A7', None),
        Product(0x03, 0x21, 0x00008E, 'USB Adapter', '2448A7H', None),
        Product(0x03, 0x22, 0x00008F, 'Central Controller Interface', '4706A', None),
        Product(0x03, 0x23, 0x00008E, 'USB Adapter', '2448A7H', None),
        Product(0x03, 0x24, 0x0000A2, 'TouchLinc', '2448A7T', None),
        Product(0x03, 0x27, 0x0000A2, 'TouchLinc', '2448A7T', None),
        Product(0x03, 0x2B, None, 'Hub', '2242-222', None),
        Product(0x03, 0x2C, None, 'Central Controller', '2243-422', None),
        Product(0x03, 0x2C, None, 'Central Controller', '2243-442', None),
        Product(0x03, 0x2D, None, 'Central Controller', '2243-522', None),
        Product(0x03, 0x2E, None, 'Hub', '2242-422', None),
        Product(0x03, 0x2F, None, 'Hub', '2242-522', None),
        Product(0x03, 0x30, None, 'Hub', '2242-442', None),
        Product(0x03, 0x31, None, 'Hub', '2242-232', None),
        Product(0x03, 0x32, None, 'Hub', '2242-222', None),
        Product(0x03, 0x33, None, 'Hub', '2245-555', None),
        Product(0x03, 0x34, None, 'Hub', '2245-442', None),
        Product(0x03, 0x35, None, 'Hub', '2245-422', None),
        Product(0x03, 0x36, None, 'Hub', '2245-522', None),
        Product(0x03, 0x37, None, 'Hub', '', None),

        Product(0x04, None, None, 'Generic Irrigation Controler', '', None),
        Product(0x04, 0x00, 0x000001, 'Compacta EZRain Sprinkler Controller', '31270', None),

        Product(0x05, None, None, 'Generic Climate Controller', '', None),
        Product(0x05, 0x00, None, 'Broan SMSC080 Exhaust Fan', '', None),
        Product(0x05, 0x01, 0x000002, 'EZTherm', '', None),
        Product(0x05, 0x02, None, 'Broan SMSC110 Exhaust Fan', '', None),
        Product(0x05, 0x03, 0x00001F, 'Thermostat Adapter', '2441V', None),
        Product(0x05, 0x04, 0x000024, 'EZTherm', '', None),
        Product(0x05, 0x05, 0x000038, 'Broan, Venmar, BEST Rangehoods', '', None),
        Product(0x05, 0x07, None, 'Wireless Thermostat', '2441ZTH', None),
        Product(0x05, 0x08, None, 'Thermostat', '2441TH', None),
        Product(0x05, 0x09, 0x000094, '7 Day Thermostat', '4715', None),
        Product(0x05, 0x0A, None, 'Wireless Thermostat', '2441ZTH', None),
        Product(0x05, 0x0B, None, 'Thermostat', '2441TH', None),
        Product(0x05, 0x0E, None, 'Integrated Remote Control Thermostat', '2491T1E', None),
        Product(0x05, 0x0F, None, 'Thermostat', '2732-422', None),
        Product(0x05, 0x10, None, 'Thermostat', '2732-522', None),
        Product(0x05, 0x11, None, 'Wireless Thermostat', '2732-432', None),
        Product(0x05, 0x12, None, 'Wireless Thermostat', '2732-532', None),
        Product(0x05, 0x13, None, 'Thermostat Heat Pump', '2732-232', None),
        Product(0x05, 0x14, None, 'Thermostat Heat Pump', '2732-432', None),
        Product(0x05, 0x15, None, 'Thermostat Heat Pump', '2732-532', None),
        Product(0x05, 0x16, None, 'Insteon Thermostat', '2441TH', None),
        Product(0x05, 0x17, None, 'Insteon Thermostat', '2732-422', None),
        Product(0x05, 0x18, None, 'Insteon Thermostat', '2732-522', None),

        Product(0x06, None, None, 'Generic Pool Controller', '', None),
        Product(0x06, 0x00, 0x000003, 'EZPool', '', None),

        Product(0x07, None, None, 'Generic Sensor Actuator', '', SensorsActuators),
        Product(0x07, 0x00, None, 'I/O Linc', '2450', SensorsActuators_2450),
        Product(0x07, 0x01, 0x000004, 'EZSns1W', '', SensorsActuators),
        Product(0x07, 0x02, 0x0000012, 'EZIO8T I/O Module', '', SensorsActuators),
        Product(0x07, 0x03, 0x0000005, 'EZIO2X4', '', SensorsActuators),
        Product(0x07, 0x04, 0x0000013, 'EZIO8SA', '', SensorsActuators),
        Product(0x07, 0x05, 0x0000014, 'EZSnsRF', '', SensorsActuators),
        Product(0x07, 0x06, 0x0000015, 'EZISnsRf', '', SensorsActuators),
        Product(0x07, 0x07, 0x0000014, 'EZIO6I', '', SensorsActuators),
        Product(0x07, 0x08, 0x0000014, 'EZIO4O', '', SensorsActuators),
        Product(0x07, 0x09, 0x0000000, 'SynchroLinc', '2423A5', SensorsActuators),
        Product(0x07, 0x0D, None, 'I/O Linc', '2450-50-60', SensorsActuators_2450),
        Product(0x07, 0x0E, None, 'I/O Module', '2248-222', SensorsActuators),
        Product(0x07, 0x0F, None, 'I/O Module', '2248-422', SensorsActuators),
        Product(0x07, 0x10, None, 'I/O Module', '2248-442', SensorsActuators),
        Product(0x07, 0x11, None, 'I/O Module', '2248-522', SensorsActuators),

        Product(0x09, None, None, 'Generic Energy Management Controller', '', None),
        Product(0x09, 0x00, 0x0000006, 'EZEnergy', '', None),
        Product(0x09, 0x01, 0x0000020, 'OnSitePro Leak Detector', '', None),
        Product(0x09, 0x02, 0x0000021, 'OnSitePro Control Valve', '', None),
        Product(0x09, 0x07, 0x0000000, 'iMeter Solo', '2423A1', None),
        Product(0x09, 0x07, 0x000006C, 'iMeter Solo', '2423A1', None),
        Product(0x09, 0x0A, 0x0000000, '220V/240V 30 AMP Load Controller Normally Open', '2477SA1', None),
        Product(0x09, 0x0B, 0x0000000, '220V/240V 30 AMP Load Controller Normally Closed', '2477SA2', None),
        Product(0x09, 0x0D, None, 'Energy Display', '2441TH', None),
        Product(0x09, 0x10, 0x0000090, 'Network Hub', '4700', None),

        Product(0x0E, None, None, 'Generic Window Coverings', '', None),
        Product(0x0E, 0x00, 0x000000B, 'Somfy Drape Controller RF Bridge', '', None),
        Product(0x0E, 0x01, 0x0000000, 'Micro Open/Close', '2444-222', None),
        Product(0x0E, 0x02, 0x0000000, 'Micro Open/Close', '2444-422', None),
        Product(0x0E, 0x03, 0x0000000, 'Micro Open/Close', '2444-522', None),

        Product(0x0F, None, None, 'Generic Plumbing Controller', '', None),
        Product(0x0F, 0x00, 0x000000E, 'Weiland Doors Central Drive and Controller', '', None),
        Product(0x0F, 0x01, 0x000000F, 'Weiland Doors Secondary Central Drive', '', None),
        Product(0x0F, 0x02, 0x0000010, 'Weiland Doors Assist Drive', '', None),
        Product(0x0F, 0x03, 0x0000011, 'Weiland Doors Elevation Drive', '', None),
        Product(0x0F, 0x04, 0x0000000, 'GarageHawk Garage Unit', '', None),
        Product(0x0F, 0x05, 0x0000000, 'GarageHawk Remote Unit', '', None),
        Product(0x0F, 0x06, 0x0000000, 'MorningLinc', '2458A1', None),
        Product(0x0F, 0x07, None, 'Deadbolt', '2863-222', None),
        Product(0x0F, 0x08, None, 'Deadbolt', '2863-422', None),
        Product(0x0F, 0x09, None, 'Deadbolt', '2863-522', None),
        Product(0x0F, 0x0A, 0x0000000, 'Lock Controller', '2862-222', None),

        Product(0x10, None, None, 'Generic Security, Heath and Safety Device', '', SecurityHealthSafety),
        Product(0x10, 0x01, None, 'Motion Sensor', '2420M', SecurityHealthSafety_2842_222),
        Product(0x10, 0x01, None, 'Motion Sensor', '2842-222', SecurityHealthSafety_2842_222),
        Product(0x10, 0x015, None, 'Door Sensor', '2845-522', SecurityHealthSafety_2845_222),
        Product(0x10, 0x02, None, 'Open/Close Sensor', '2421', SecurityHealthSafety),
        Product(0x10, 0x02, None, 'Open/Close Sensor', '2843-222', SecurityHealthSafety),
        Product(0x10, 0x03, 0x0000A0, 'Motion Sensor', '4716', SecurityHealthSafety_2842_222),
        Product(0x10, 0x04, None, 'Motion Sensor', '2842-422', SecurityHealthSafety_2842_222),
        Product(0x10, 0x05, None, 'Motion Sensor', '2842-522', SecurityHealthSafety_2842_222),
        Product(0x10, 0x06, None, 'Open/Close Sensor', '2843-422', SecurityHealthSafety),
        Product(0x10, 0x07, None, 'Open/Close Sensor', '2843-522', SecurityHealthSafety),
        Product(0x10, 0x08, None, 'Leak Sensor', '2852-222', SecurityHealthSafety_2852_222),
        Product(0x10, 0x09, None, 'Door Sensor', '2843-232', SecurityHealthSafety_2845_222),
        Product(0x10, 0x0A, None, 'Smoke Bridge', '2982-222', SecurityHealthSafety_2982_222),
        Product(0x10, 0x11, None, 'Door Sensor', '2845-222', SecurityHealthSafety_2845_222),
        Product(0x10, 0x14, None, 'Door Sensor', '2845-422', SecurityHealthSafety_2845_222),
        Product(0x10, 0x16, None, 'Motion Sensor II', '2844-222', SecurityHealthSafety_2842_222),

        Product(0xFF, 0x00, None, 'Unrecognized INSTEON Device', '', UnknownDevice),
        Product(0xFF, 0x01, None, 'Unknown Device', '', UnknownDevice),
    ]

    def __init__(self):
        """Initialize the INSTEON Product Database (IPDB)."""
        self.log = logging.getLogger(__name__)

    def __len__(self):
        """Return the length of the product database."""
        return len(self.products)

    def __iter__(self):
        """Iterate through the product database."""
        for product in self.products:
            yield product

    def __getitem__(self, key):
        """Return an item from the product database."""
        cat, subcat = key

        for product in self.products:
            if cat == product.cat and subcat == product.subcat:
                return product

        # We failed to find a device in the database, so we will make a best
        # guess from the cat and return the generic class
        #

        for product in self.products:
            if cat == product.cat and product.subcat is None:
                return product

        # We did not find the device or even a generic device of that category
        return Product(cat, subcat, None, None, None, None)
