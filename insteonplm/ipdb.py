"""Embodies the INSTEON Product Database static data and access methods."""
import logging
import collections

# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods

Product = collections.namedtuple('Product', 'cat subcat product_key description model capabilities')


class IPDB(object):
    """Embodies the INSTEON Product Database static data and access methods."""

    products = [
        Product(0x01, 0x00, None, 'LampLinc 3-pin', '2456D3', ['light', 'dimmer']),
        Product(0x01, 0x01, None, 'SwitchLinc Dimmer (600W)', '2476D', ['light', 'dimmer']),
        Product(0x01, 0x02, None, 'In-LineLinc Dimmer', '2475D', ['light', 'dimmer']),
        Product(0x01, 0x03, None, 'Icon Switch Dimmer', '2476D', ['light', 'dimmer']),
        Product(0x01, 0x04, None, 'SwitchLinc Dimmer (1000W)', '2476DH', ['light', 'dimmable']),
        Product(0x01, 0x06, None, 'LampLinc 2-pin', '2456D2', ['light', 'dimmer']),
        Product(0x01, 0x07, None, 'LampLinc Dimmer V2 2-pin', '2856D2', ['light', 'dimmable']),
        Product(0x01, 0x0d, None, 'SocketLinc Dimmer', '2454D', ['light', 'dimmable']),
        Product(0x01, 0x0e, None, 'LampLinc Dual Band 2-pin', '2457D2', ['light', 'dimmable']),
        Product(0x01, 0x13, 0x000032, 'SwitchLinc Dimmer (Lixar)', '2676D-B', ['light', 'dimmer']),
        Product(0x01, 0x17, None, 'ToggleLinc Dimmer', '2466D', ['light', 'dimmer']),
        Product(0x01, 0x18, 0x00003F, 'Icon SwitchLinc Dimmer Inline Companiion', '2474D', ['light', 'dimmer']),
        Product(0x01, 0x1a, 0x00004F, 'In-LineLinc Dimmer', '2475DA1', ['light', 'dimmable']),
        Product(0x01, 0x1b, 0x000050, 'KeypadLinc Dimmer, 6-button', '2486DWH6', ['light', 'dimmable']),
        Product(0x01, 0x1b, 0x000051, 'KeypadLinc Dimmer, 8-button', '2486DWH8', ['light', 'dimmable']),
        Product(0x01, 0x1d, None, 'SwitchLinc Dimmer (1200W)', '2476D', ['light', 'dimmable']),
        Product(0x01, 0x1e, None, 'Icon Switch Dimmer i2', '2476DB', ['light', 'dimmer']),
        Product(0x01, 0x1f, None, 'ToggleLinc Dimmer', '2466D', ['light', 'dimmer']),
        Product(0x01, 0x20, None, 'SwitchLinc Dimmer (600W)', '2477D', ['light', 'dimmable']),
        Product(0x01, 0x21, None, 'OutletLinc Dimmer', '2472D', ['light', 'dimmable']),
        Product(0x01, 0x22, None, 'LampLinc 2-pin', '2457D2X', ['light', 'dimmer']),
        Product(0x01, 0x23, None, 'LampLinc EZ', '2457D2', ['light', 'dimmer']),
        Product(0x01, 0x24, None, 'SwitchLinc 2-wire Dimmer', '2474D', ['light', 'dimmer']),
        Product(0x01, 0x25, None, 'Ballast Dimmer', '2475DA2', ['light', 'dimmable']),
        Product(0x01, 0x2e, None, 'FanLinc Dual Band', '2475F', ['light', 'dimmable']),
        Product(0x01, 0x31, None, 'SwitchLinc Dimmer 240V', '2478D', ['light', 'dimmer']),
        Product(0x01, 0x32, None, 'In-LineLinc Dimmer', '2457D2', ['light', 'dimmable']),
        Product(0x01, 0x34, None, 'DIN Rail Dimmer', '2542-222', ['light', 'dimmable']),
        Product(0x01, 0x35, None, 'Micro Dimmer', '2442-222', ['light', 'dimmable']),
        Product(0x01, 0x3a, None, 'LED Bulb', '2672-222', ['light', 'dimmable']),
        Product(0x01, 0x41, None, 'KeypadLinc Dimmer, 8 button', '2334-222', ['light', 'dimmable']),
        Product(0x01, 0x42, None, 'KeypadLinc Dimmer, 6 button', '2334-232', ['light', 'dimmable']),
        Product(0x01, 0x49, None, 'Recessed LED Bulb', '2674-222', ['light', 'dimmable']),

        Product(0x02, 0x06, None, 'ApplianceLinc Outdoor 3-pin', '2456S3E', ['switch']),
        Product(0x02, 0x08, None, 'OutletLinc', '2473S', ['switch']),
        Product(0x02, 0x09, None, 'ApplianceLinc 3-pin', '2456S3', ['switch']),
        Product(0x02, 0x10, None, 'In-LineLinc Relay', '2475S', ['switch']),
        Product(0x02, 0x12, None, 'Icon SwitchLinc Relay Inline Companion', '2474S', ['switch']),
        Product(0x02, 0x13, None, 'Icon SwitchLinc Relay (Lixar)', '2676R-B', ['switch']),
        Product(0x02, 0x14, None, 'In-LineLinc Relay with Sense', '2475S2', ['switch']),
        Product(0x02, 0x0a, None, 'SwitchLinc Relay', '2476S', ['light']),
        Product(0x02, 0x0b, None, 'Icon Relay On-Off', '2876SB', ['light']),
        Product(0x02, 0x0c, None, 'Icon Appliance Module 3-pin', '2856SB', ['switch']),
        Product(0x02, 0x0d, None, 'ToggleLinc Relay', '2466S', ['light']),
        Product(0x02, 0x0e, None, 'SwitchLinc Relay Timer', '2476ST', ['switch']),
        Product(0x02, 0x16, None, 'Icon Relay On-Off', '2876SB', ['light']),
        Product(0x02, 0x17, None, 'Icon Appliance Module', '2856SB', ['switch']),
        Product(0x02, 0x1a, None, 'ToggleLinc Relay', '2466SW', ['switch']),
        Product(0x02, 0x1f, None, 'In-LineLinc Relay', '2475SDB', ['switch']),
        Product(0x02, 0x2a, None, 'SwitchLinc Switch', '2477S', ['light']),
        Product(0x02, 0x2e, None, 'DIN Rail On/Off', '2453-222', ['switch']),
        Product(0x02, 0x2f, None, 'Micro On/Off', '2443-222', ['switch']),
        Product(0x02, 0x37, None, 'On/Off Module', '2635-222', ['switch']),
        Product(0x02, 0x38, None, 'On/Off Outdoor Module', '2634-222', ['switch']),
        Product(0x02, 0x39, None, 'On/Off Outlet', '2663-222', ['switch']),

        Product(0x05, 0x0b, None, 'Thermostat', '2441TH', ['climate']), #<- Coming Soon!

        Product(0x07, 0x00, None, 'I/O Linc', '2450', ['switch', 'binary_sensor', 'relay']),

        Product(0x09, 0x0a, None, '220/240V 30A Load Controller NO', '2477SA1', ['switch']),
        Product(0x09, 0x0b, None, '220/240V 30A Load Controller NC', '2477SA2', ['switch']),

        Product(0x10, 0x01, None, 'Motion Sensor', '2842-222', ['binary_sensor']),
        Product(0x10, 0x02, None, 'TriggerLinc', '2421', ['binary_sensor']),
        Product(0x10, 0x08, None, 'Water Leak Sensor', '2852-222', ['binary_sensor']),
        Product(0x10, 0x11, None, 'Hidden Door Sensor', '2845-222', ['binary_sensor', 'no_requests']),

        Product(0x0f, 0x06, None, 'MorningLinc', '2458A1', ['switch']),
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
        # guess from the cat/subcat.
        #
        name = 'Unknown Device'
        capabilities = []

        if cat == 0x01:
            name = 'Unknown Dimmer'
            capabilities.append('light')
            capabilities.append('dimmer')

        if cat == 0x02:
            name = 'Unknown Device'
            capabilities.append('switch')

        if cat == 0x10:
            name = 'Unknown Sensor'
            capabilities.append('binary_sensor')

        return Product(cat, subcat, None, name, None, capabilities)
