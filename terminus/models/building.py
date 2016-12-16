from city_model import CityModel
from geometry.point import Point


# TODO: separate concepts of origin and translation vector for the pose.
class Building(CityModel):
    def __init__(self, origin, vertices, height=10, name=None):
        """
        Generates a building with a base shape given by the vertices list
        and extruded the given height, located at position 'origin'.
        """
        super(Building, self).__init__(name)
        self.origin = origin
        self.vertices = vertices
        self.height = height

    @staticmethod
    def square(origin, size, height):
        """
        Generate a square building of the given lateral size, height and
        centered in the given position.
        """
        w = size / 2.0
        vertices = [
            Point(w, w, 0),
            Point(-w, w, 0),
            Point(-w, -w, 0),
            Point(w, -w, 0)
        ]
        return Building(origin, vertices, height)

    def accept(self, generator):
        generator.start_building(self)
        generator.end_building(self)
