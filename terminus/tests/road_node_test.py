"""
Copyright (C) 2017 Open Source Robotics Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest

from geometry.bounding_box import BoundingBox
from geometry.point import Point

from models.road_node import RoadNode


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
