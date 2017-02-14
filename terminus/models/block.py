from city_model import CityModel
from geometry.point import Point
from geometry.bounding_box import BoundingBox


class Block(CityModel):
    def __init__(self, origin, vertices, height=0.15, name=None):
        """
        Generates one block of a city with a shape defined by an array of
        vertices and the specified height.
        """
        super(Block, self).__init__(name)
        self.origin = origin
        self.height = height
        self.vertices = vertices

    @staticmethod
    def square(origin, size):
        """
        Generate a square block of the given size and in the given position.
        """
        w = size / 2.0
        vertices = [
            Point(w, w, 0),
            Point(-w, w, 0),
            Point(-w, -w, 0),
            Point(w, -w, 0)
        ]
        return Block(origin, vertices)

    def accept(self, generator):
        generator.start_block(self)
        generator.end_block(self)

    def bounding_box(self):
        box_list = map(lambda vertex: BoundingBox(vertex, vertex), self.vertices)
        return BoundingBox.from_boxes(box_list).translate(self.origin)
