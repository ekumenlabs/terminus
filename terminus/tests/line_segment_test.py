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

from math import *

from geometry.point import Point
from geometry.line_segment import LineSegment


class LineSegmentTest(unittest.TestCase):

    def test_includes_point_2d(self):
        segment = LineSegment(Point(0, 0), Point(1, 0))

        self.assertTrue(segment.includes_point(Point(0, 0)))
        self.assertTrue(segment.includes_point(Point(1, 0)))
        self.assertTrue(segment.includes_point(Point(0.5, 0), 0))

        self.assertFalse(segment.includes_point(Point(-0.01, 0)))
        self.assertFalse(segment.includes_point(Point(1.01, 0)))
        self.assertFalse(segment.includes_point(Point(0.5, 0.01)))
        self.assertFalse(segment.includes_point(Point(0.5, -0.01)))

    def test_includes_point_3d(self):
        segment = LineSegment(Point(0, 0, 0), Point(1, 1, 1))

        self.assertTrue(segment.includes_point(Point(0, 0, 0)))
        self.assertTrue(segment.includes_point(Point(1, 1, 1)))
        self.assertTrue(segment.includes_point(Point(0.5, 0.5, 0.5)))

        self.assertFalse(segment.includes_point(Point(1, 1, 1.01)))
        self.assertFalse(segment.includes_point(Point(1, 1.01, 1)))
        self.assertFalse(segment.includes_point(Point(1.01, 1, 1)))
        self.assertFalse(segment.includes_point(Point(-0.01, 0, 0)))
        self.assertFalse(segment.includes_point(Point(0, -0.01, 0)))
        self.assertFalse(segment.includes_point(Point(0, 0, -0.01)))
        self.assertFalse(segment.includes_point(Point(0.51, 0.5, 0.5)))
        self.assertFalse(segment.includes_point(Point(0.5, 0.51, 0.5)))
        self.assertFalse(segment.includes_point(Point(0.5, 0.5, 0.51)))

    def test_includes_point_buffer(self):
        '''The point is slightly outside the line, so by increasing the buffer
        we use to test collinearity between vectors we make it pass'''
        segment = LineSegment(Point(0, 0), Point(1, 0))
        self.assertTrue(segment.includes_point(Point(0.5, 0)))
        self.assertFalse(segment.includes_point(Point(0.5, 0.01)))
        self.assertTrue(segment.includes_point(Point(0.5, 0.01), 0.01))

    def test_is_orthogonal_to_touching_segments(self):
        target_segment = LineSegment(Point(2, 2), Point(4, 2))
        orthogonal_segment = LineSegment(Point(3, 1), Point(3, 2))
        non_orthogonal_segment = LineSegment(Point(3, 1), Point(3.01, 2))
        self.assertTrue(target_segment.is_orthogonal_to(orthogonal_segment))
        self.assertFalse(target_segment.is_orthogonal_to(non_orthogonal_segment))

        target_segment = LineSegment(Point(2, 2), Point(2, 4))
        orthogonal_segment = LineSegment(Point(1, 3), Point(2, 3))
        non_orthogonal_segment = LineSegment(Point(1, 3), Point(2, 3.01))
        self.assertTrue(target_segment.is_orthogonal_to(orthogonal_segment))
        self.assertFalse(target_segment.is_orthogonal_to(non_orthogonal_segment))

        target_segment = LineSegment(Point(2, 2), Point(5, 5))
        orthogonal_segment = LineSegment(Point(5, 3), Point(4, 4))
        non_orthogonal_segment = LineSegment(Point(5.01, 3), Point(4, 4))
        self.assertTrue(target_segment.is_orthogonal_to(orthogonal_segment))
        self.assertFalse(target_segment.is_orthogonal_to(non_orthogonal_segment))

    def test_is_orthogonal_to_non_touching_segments(self):
        target_segment = LineSegment(Point(2, 2), Point(4, 2))
        orthogonal_segment = LineSegment(Point(3, 1), Point(3, 1.9))
        non_orthogonal_segment = LineSegment(Point(3, 1), Point(3.01, 1.9))
        self.assertTrue(target_segment.is_orthogonal_to(orthogonal_segment))
        self.assertFalse(target_segment.is_orthogonal_to(non_orthogonal_segment))

        target_segment = LineSegment(Point(2, 2), Point(2, 4))
        orthogonal_segment = LineSegment(Point(1, 3), Point(1.9, 3))
        non_orthogonal_segment = LineSegment(Point(1, 3), Point(1.9, 3.01))
        self.assertTrue(target_segment.is_orthogonal_to(orthogonal_segment))
        self.assertFalse(target_segment.is_orthogonal_to(non_orthogonal_segment))

        target_segment = LineSegment(Point(2, 2), Point(5, 5))
        orthogonal_segment = LineSegment(Point(5, 3), Point(4.1, 3.9))
        non_orthogonal_segment = LineSegment(Point(5.01, 3), Point(3.9, 3.9))
        self.assertTrue(target_segment.is_orthogonal_to(orthogonal_segment))
        self.assertFalse(target_segment.is_orthogonal_to(non_orthogonal_segment))

    def test_two_segments_intersect(self):
        first_segment = LineSegment(Point(1, 0), Point(3, 4))
        second_segment = LineSegment(Point(1, 4), Point(3, 0))
        non_intersect_segment = LineSegment(Point(3, 1), Point(3, 2))
        self.assertEqual(first_segment.find_intersection(second_segment), Point(2, 2, 0))
        self.assertEqual(first_segment.find_intersection(non_intersect_segment), None)

        first_segment = LineSegment(Point(28.5299698219, 160.06688421), Point(-48.1969708416, -28.3309145497))
        second_segment = LineSegment(Point(-193.740103155, 132.470681), Point(193.740103155, 132.470681))
        non_intersect_segment = LineSegment(Point(193.740103155, 132.470681), Point(193.740103155, -132.470681))
        self.assertPointAlmostEqual(first_segment.find_intersection(second_segment), Point(17.2911323186, 132.470681, 0))
        self.assertEqual(first_segment.find_intersection(non_intersect_segment), None)

    def test_extend(self):
        original = LineSegment(Point(0, 0), Point(0, 1))
        expected = LineSegment(Point(0, 0), Point(0, 2))
        self.assertEquals(original.extend(1), expected)

        original = LineSegment(Point(0, 0), Point(1, 0))
        expected = LineSegment(Point(0, 0), Point(3, 0))
        self.assertEquals(original.extend(2), expected)

        original = LineSegment(Point(0, 0), Point(1, 1))
        expected = LineSegment(Point(0, 0), Point(2, 2))
        self.assertEquals(original.extend(sqrt(2)), expected)

    def assertPointAlmostEqual(self, point1, point2):
        self.assertAlmostEqual(point1.x, point2.x)
        self.assertAlmostEqual(point1.y, point2.y)
