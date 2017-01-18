import unittest
import math
from geometry.point import Point


class PointTest(unittest.TestCase):

    def test_distance_same_y(self):
        p = Point(1.0, 0.0)
        self.assertEqual(p.distance_to(Point(-1.0, 0.0)), 2.0)

    def test_distance_same_x(self):
        p = Point(0.0, 1.0)
        self.assertEqual(p.distance_to(Point(0.0, -1.0)), 2.0)

    def test_distance_conmutative(self):
        p1 = Point(1.0, 1.0)
        p2 = Point(-1.0, -1.0)
        self.assertEqual(p1.distance_to(p2), p2.distance_to(p1))

    def test_distance_same_point(self):
        p = Point(1.0, 0.0)
        self.assertEqual(p.distance_to(p), 0.0)

    def test_distance_same_value_point(self):
        p = Point(1.0, 0.0)
        self.assertEqual(p.distance_to(Point(1.0, 0.0)), 0.0)

    def test_yaw(self):
        origin = Point(0.0, 0.0)

        angle = origin.yaw(Point(1.0, 0.0))
        self.assertEqual(0.0, angle)

        angle = origin.yaw(Point(1.0, 1.0))
        self.assertEqual(math.pi / 4.0, angle)

        angle = origin.yaw(Point(0.0, 1.0))
        self.assertEqual(math.pi / 2.0, angle)

        angle = origin.yaw(Point(-1.0, 1.0))
        self.assertEqual(3.0 * math.pi / 4.0, angle)

        angle = origin.yaw(Point(-1.0, 0.0))
        self.assertEqual(math.pi, angle)

        angle = origin.yaw(Point(-1.0, -1.0))
        self.assertEqual(- 3.0 * math.pi / 4.0, angle)

        angle = origin.yaw(Point(0.0, -1.0))
        self.assertEqual(- math.pi / 2.0, angle)

        angle = origin.yaw(Point(1.0, -1.0))
        self.assertEqual(- math.pi / 4.0, angle)
