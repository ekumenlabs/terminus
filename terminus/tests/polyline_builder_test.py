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

import math
import unittest
from custom_assertions_mixin import CustomAssertionsMixin

from shapely.geometry import LineString

from geometry.point import Point
from geometry.line_segment import LineSegment
from geometry.arc import Arc

from models.polyline_builder import PolylineBuilder
from models.street import Street


class PolylineBuilderTest(CustomAssertionsMixin, unittest.TestCase):

    def _road_points(self):
        return [
            Point(0, 0),
            Point(50, -50),
            Point(75, -50),
            Point(100, 0)
        ]

    def test_malformed_paths(self):
        with self.assertRaises(ValueError):
            lane = Street.from_control_points([]).lane_at(0)
            geometry = lane.geometry_using(PolylineBuilder)

        with self.assertRaises(ValueError):
            lane = Street.from_control_points([Point(0, 0)]).lane_at(0)
            geometry = lane.geometry_using(PolylineBuilder)

    def test_elements_single_segment_path(self):
        a, b = self._road_points()[0:2]
        lane = Street.from_control_points([a, b]).lane_at(0)
        geometry = lane.geometry_using(PolylineBuilder)
        expected_elements = [LineSegment(a, b)]
        self.assertEquals(geometry.elements(), expected_elements)

    def test_elements_multiple_segments_path(self):
        [a, b, c, d] = self._road_points()
        lane = Street.from_control_points([a, b, c, d]).lane_at(0)
        geometry = lane.geometry_using(PolylineBuilder)
        expected_elements = [
            LineSegment(a, b),
            LineSegment(b, c),
            LineSegment(c, d)
        ]
        self.assertEquals(geometry.elements(), expected_elements)

    def test_line_interpolation_points_single_segment_path(self):
        a, b = self._road_points()[0:2]
        lane = Street.from_control_points([a, b]).lane_at(0)
        geometry = lane.geometry_using(PolylineBuilder)
        self.assertEquals(geometry.line_interpolation_points(), [a, b])

    def test_line_interpolation_points_multiple_segments_path(self):
        points = self._road_points()
        tuples = map(lambda point: point.to_tuple(), points)
        lane = Street.from_control_points(points).lane_at(0)
        geometry = lane.geometry_using(PolylineBuilder)
        interpolation_points = geometry.line_interpolation_points()
        self.assertEquals(interpolation_points, points)
