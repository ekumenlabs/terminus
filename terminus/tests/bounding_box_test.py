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

from geometry.point import Point

from geometry.bounding_box import BoundingBox


class BoundingBoxTest(unittest.TestCase):

    def test_eq_on_identical_objects(self):
        box = BoundingBox(Point(10, 10), Point(20, 20))
        self.assertTrue(box == box)

    def test_eq_on_non_identical_objects(self):
        box = BoundingBox(Point(0, 0), Point(10, 10))
        box_with_same_origin_and_corner = BoundingBox(Point(0, 0), Point(10, 10))
        self.assertTrue(box == box_with_same_origin_and_corner)

    def test_eq_on_different_objects(self):
        box_1 = BoundingBox(Point(10, 20), Point(30, 40))
        box_2 = BoundingBox(Point(55, 15), Point(45, 16))
        self.assertFalse(box_1 == box_2)

    def test_normalize_on_creation(self):
        box = BoundingBox(Point(20, 30), Point(10, 40))
        self.assertEqual(box.origin, Point(10, 30))
        self.assertEqual(box.corner, Point(20, 40))
        other_box = BoundingBox(Point(25, 13), Point(82, 9))
        self.assertEqual(other_box.origin, Point(25, 9))
        self.assertEqual(other_box.corner, Point(82, 13))

    def test_merge(self):
        box_1 = BoundingBox(Point(10, 20), Point(20, 30))
        box_2 = BoundingBox(Point(40, -10), Point(50, 0))
        expected_merge = BoundingBox(Point(10, -10), Point(50, 30))
        self.assertEqual(box_1.merge(box_2), expected_merge)

    def test_merge_nested_boxes(self):
        box_1 = BoundingBox(Point(20, 20), Point(30, 30))
        box_2 = BoundingBox(Point(10, 10), Point(40, 40))
        self.assertEqual(box_1.merge(box_2), box_2)

    def test_merge_with_negative_values(self):
        box_1 = BoundingBox(Point(10, -30), Point(20, -10))
        box_2 = BoundingBox(Point(-20, 10), Point(-10, 20))
        expected_merge = BoundingBox(Point(-20, -30), Point(20, 20))
        self.assertEqual(box_1.merge(box_2), expected_merge)

    def test_merge_bounding_box_with_itself(self):
        box = BoundingBox(Point(30, 45), Point(15, 18))
        self.assertEqual(box.merge(box), box)

    def test_from_boxes_with_one_box(self):
        box = BoundingBox(Point(17, 4), Point(59, 7))
        self.assertEqual(BoundingBox.from_boxes([box]), box)

    def test_from_boxes_with_two_boxes(self):
        box_1 = BoundingBox(Point(-5, -10), Point(5, 0))
        box_2 = BoundingBox(Point(-5, 10), Point(5, 20))
        box_list = [box_1, box_2]
        expected_merge = BoundingBox(Point(-5, -10), Point(5, 20))
        self.assertEqual(BoundingBox.from_boxes(box_list), expected_merge)

    def test_from_boxes_with_five_boxes(self):
        box_1 = BoundingBox(Point(-20, -10), Point(-10, 10))
        box_2 = BoundingBox(Point(20, 5), Point(30, 15))
        box_3 = BoundingBox(Point(-15, 0), Point(10, 20))
        box_4 = BoundingBox(Point(55, 15), Point(45, 16))
        box_5 = BoundingBox(Point(-5, -10), Point(5, 0))
        box_list = [box_1, box_2, box_3, box_4, box_4]
        expected_merge = BoundingBox(Point(-20, -10), Point(55, 20))
        self.assertEqual(BoundingBox.from_boxes(box_list), expected_merge)

    def test_from_boxes_with_empty_box_list(self):
        box_list = []
        self.assertRaises(Exception, lambda: BoundingBox.from_boxes(box_list))

    def test_width(self):
        box = BoundingBox(Point(25, 40), Point(30, 50))
        self.assertEqual(box.width(), 5)

    def test_height(self):
        box = BoundingBox(Point(-10, 18), Point(15, 43))
        self.assertEqual(box.height(), 25)
