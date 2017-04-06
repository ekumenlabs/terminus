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
            PolylineBuilder([]).build_path_geometry()

        with self.assertRaises(ValueError):
            PolylineBuilder([Point(0, 0)]).build_path_geometry()

    def test_elements_single_segment_path(self):
        a, b = self._road_points()[0:2]
        geometry = PolylineBuilder([a, b]).build_path_geometry()
        expected_elements = [LineSegment(a, b)]
        self.assertEquals(geometry.elements(), expected_elements)

    def test_elements_multiple_segments_path(self):
        [a, b, c, d] = self._road_points()
        geometry = PolylineBuilder([a, b, c, d]).build_path_geometry()
        expected_elements = [
            LineSegment(a, b),
            LineSegment(b, c),
            LineSegment(c, d)
        ]
        self.assertEquals(geometry.elements(), expected_elements)

    def test_to_line_string_single_segment_path(self):
        a, b = self._road_points()[0:2]
        geometry = PolylineBuilder([a, b]).build_path_geometry()
        expected_line_string = LineString([a.to_tuple(), b.to_tuple()])
        self.assertEquals(geometry.to_line_string(), expected_line_string)

    def test_to_line_string_multiple_segments_path(self):
        points = self._road_points()
        tuples = map(lambda point: point.to_tuple(), points)
        geometry = PolylineBuilder(points).build_path_geometry()
        geometry_line_string = geometry.to_line_string()
        self.assertEquals(len(geometry_line_string.coords), 4)
        expected_line_string = LineString(tuples)
        self.assertTrue(geometry.to_line_string().equals(expected_line_string))
