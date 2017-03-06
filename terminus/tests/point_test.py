"""
/*
 * Copyright (C) 2017 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
"""
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

    def test_cross_product(self):
        self.assertEquals(Point(3, 0, 0).cross_product(Point(0, 4, 0)),
                          Point(0, 0, 12))
        self.assertEquals(Point(1, 2, 3).cross_product(Point(4, 5, 6)),
                          Point(-3, 6, -3))

    def test_squared_distance_to(self):
        self.assertEquals(0, Point(1, 2).squared_distance_to(Point(1, 2)))
        self.assertEquals(1, Point(1, 0).squared_distance_to(Point(2, 0)))
        self.assertEquals(4, Point(1, 0).squared_distance_to(Point(3, 0)))
        self.assertEquals(8, Point(0, 0).squared_distance_to(Point(2, 2)))

    def test_norm(self):
        self.assertEquals(Point(0, 0, 0).norm(), 0)
        self.assertEquals(Point(1, 0, 0).norm(), 1)
        self.assertEquals(Point(0, 1, 0).norm(), 1)
        self.assertEquals(Point(0, 0, 1).norm(), 1)
        self.assertAlmostEquals(Point(1, 1, 0).norm(), 1.41421356)
        self.assertAlmostEquals(Point(0, 1, 1).norm(), 1.41421356)
        self.assertAlmostEquals(Point(1, 0, 1).norm(), 1.41421356)
        self.assertAlmostEquals(Point(1, 1, 1).norm(), 1.73205080)
