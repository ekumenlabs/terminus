import unittest

import math

from geometry.point import Point
from geometry.line import Line


class LineTest(unittest.TestCase):

    def test_intersection(self):
        line = Line.from_points(Point(0, 0), Point(1, 1))

        test_line = Line.from_points(Point(0, -1), Point(0, 1))
        self.assertEquals(line.intersection(test_line), Point(0, 0))

        test_line = Line.from_points(Point(-1, 1), Point(-1, 2))
        self.assertEquals(line.intersection(test_line), Point(-1, -1))

        test_line = Line.from_points(Point(2, 1), Point(0, 3))
        self.assertEquals(line.intersection(test_line), Point(1.5, 1.5))

        # Parallel lines
        test_line = Line.from_points(Point(1, 1), Point(2, 2))
        self.assertEquals(line.intersection(test_line), None)

        # Same lines
        test_line = Line.from_points(Point(-1, -1), Point(0, 0))
        self.assertEquals(line.intersection(test_line), None)
