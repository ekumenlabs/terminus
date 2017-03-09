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
import mock

from geometry.point import Point
from geometry.bounding_box import BoundingBox
from models.ground_plane import GroundPlane


class GroundPlaneTest(unittest.TestCase):

    def test_accept(self):
        plane = GroundPlane(1, Point(0, 0, 0))
        generator_mock = mock.Mock()
        calls = [mock.call.start_ground_plane(plane), mock.call.end_ground_plane(plane)]
        plane.accept(generator_mock)
        generator_mock.assert_has_calls(calls)

    def test_bounding_box_with_origin_at_0_0(self):
        ground_plane = GroundPlane(10, Point(0, 0))
        expected_box = BoundingBox(Point(-5, -5), Point(5, 5))
        self.assertEqual(ground_plane.bounding_box(), expected_box)

    def test_bounding_box_with_origin_not_at_0_0(self):
        ground_plane = GroundPlane(20, Point(-5, 30))
        expected_box = BoundingBox(Point(-15, 20), Point(5, 40))
