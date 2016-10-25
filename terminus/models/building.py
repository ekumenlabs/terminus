from city_model import CityModel


class Building(CityModel):
    def __init__(self, origin, size, height, name=None):
        """
        Generates a square building of base (size * size) and the given height,
        located at position 'origin'.
        """
        super(Building, self).__init__(name)
        self.origin = origin
        self.size = size
        self.height = height

    def box_base(self):
        return self.origin.z + self.height / 2

    def accept(self, generator):
        generator.start_building(self)
        generator.end_building(self)
