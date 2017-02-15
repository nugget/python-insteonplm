import asyncio
import logging
import binascii
import collections

Product = collections.namedtuple('Product', ['cat', 'subcat', 'product_key', 'description', 'model', 'capabilities'])

class IPDB(object):
    products = []
    products.append(Product(0x01,0x07,None,'LampLinc Dimmer V2 2-pin', '2856D2',['light','dimmable']))
    products.append(Product(0x01,0x20,None,'SwitchLinc Dimmer (600W)', '2477D',['light','dimmable']))
    products.append(Product(0x07,0x00,None,'I/O Linc', '2450',['switch','binary_sensor']))

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def __len__(self):
        return len(self.products)

    def __iter__(self):
        for x in self.products:
            yield x

    def __getitem__(self, key):
        cat, subcat = key

        for x in self.products:
            if cat == x.cat and subcat == x.subcat:
               return x

        return Product(cat,subcat,None,'Unknown Device', None, [])
