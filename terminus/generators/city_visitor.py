class CityVisitor(object):

    def __init__(self, city):
        self.city = city

    def run(self):
        self.city.accept(self)

    # Double-dispatching methods. By default do nothing. Override in subclasses
    # to build the required file contents

    def start_city(self, city):
        pass

    def end_city(self, city):
        pass

    def start_street(self, street):
        pass

    def end_street(self, street):
        pass

    def start_trunk(self, trunk):
        pass

    def end_trunk(self, trunk):
        pass

    def start_ground_plane(self, plane):
        pass

    def end_ground_plane(self, plane):
        pass

    def start_block(self, block):
        pass

    def end_block(self, block):
        pass

    def start_building(self, building):
        pass

    def end_building(self, building):
        pass
