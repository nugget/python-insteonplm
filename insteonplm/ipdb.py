import asyncio
import logging
import binascii
import collections

Product = collections.namedtuple('Product', 'cat subcat product_key description model capabilities')

class IPDB(object):
    products = [
        Product(0x01, 0x07, None, 'LampLinc Dimmer V2 2-pin', '2856D2', ['light', 'dimmable']),
        Product(0x01, 0x25, None, 'Ballast Dimmer', '2475DA2', ['light', 'dimmable']),
        Product(0x01, 0x34, None, 'DIN Rail Dimmer', '2542-222', ['light', 'dimmable']),
        Product(0x01, 0x04, None, 'SwitchLinc Dimmer (1000W)', '2476DH', ['light', 'dimmable']),
        Product(0x01, 0x20, None, 'SwitchLinc Dimmer (600W)', '2477D', ['light', 'dimmable']),
        Product(0x01, 0x1d, None, 'SwitchLinc Dimmer (1200W)', '2476D', ['light', 'dimmable']),

        Product(0x02, 0x0a, None, 'SwitchLinc Relay', '2476S', ['light']),
        Product(0x02, 0x2a, None, 'SwitchLinc Switch', '2477S', ['light']),

        Product(0x07, 0x00, None, 'I/O Linc', '2450', ['switch', 'binary_sensor', 'relay']),
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

        return Product(cat, subcat, None, name, None, capabilities)
