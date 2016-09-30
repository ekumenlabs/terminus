from models.point import Point
from models.block import Block

class SquareBlockBuilder(object):
    def gen_block(self, origin, size):
        """
        Generate a square block of the given size and in the given position.
        """
        w = size / 2.0
        vertices = [Point(w, w, 0), Point(-w, w, 0), Point(-w, -w, 0), Point(w, -w, 0)]
        return Block(origin, vertices)
