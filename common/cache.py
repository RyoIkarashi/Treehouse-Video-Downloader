from threading import Timer

""" simple in-memory cache """
class Cache:
    def __init__(self):
        self.cache = {}

    def set(self, name, data, ttl = 0):
        self.cache[name] = data

        if(ttl > 0):
            Timer(ttl, self._evit, args = [name]).start()

    def get(self, name):
        try:
            return self.cache[name]
        except KeyError:
            return None

    def evit(self, name):
        try:
            del self.cache[name]
        except KeyError:
            print("where it go?")
