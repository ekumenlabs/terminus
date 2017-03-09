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
from models.block import Block


class BlockTest(unittest.TestCase):

    def test_accept(self):
        vertices = [Point(0, 0, 0), Point(0, 1, 0), Point(1, 0, 0)]
        block = Block(Point(0, 0, 0), vertices)
        generator_mock = mock.Mock()
        calls = [mock.call.start_block(block), mock.call.end_block(block)]
        block.accept(generator_mock)
        generator_mock.assert_has_calls(calls)

    def test_bounding_box(self):
        block = Block(Point(10, 20),
                      [Point(15, 30), Point(15, -5), Point(40, 30), Point(40, -5)],
                      1)
        self.assertEqual(block.bounding_box(), BoundingBox(Point(25, 15), Point(50, 50, 1)))

    def test_bounding_box_with_one_point_block_centered_at_0_0(self):
        origin = Point(0, 0)
        block = Block.square(origin, 0)
        self.assertEqual(block.bounding_box(), BoundingBox(origin, origin + Point(0, 0, 0.15)))

    def test_bounding_box_with_one_point_block_not_centered_at_0_0(self):
        origin = Point(34, 68)
        block = Block.square(origin, 0)
        self.assertEqual(block.bounding_box(), BoundingBox(origin, origin + Point(0, 0, 0.15)))

    def test_bounding_box_with_pentagonal_base_block(self):
        block = Block(Point(10, 20),
                      [Point(-10, -20), Point(10, -30), Point(20, 10), Point(-5, 30), Point(-20, 5)],
                      2)
        self.assertEqual(block.bounding_box(),
                         BoundingBox(Point(-10, -10), Point(30, 50, 2)))

    def test_bounding_box_with_not_convex_base_block(self):
        block = Block(Point(0, 0), [Point(-15, 0), Point(10, -40), Point(0, 0), Point(15, 30)])
        self.assertEqual(block.bounding_box(), BoundingBox(Point(-15, -40), Point(15, 30, 0.15)))
