"""Embodies the INSTEON Product Database static data and access methods."""
import logging
import collections

from .unknowndevice import UnknownDevice 
from .generalController import GeneralController
from .dimmableLightingControl import DimmableLightingControl
from .dimmableLightingControl import DimmableLightingControl_2475F
from .switchedLightingControl import SwitchedLightingControl
from .switchedLightingControl import SwitchedLightingControl_2663_222 
from .securityHealthSafety import SecurityHealthSafety, SecurityHealthSafety_2842_222,SecurityHealthSafety_2982_222
from .sensorsActuators import SensorsActuators
from .sensorsActuators import SensorsActuators_2450

# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods

Product = collections.namedtuple('Product', 'cat subcat product_key description model deviceclass')


class IPDB(object):
    """Embodies the INSTEON Product Database static data and access methods."""

    products = [
        Product(None, None, None, '', '', UnknownDevice),
        
        Product(0x00, None, None, 'Generic General Controller', '', GeneralController),
        Product(0x00, 0x04, None, 'ControLinc', '2430', GeneralController),
        Product(0x00, 0x05, None, 'RemoteLink', '2440', GeneralController),
        Product(0x00, 0x06, None, 'Icon Tabletop Controlle', '2830', GeneralController),
        Product(0x00, 0x08, None, 'EZBridge/EZServer', '', GeneralController),
        Product(0x00, 0x09, None, 'SignaLinc RF Signal Enhancer', '2442', GeneralController),
        Product(0x00, 0x0b, 0x000007, 'Balboa Instrument’s Poolux LCD Controller', '', GeneralController),
        Product(0x00, 0x0b, 0x000022, 'Access Point', '2443', GeneralController),
        Product(0x00, 0x0c, 0x000028, 'IES Color Touchscreen','', GeneralController),

        Product(0x01, None, None, 'Generic Dimmable Lighting', '', DimmableLightingControl),
        Product(0x01, 0x00, None, 'LampLinc 3-pin', '2456D3', DimmableLightingControl),
        Product(0x01, 0x01, None, 'SwitchLinc Dimmer (600W)', '2476D', DimmableLightingControl),
        Product(0x01, 0x02, None, 'In-LineLinc Dimmer', '2475D', DimmableLightingControl),
        Product(0x01, 0x03, None, 'Icon Switch Dimmer', '2476D', DimmableLightingControl),
        Product(0x01, 0x04, None, 'SwitchLinc Dimmer (1000W)', '2476DH', DimmableLightingControl),
        Product(0x01, 0x06, None, 'LampLinc 2-pin', '2456D2', DimmableLightingControl),
        Product(0x01, 0x07, None, 'LampLinc Dimmer V2 2-pin', '2856D2', DimmableLightingControl),
        Product(0x01, 0x0d, None, 'SocketLinc Dimmer', '2454D', DimmableLightingControl),
        Product(0x01, 0x0e, None, 'LampLinc Dual Band 2-pin', '2457D2', DimmableLightingControl),
        Product(0x01, 0x13, 0x000032, 'SwitchLinc Dimmer (Lixar)', '2676D-B', DimmableLightingControl),
        Product(0x01, 0x17, None, 'ToggleLinc Dimmer', '2466D', DimmableLightingControl),
        Product(0x01, 0x18, 0x00003F, 'Icon SwitchLinc Dimmer Inline Companiion', '2474D', DimmableLightingControl),
        Product(0x01, 0x1a, 0x00004F, 'In-LineLinc Dimmer', '2475DA1', DimmableLightingControl),
        Product(0x01, 0x1b, 0x000050, 'KeypadLinc Dimmer, 6-button', '2486DWH6', DimmableLightingControl),
        Product(0x01, 0x1b, 0x000051, 'KeypadLinc Dimmer, 8-button', '2486DWH8', DimmableLightingControl),
        Product(0x01, 0x1d, None, 'SwitchLinc Dimmer (1200W)', '2476D', DimmableLightingControl),
        Product(0x01, 0x1e, None, 'Icon Switch Dimmer i2', '2476DB', DimmableLightingControl),
        Product(0x01, 0x1f, None, 'ToggleLinc Dimmer', '2466D', DimmableLightingControl),
        Product(0x01, 0x20, None, 'SwitchLinc Dimmer (600W)', '2477D', DimmableLightingControl),
        Product(0x01, 0x21, None, 'OutletLinc Dimmer', '2472D', DimmableLightingControl),
        Product(0x01, 0x22, None, 'LampLinc 2-pin', '2457D2X', DimmableLightingControl),
        Product(0x01, 0x23, None, 'LampLinc EZ', '2457D2', DimmableLightingControl),
        Product(0x01, 0x24, None, 'SwitchLinc 2-wire Dimmer', '2474D', DimmableLightingControl),
        Product(0x01, 0x25, None, 'Ballast Dimmer', '2475DA2', DimmableLightingControl),
        Product(0x01, 0x2e, None, 'FanLinc Dual Band', '2475F', DimmableLightingControl_2475F),
        Product(0x01, 0x31, None, 'SwitchLinc Dimmer 240V', '2478D', DimmableLightingControl),
        Product(0x01, 0x32, None, 'In-LineLinc Dimmer', '2457D2', DimmableLightingControl),
        Product(0x01, 0x34, None, 'DIN Rail Dimmer', '2542-222', DimmableLightingControl),
        Product(0x01, 0x35, None, 'Micro Dimmer', '2442-222', DimmableLightingControl),
        Product(0x01, 0x3a, None, 'LED Bulb', '2672-222', DimmableLightingControl),
        Product(0x01, 0x41, None, 'KeypadLinc Dimmer, 8 button', '2334-222', DimmableLightingControl),
        Product(0x01, 0x42, None, 'KeypadLinc Dimmer, 6 button', '2334-232', DimmableLightingControl),
        Product(0x01, 0x49, None, 'Recessed LED Bulb', '2674-222', DimmableLightingControl),

        Product(0x02, None, None, 'Generic Switched Lighting', '', SwitchedLightingControl),
        Product(0x02, 0x06, None, 'ApplianceLinc Outdoor 3-pin', '2456S3E', SwitchedLightingControl),
        Product(0x02, 0x08, None, 'OutletLinc', '2473S', SwitchedLightingControl),
        Product(0x02, 0x09, None, 'ApplianceLinc 3-pin', '2456S3', SwitchedLightingControl),
        Product(0x02, 0x10, None, 'In-LineLinc Relay', '2475S', SwitchedLightingControl),
        Product(0x02, 0x12, None, 'Icon SwitchLinc Relay Inline Companion', '2474S', SwitchedLightingControl),
        Product(0x02, 0x13, None, 'Icon SwitchLinc Relay (Lixar)', '2676R-B', SwitchedLightingControl),
        Product(0x02, 0x14, None, 'In-LineLinc Relay with Sense', '2475S2', SwitchedLightingControl),
        Product(0x02, 0x0a, None, 'SwitchLinc Relay', '2476S', SwitchedLightingControl),
        Product(0x02, 0x0b, None, 'Icon Relay On-Off', '2876SB', SwitchedLightingControl),
        Product(0x02, 0x0c, None, 'Icon Appliance Module 3-pin', '2856SB', SwitchedLightingControl),
        Product(0x02, 0x0d, None, 'ToggleLinc Relay', '2466S', SwitchedLightingControl),
        Product(0x02, 0x0e, None, 'SwitchLinc Relay Timer', '2476ST', SwitchedLightingControl),
        Product(0x02, 0x16, None, 'Icon Relay On-Off', '2876SB', SwitchedLightingControl),
        Product(0x02, 0x17, None, 'Icon Appliance Module', '2856SB', SwitchedLightingControl),
        Product(0x02, 0x1a, None, 'ToggleLinc Relay', '2466SW', SwitchedLightingControl),
        Product(0x02, 0x1f, None, 'In-LineLinc Relay', '2475SDB', SwitchedLightingControl),
        Product(0x02, 0x2a, None, 'SwitchLinc Switch', '2477S', SwitchedLightingControl),
        Product(0x02, 0x2e, None, 'DIN Rail On/Off', '2453-222', SwitchedLightingControl),
        Product(0x02, 0x2f, None, 'Micro On/Off', '2443-222', SwitchedLightingControl),
        Product(0x02, 0x37, None, 'On/Off Module', '2635-222', SwitchedLightingControl),
        Product(0x02, 0x38, None, 'On/Off Outdoor Module', '2634-222', SwitchedLightingControl),
        Product(0x02, 0x39, None, 'On/Off Outlet', '2663-222', SwitchedLightingControl_2663_222),

        Product(0x03, None, None, 'Generic PLM', '', None),
        Product(0x03, 0x15, None, 'PowerLinc Modem (USB)', '2413U', None),  # PLM
        Product(0x03, 0x20, None, 'USB Adapter', '2448A7', None), # PLM

        Product(0x05, 0x0b, None, 'Thermostat', '2441TH', None), #<- Coming Soon!

        Product(0x07, 0x00, None, 'I/O Linc', '2450', SensorsActuators_2450),

        Product(0x09, 0x0a, None, '220/240V 30A Load Controller NO', '2477SA1', None),
        Product(0x09, 0x0b, None, '220/240V 30A Load Controller NC', '2477SA2', None),

        
        Product(0x10, None, None, 'Generic Security, Heath and Safety Device', '', SecurityHealthSafety),
        Product(0x10, 0x01, None, 'Motion Sensor', '2842-222', SecurityHealthSafety_2842_222),
        Product(0x10, 0x02, None, 'TriggerLinc', '2421', SecurityHealthSafety),
        Product(0x10, 0x08, None, 'Water Leak Sensor', '2852-222', SecurityHealthSafety),
        Product(0x10, 0x0a, None, 'Smoke Bridge', '2982-222', SecurityHealthSafety_2982_222),
        Product(0x10, 0x11, None, 'Hidden Door Sensor', '2845-222', SecurityHealthSafety),
        Product(0x0f, 0x06, None, 'MorningLinc', '2458A1', None),
    ]

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def __len__(self):
        return len(self.products)

    def __iter__(self):
        for product in self.products:
            yield product

    def __getitem__(self, key):
        cat, subcat = key

        for product in self.products:
            if cat == product.cat and subcat == product.subcat:
                return product

        # We failed to find a device in the database, so we will make a best
        # guess from the cat and return the generic class
        #
        
        for product in self.products:
            if cat == product.cat and product.subcat == None:
                return product

        # We did not find the device or even a generic device of that category
        return Product(cat, subcat, None, None, None, None) 
