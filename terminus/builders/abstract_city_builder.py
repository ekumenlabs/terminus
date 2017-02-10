class AbstractCityBuilder(object):

    def name(self):
        return self.__class__.__name__

    def get_city(self):
        raise NotImplementedError()
