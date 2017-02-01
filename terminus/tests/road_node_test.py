import unittest

from models.road_node import RoadNode

from geometry.bounding_box import BoundingBox

from geometry.point import Point


class RoadNodeTest(unittest.TestCase):

    def test_road_node_bounding_box(self):
        node = RoadNode(Point(-30, 25))
        expected_box = BoundingBox(Point(-40, 15), Point(-20, 35))
        self.assertEqual(node.road_node_bounding_box(20), expected_box)
