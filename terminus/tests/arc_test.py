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
from custom_assertions_mixin import CustomAssertionsMixin

from math import *

from geometry.point import Point
from geometry.arc import Arc


class ArcTest(CustomAssertionsMixin, unittest.TestCase):

    def test_null_arc_end_point(self):
        null_arc = Arc(Point(0, 0), 90, 10, 0)
        self.assertAlmostEqual(null_arc.end_point(), Point(0, 0))

    def test_axis_aligned_arc_end_point(self):

        # Positive heading and angular length
        arc_90_deg = Arc(Point(0, 0), 90, 10, 90)
        self.assertAlmostEqual(arc_90_deg.end_point(), Point(-10, 10))

        arc_180_deg = Arc(Point(0, 0), 90, 10, 180)
        self.assertAlmostEqual(arc_180_deg.end_point(), Point(-20, 0))

        arc_270_deg = Arc(Point(0, 0), 90, 10, 270)
        self.assertAlmostEqual(arc_270_deg.end_point(), Point(-10, -10))

        arc_360_deg = Arc(Point(0, 0), 90, 10, 360)
        self.assertAlmostEqual(arc_360_deg.end_point(), Point(0, 0))

        # Positive heading and negative angular length
        arc_minus_90_deg = Arc(Point(0, 0), 90, 10, -90)
        self.assertAlmostEqual(arc_minus_90_deg.end_point(), Point(10, 10))

        arc_minus_180_deg = Arc(Point(0, 0), 90, 10, -180)
        self.assertAlmostEqual(arc_minus_180_deg.end_point(), Point(20, 0))

        arc_minus_270_deg = Arc(Point(0, 0), 90, 10, -270)
        self.assertAlmostEqual(arc_minus_270_deg.end_point(), Point(10, -10))

        arc_minus_360_deg = Arc(Point(0, 0), 90, 10, -360)
        self.assertAlmostEqual(arc_minus_360_deg.end_point(), Point(0, 0))

        # Negative heading and positive angular length
        arc_minus_90_deg = Arc(Point(0, 0), -90, 10, 90)
        self.assertAlmostEqual(arc_minus_90_deg.end_point(), Point(10, -10))

        arc_minus_180_deg = Arc(Point(0, 0), -90, 10, 180)
        self.assertAlmostEqual(arc_minus_180_deg.end_point(), Point(20, 0))

        arc_minus_270_deg = Arc(Point(0, 0), -90, 10, 270)
        self.assertAlmostEqual(arc_minus_270_deg.end_point(), Point(10, 10))

        arc_minus_360_deg = Arc(Point(0, 0), -90, 10, 360)
        self.assertAlmostEqual(arc_minus_360_deg.end_point(), Point(0, 0))

        # Negative heading and angular length
        arc_90_deg = Arc(Point(0, 0), -90, 10, -90)
        self.assertAlmostEqual(arc_90_deg.end_point(), Point(-10, -10))

        arc_180_deg = Arc(Point(0, 0), -90, 10, -180)
        self.assertAlmostEqual(arc_180_deg.end_point(), Point(-20, 0))

        arc_270_deg = Arc(Point(0, 0), -90, 10, -270)
        self.assertAlmostEqual(arc_270_deg.end_point(), Point(-10, 10))

        arc_360_deg = Arc(Point(0, 0), -90, 10, -360)
        self.assertAlmostEqual(arc_360_deg.end_point(), Point(0, 0))

    def test_45_degree_variants_end_point(self):
        arc_45_deg = Arc(Point(0, 10), 0, 10, 45)
        self.assertAlmostEqual(arc_45_deg.end_point(), Point(7.07106781, 12.92893218))

        arc_135_deg = Arc(Point(0, 0), 90, 10, 135)
        self.assertAlmostEqual(arc_135_deg.end_point(), Point(-17.07106781, 7.07106781))

        arc_225_deg = Arc(Point(0, 0), 315, 10, 225)
        self.assertAlmostEqual(arc_225_deg.end_point(), Point(7.07106781, 17.07106781))

        arc_315_deg = Arc(Point(0, 0), -45, 10, 315)
        self.assertAlmostEqual(arc_315_deg.end_point(), Point(-2.92893218, 7.07106781))

    def test_length(self):
        null_arc = Arc(Point(0, 0), 90, 10, 0)
        self.assertAlmostEqual(null_arc.length(), 0)

        arc_360_deg = Arc(Point(0, 0), 90, 10, 360)
        self.assertAlmostEqual(arc_360_deg.length(), 62.8318530718)

        arc_90_deg = Arc(Point(0, 0), 90, 10, 90)
        self.assertAlmostEqual(arc_90_deg.length(), 15.707963268)

        arc_57_deg = Arc(Point(0, 0), 30, 10, 57.29576)
        self.assertAlmostEqual(arc_57_deg.length(), 10, 5)

    def test_extend(self):
        null_arc = Arc(Point(0, 0), 90, 10, 0)
        arc_90_deg = null_arc.extend(15.707963268)
        expected_arc = Arc(Point(0, 0), 90, 10, 90)
        self.assertArcAlmostEqual(arc_90_deg, expected_arc)

        negative_arc = Arc(Point(0, 0), 90, 10, -180)
        extended_deg = negative_arc.extend(10)
        expected_arc = Arc(Point(0, 0), 90, 10, -122.704220487)
        self.assertArcAlmostEqual(extended_deg, expected_arc)

    def test_center_point(self):
        null_arc = Arc(Point(0, 0), 90, 10, 0.0)
        self.assertAlmostEqual(null_arc.center_point(), Point(-10, 0))

        arc = Arc(Point(0, 0), 30, 10, 1)
        self.assertAlmostEqual(arc.center_point(), Point(-5, 8.660254037))

        arc = Arc(Point(0, 0), 30, 10, -1)
        self.assertAlmostEqual(arc.center_point(), Point(5, -8.660254038))

        arc = Arc(Point(0, 0), -60, 10, 1)
        self.assertAlmostEqual(arc.center_point(), Point(8.660254038, 5))

        arc = Arc(Point(0, 0), -60, 10, -1)
        self.assertAlmostEqual(arc.center_point(), Point(-8.660254038, -5))

    def test_includes_point(self):
        arc_90_deg = Arc(Point(0, 0), 90, 10, 90)
        self.assertTrue(arc_90_deg.includes_point(Point(0, 0)))
        self.assertTrue(arc_90_deg.includes_point(Point(-2.92893219, 7.07106781)))
        self.assertTrue(arc_90_deg.includes_point(Point(-10, 10)))

        arc_135_neg_deg = Arc(Point(0, 0), 90, 10, -135)
        self.assertTrue(arc_135_neg_deg.includes_point(Point(0, 0)))
        self.assertTrue(arc_135_neg_deg.includes_point(Point(2.92893219, 7.07106781)))
        self.assertTrue(arc_135_neg_deg.includes_point(Point(17.07106781, 7.07106781)))

    def test_point_at_offset(self):
        arc_90_deg = Arc(Point(0, 0), 90, 10, 90)
        self.assertAlmostEqual(arc_90_deg.point_at_offset(0), Point(0, 0))
        self.assertAlmostEqual(arc_90_deg.point_at_offset(7.853981634), Point(-2.92893219, 7.07106781))
        self.assertAlmostEqual(arc_90_deg.point_at_offset(15.7079632679), Point(-10, 10))

        arc_135_neg_deg = Arc(Point(0, 0), 90, 10, -135)
        self.assertAlmostEqual(arc_135_neg_deg.point_at_offset(0), Point(0, 0))
        self.assertAlmostEqual(arc_135_neg_deg.point_at_offset(15.7079632679), Point(10, 10))
        self.assertAlmostEqual(arc_135_neg_deg.point_at_offset(23.5619449019), Point(17.07106781, 7.07106781))

    def test_find_arc_intersection_with_circles_that_do_not_intersect(self):
        arc1 = Arc(Point(1, 0), 90, 1, 180)
        arc2 = Arc(Point(10, 10), 180, 2, 270)
        self.assertEqual(arc1._find_arc_intersection(arc2), [])

    def test_find_arc_intersection_with_arcs_that_intersect_at_one_point(self):
        arc1 = Arc(Point(5, 0), 90, 5, 90)
        arc2 = Arc(Point(0, 3), 0, 5, 45)
        self.assertEqual(arc1._find_arc_intersection(arc2), [Point(3, 4)])

    def test_find_arc_intersection_with_circles_that_intersect_but_no_arc_intersection(self):
        arc1 = Arc(Point(5, 0), 90, 5, 10)
        arc2 = Arc(Point(0, 3), 0, 5, 10)
        self.assertEqual(arc1._find_arc_intersection(arc2), [])
