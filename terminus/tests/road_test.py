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

from geometry.bounding_box import BoundingBox
from geometry.point import Point
from geometry.latlon import LatLon
from models.road import Road
from models.street import Street
from models.road_node import RoadNode
import math


class RoadTest(unittest.TestCase):

    def test_get_waypoint_positions_empty(self):
        road = Street.from_points([])
        self.assertEqual(road.get_waypoint_positions(), [])

    def test_get_waypoint_positions_one_point(self):
        points = [Point(0.0, 1.0)]
        road = Street.from_points(points)
        self.assertEqual(road.get_waypoint_positions(), points)

    def test_get_waypoint_positions(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Street.from_points(points)
        self.assertEqual(road.get_waypoint_positions(), points)

    def test_get_waypoint_distances_empty(self):
        road = Street.from_points([])
        self.assertEqual(road.get_waypoint_distances(), [])

    def test_get_waypoint_distances_one_point(self):
        road = Street.from_points([Point(1.0, 2.0)])
        self.assertEqual(road.get_waypoint_distances(), [0.0])

    def test_get_waypoint_distances(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0), Point(0.0, 0.0)]
        distances = [1.0, 1.0, math.sqrt(5)]
        road = Street.from_points(points)
        self.assertEqual(road.get_waypoint_distances(), distances)

    def test_get_waypoints_yaws(self):
        points = [Point(0.0, 0.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        yaws = [math.pi / 4.0, 0.0]
        road = Street.from_points(points)
        self.assertEqual(road.get_waypoints_yaws(), yaws)

    def test_length_full(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Street.from_points(points)
        self.assertEqual(road.length(), 2.0)

    def test_length_partial_from_beginning(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Street.from_points(points)
        self.assertEqual(road.length(0, 1), 1.0)

    def test_length_partial_to_end(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Street.from_points(points)
        self.assertEqual(road.length(1), 1.0)

    def test_length_empty(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Street.from_points(points)
        self.assertEqual(road.length(1, 1), 0.0)

    def test_length_empty_road(self):
        road = Street.from_points([])
        self.assertEqual(road.length(), 0.0)

    def test_node_bounding_boxes(self):
        points_list = [Point(10, 20), Point(-15, 10), Point(40, -20)]
        road = Road.from_points(points_list)
        road.add_lane(10)
        road.add_lane(20)
        width = road.width()
        expected_box_list = [BoundingBox(Point(10 - width / 2, 20 - width / 2), Point(10 + width / 2, 20 + width / 2)),
                             BoundingBox(Point(-15 - width / 2, 10 - width / 2), Point(-15 + width / 2, 10 + width / 2)),
                             BoundingBox(Point(40 - width / 2, -20 - width / 2), Point(40 + width / 2, -20 + width / 2))]
        self.assertEqual(road._node_bounding_boxes(), expected_box_list)

    def test_bounding_box(self):
        points_list = [Point(10, 20), Point(-15, 10), Point(40, -20)]
        road = Road.from_points(points_list)
        road.add_lane(10)
        road.add_lane(20)
        width = road.width()
        expected_box = BoundingBox(Point(-15 - width / 2, -20 - width / 2),
                                   Point(40 + width / 2, 20 + width / 2))
        self.assertEqual(road.bounding_box(), expected_box)

    def test_bounding_box_for_road_with_one_lane_of_null_offset(self):
        road = Road.from_points([Point(15, 50), Point(-20, 10)])
        road.add_lane(0)
        expected_box = BoundingBox(Point(-22, 8), Point(17, 52))
        self.assertEqual(road.bounding_box(), expected_box)

    def test_bounding_box_for_road_with_one_lane_and_positive_offset(self):
        road = Road.from_points([Point(-10, 40), Point(5, -20)])
        road.add_lane(10)
        expected_box = BoundingBox(Point(-22, -32), Point(17, 52))
        self.assertEqual(road.bounding_box(), expected_box)

    def test_bounding_box_with_lanes_with_positive_and_negative_offsets(self):
        road = Road.from_points([Point(30, 25), Point(90, -30), Point(-25, 50)])
        road.add_lane(20)
        road.add_lane(-30)
        expected_box = BoundingBox(Point(-52, -57), Point(117, 77))
        self.assertEqual(road.bounding_box(), expected_box)

    def test_bounding_box_with_one_lane_with_null_width_and_offset(self):
        road = Road.from_points([Point(0, 0), Point(10, 10)])
        road.add_lane(0, 0)
        self.assertEqual(road.bounding_box(), BoundingBox(Point(0, 0), Point(10, 10)))

    def test_bounding_box_for_rode_with_one_node_and_null_width(self):
        point = Point(0, 0)
        road = Road.from_points([point])
        road.add_lane(0, 0)
        self.assertEqual(road.bounding_box(), BoundingBox(point, point))

    def test_bounding_box_for_road_with_one_node_and_positive_width(self):
        point = Point(10, 10)
        road = Road.from_points([point])
        road.add_lane(10)
        expected_box = BoundingBox(Point(-2, -2), Point(22, 22))
        self.assertEqual(road.bounding_box(), expected_box)
