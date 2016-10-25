class CityElement(object):
    """A city element is an object that belongs to a city and that may
    be visited by a generator to create the contents for a file.
    We are using a vistor pattern here to do the double-dispatching and
    the entry point is the `accept` message"""

    def accept(self, generator):
        raise NotImplementedError()
