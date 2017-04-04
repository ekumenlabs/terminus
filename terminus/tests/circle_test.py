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
from geometry.point import Point
from geometry.circle import Circle


class CircleTest(unittest.TestCase):

    def test_intersection_at_one_point(self):
        circle1 = Circle(Point(0, 0), 2)
        circle2 = Circle(Point(3, 0), 1)
        self.assertEqual(circle1.intersection(circle2), [Point(2, 0)])

    def test_intersection_at_one_point_in_nested_circles(self):
        circle1 = Circle(Point(0, 0), 4)
        circle2 = Circle(Point(2, 0), 2)
        self.assertEqual(circle1.intersection(circle2), [Point(4, 0)])

    def test_intersection_at_two_points(self):
        circle1 = Circle(Point(-3, 0), 5)
        circle2 = Circle(Point(3, 0), 5)
        self.assertEqual(circle1.intersection(circle2), [Point(0, 4), Point(0, -4)])
