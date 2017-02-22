from city_model import CityModel
from geometry.bounding_box import BoundingBox
from geometry.point import Point


class GroundPlane(CityModel):
    def __init__(self, size, origin, name=None):
        super(GroundPlane, self).__init__(name)
        self.size = size
        self.origin = origin

    def bounding_box(self):
        box_origin = Point(-self.size / 2.0, -self.size / 2.0)
        box_corner = Point(self.size / 2.0, self.size / 2.0)
        box = BoundingBox(box_origin, box_corner)
        return box.translate(self.origin)

    def accept(self, generator):
        generator.start_ground_plane(self)
        generator.end_ground_plane(self)
