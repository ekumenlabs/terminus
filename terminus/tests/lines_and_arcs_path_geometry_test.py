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

from models.lines_and_arcs_builder import LinesAndArcsBuilder


class LinesAndArcsBuilderTest(CustomAssertionsMixin, unittest.TestCase):

    def test_malformed_paths(self):
        with self.assertRaises(ValueError):
            LinesAndArcsBuilder([]).build_path_geometry()

        with self.assertRaises(ValueError):
            LinesAndArcsBuilder([Point(0, 0)]).build_path_geometry()

    def test_elements_single_segment_path(self):
        a = Point(0, 0)
        b = Point(50, -50)
        geometry = LinesAndArcsBuilder([a, b]).build_path_geometry()
        expected_elements = [LineSegment(a, b)]
        self.assertAlmostEqual(geometry.elements(), expected_elements)

    def test_elements_two_collinear_segment_path(self):
        a = Point(0, 0)
        b = Point(50, -50)
        c = Point(100, -100)
        geometry = LinesAndArcsBuilder([a, b, c]).build_path_geometry()
        expected_elements = [LineSegment(a, c)]
        self.assertAlmostEqual(geometry.elements(), expected_elements)

    def test_elements_two_non_collinear_segment_path(self):
        a = Point(0, 0)
        b = Point(50, 0)
        c_up = Point(100, 10)
        c_down = Point(100, -10)

        geometry = LinesAndArcsBuilder([a, b, c_up]).build_path_geometry()
        expected_elements = [
            LineSegment(a, Point(45.0, 0.0)),
            Arc(Point(45.0, 0.0), 0.0, 50.49509756, 11.30993247),
            LineSegment(Point(54.90290337, 0.98058067), c_up)]
        self.assertAlmostEqual(geometry.elements(), expected_elements)

        geometry = LinesAndArcsBuilder([a, b, c_down]).build_path_geometry()
        expected_elements = [
            LineSegment(a, Point(45.0, 0.0)),
            Arc(Point(45.0, 0.0), 0.0, 50.49509756, -11.30993247),
            LineSegment(Point(54.90290337, -0.98058067), c_down)]
        self.assertAlmostEqual(geometry.elements(), expected_elements)

    def test_elements_S_path(self):
        a = Point(0, 0)
        b = Point(50, 0)
        c = Point(50, 20)
        d = Point(100, 20)

        geometry = LinesAndArcsBuilder([a, b, c, d]).build_path_geometry()

        expected_elements = [
            LineSegment(a, Point(45, 0)),
            Arc(Point(45, 0), 0, 5, 90),
            LineSegment(Point(50, 5), Point(50, 15)),
            Arc(Point(50, 15), 90, 5, -90),
            LineSegment(Point(55, 20), d)]
        self.assertAlmostEqual(geometry.elements(), expected_elements)

    def test_elements_short_S_path(self):
        a = Point(0, 0)
        b = Point(50, 0)
        c = Point(50, 10)
        d = Point(100, 10)

        geometry = LinesAndArcsBuilder([a, b, c, d]).build_path_geometry()

        expected_elements = [
            LineSegment(a, Point(45, 0)),
            Arc(Point(45, 0), 0, 5, 90),
            Arc(Point(50, 5), 90, 5, -90),
            LineSegment(Point(55, 10), d)]
        self.assertAlmostEqual(geometry.elements(), expected_elements)

    def test_elements_very_short_S_path(self):
        a = Point(0, 0)
        b = Point(50, 0)
        c = Point(50, 7)
        d = Point(100, 7)

        geometry = LinesAndArcsBuilder([a, b, c, d]).build_path_geometry()

        expected_elements = [
            LineSegment(a, Point(46.5, 0)),
            Arc(Point(46.5, 0), 0, 3.5, 90),
            Arc(Point(50, 3.5), 90, 3.5, -90),
            LineSegment(Point(53.5, 7), d)]
        self.assertAlmostEqual(geometry.elements(), expected_elements)

    def test_elements_heading_signle_segment_path(self):
        a = Point(0, 0)
        b = Point(50, -50)

        geometry = LinesAndArcsBuilder([a, b]).build_path_geometry()
        elements = geometry.elements()

        self.assertAlmostEqual(geometry.elements()[0].start_heading(), -45)
        self.assertAlmostEqual(geometry.elements()[0].end_heading(), -45)

    def test_elements_heading_two_collinear_segment_path(self):
        a = Point(0, 0)
        b = Point(50, 50)
        c = Point(100, 100)

        geometry = LinesAndArcsBuilder([a, b, c]).build_path_geometry()
        elements = geometry.elements()

        self.assertAlmostEqual(elements[0].start_heading(), 45)
        self.assertAlmostEqual(elements[0].end_heading(), 45)

    def test_elements_heading_two_non_collinear_segment_path(self):
        a = Point(0, 0)
        b = Point(50, 0)
        c = Point(60, 10)

        geometry = LinesAndArcsBuilder([a, b, c]).build_path_geometry()
        elements = geometry.elements()

        self.assertAlmostEqual(elements[0].start_heading(), 0)
        self.assertAlmostEqual(elements[0].end_heading(), 0)
        self.assertAlmostEqual(elements[1].start_heading(), 0)
        self.assertAlmostEqual(elements[1].end_heading(), 45)
        self.assertAlmostEqual(elements[2].start_heading(), 45)
        self.assertAlmostEqual(elements[2].end_heading(), 45)

    def test_elements_heading_S_path(self):
        a = Point(0, 0)
        b = Point(50, 0)
        c = Point(50, 20)
        d = Point(100, 20)

        geometry = LinesAndArcsBuilder([a, b, c, d]).build_path_geometry()
        elements = geometry.elements()

        self.assertAlmostEqual(elements[0].start_heading(), 0)
        self.assertAlmostEqual(elements[0].end_heading(), 0)
        self.assertAlmostEqual(elements[1].start_heading(), 0)
        self.assertAlmostEqual(elements[1].end_heading(), 90)
        self.assertAlmostEqual(elements[2].start_heading(), 90)
        self.assertAlmostEqual(elements[2].end_heading(), 90)
        self.assertAlmostEqual(elements[3].start_heading(), 90)
        self.assertAlmostEqual(elements[3].end_heading(), 0)
        self.assertAlmostEqual(elements[4].start_heading(), 0)
        self.assertAlmostEqual(elements[4].end_heading(), 0)
