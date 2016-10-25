from city_model import CityModel


class GroundPlane(CityModel):
    def __init__(self, size, origin, name=None):
        super(GroundPlane, self).__init__(name)
        self.size = size
        self.origin = origin

    def accept(self, generator):
        generator.start_ground_plane(self)
        generator.end_ground_plane(self)
