import logging

class MockCallbacks(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.callbackvalue1 = None
        self.callbackvalue2 = None
        self.callbackvalue3 = None
        self.callbackvalue4 = None
        self.callbackvalue5 = None
        self.callbackvalue6 = None
        self.callbackvalue7 = None
        self.callbackvalue8 = None
        self.callbackvalue9 = None
    
    def callbackmethod1(self, id, state, value):
        self.log.debug('Called method 1 callback')
        self.callbackvalue1 = value
    
    def callbackmethod2(self, id, state, value):
        self.log.debug('Called method 2 callback')
        self.callbackvalue2 = value
    
    def callbackmethod3(self, id, state, value):
        self.log.debug('Called method 3 callback')
        self.callbackvalue3 = value
    
    def callbackmethod4(self, id, state, value):
        self.log.debug('Called method 4 callback')
        self.callbackvalue4 = value
    
    def callbackmethod5(self, id, state, value):
        self.log.debug('Called method 5 callback')
        self.callbackvalue5 = value
    
    def callbackmethod6(self, id, state, value):
        self.log.debug('Called method 6 callback')
        self.callbackvalue6 = value
    
    def callbackmethod7(self, id, state, value):
        self.log.debug('Called method 7 callback')
        self.callbackvalue7 = value
    
    def callbackmethod8(self, id, state, value):
        self.log.debug('Called method 8 callback')
        self.callbackvalue8 = value
    
    def callbackmethod9(self, id, state, value):
        self.log.debug('Called method 9 callback')
        self.callbackvalue9 = value