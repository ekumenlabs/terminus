import unittest

from models.road_node import RoadNode

from geometry.bounding_box import BoundingBox

from geometry.point import Point


class RoadNodeTest(unittest.TestCase):

    def test_bounding_box(self):
        node = RoadNode(Point(-30, 25))
        expected_box = BoundingBox(Point(-40, 15), Point(-20, 35))
        self.assertEqual(node.bounding_box(20), expected_box)

    def test_bounding_box_with_width_equal_to_zero(self):
        node = RoadNode(Point(18, -30))
        expected_box = BoundingBox(Point(18, -30), Point(18, -30))
        self.assertEqual(node.bounding_box(0), expected_box)

    def test_bounding_box_with_negative_width(self):
        node = RoadNode(Point(18, 15))
        self.assertRaises(ValueError, lambda: node.bounding_box(-8))
