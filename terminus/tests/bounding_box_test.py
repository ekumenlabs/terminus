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

    def test_merge_multiple_boundig_boxes_for_two_boxes(self):
        box_1 = BoundingBox(Point(-5, -10), Point(5, 0))
        box_2 = BoundingBox(Point(-5, 10), Point(5, 20))
        box_list = [box_1, box_2]
        expected_merge = box_1.merge(box_2)
        self.assertEqual(box_1.merge_multiple_boundingboxes(box_list), expected_merge)

    def test_merge_multiple_boundingboxes_for_three_boxes(self):
        box_1 = BoundingBox(Point(-20, -10), Point(-10, 10))
        box_2 = BoundingBox(Point(20, 5), Point(30, 15))
        box_3 = BoundingBox(Point(-15, 0), Point(10, 20))
        box_list = [box_1, box_2, box_3]
        expected_merge = BoundingBox(Point(-20, -10), Point(30, 20))
        self.assertEqual(box_2.merge_multiple_boundingboxes(box_list), expected_merge)

    def test_merge_multiple_boundingboxes_for_five_boxes(self):
        box_1 = BoundingBox(Point(-20, -10), Point(-10, 10))
        box_2 = BoundingBox(Point(20, 5), Point(30, 15))
        box_3 = BoundingBox(Point(-15, 0), Point(10, 20))
        box_4 = BoundingBox(Point(55, 15), Point(45, 16))
        box_5 = BoundingBox(Point(-5, -10), Point(5, 0))
        box_list = [box_1, box_2, box_3, box_4, box_4]
        expected_merge = BoundingBox(Point(-20, -10), Point(55, 20))
        self.assertEqual(box_1.merge_multiple_boundingboxes(box_list), expected_merge)
