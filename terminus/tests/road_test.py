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

from geometry.bounding_box import BoundingBox
from geometry.point import Point
from geometry.latlon import LatLon
from models.city import City
from models.road import Road
from models.road_node import RoadNode
from models.road_simple_node import RoadSimpleNode
from models.road_intersection_node import RoadIntersectionNode


class RoadTest(unittest.TestCase):

    def test_control_points_empty(self):
        road = Road.from_control_points([])
        self.assertEqual(road.control_points(), [])

    def test_control_points_one_point(self):
        points = [Point(0.0, 1.0)]
        road = Road.from_control_points(points)
        self.assertEqual(road.control_points(), points)

    def test_control_points(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Road.from_control_points(points)
        self.assertEqual(road.control_points(), points)

    def test_control_points_distances_empty(self):
        road = Road.from_control_points([])
        self.assertEqual(road.control_points_distances(), [])

    def test_control_points_distances_one_point(self):
        road = Road.from_control_points([Point(1.0, 2.0)])
        self.assertEqual(road.control_points_distances(), [0.0])

    def test_control_points_distances(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0), Point(0.0, 0.0)]
        distances = [1.0, 1.0, math.sqrt(5)]
        road = Road.from_control_points(points)
        self.assertEqual(road.control_points_distances(), distances)

    def test_sum_control_points_distances_full(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Road.from_control_points(points)
        self.assertEqual(road.sum_control_points_distances(), 2.0)

    def test_sum_control_points_distances_partial_from_beginning(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Road.from_control_points(points)
        self.assertEqual(road.sum_control_points_distances(0, 1), 1.0)

    def test_sum_control_points_distances_partial_to_end(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Road.from_control_points(points)
        self.assertEqual(road.sum_control_points_distances(1), 1.0)

    def test_sum_control_points_distances_empty(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Road.from_control_points(points)
        self.assertEqual(road.sum_control_points_distances(1, 1), 0.0)

    def test_sum_control_points_distances_empty_road(self):
        road = Road.from_control_points([])
        self.assertEqual(road.sum_control_points_distances(), 0.0)

    def test_node_bounding_boxes(self):
        points_list = [Point(10, 20), Point(-15, 10), Point(40, -20)]
        road = Road.from_control_points(points_list)
        road.add_lane(10)
        road.add_lane(20)
        width = road.width()
        expected_box_list = [BoundingBox(Point(10 - width / 2, 20 - width / 2), Point(10 + width / 2, 20 + width / 2)),
                             BoundingBox(Point(-15 - width / 2, 10 - width / 2), Point(-15 + width / 2, 10 + width / 2)),
                             BoundingBox(Point(40 - width / 2, -20 - width / 2), Point(40 + width / 2, -20 + width / 2))]
        self.assertEqual(road._node_bounding_boxes(), expected_box_list)

    def test_bounding_box(self):
        points_list = [Point(10, 20), Point(-15, 10), Point(40, -20)]
        road = Road.from_control_points(points_list)
        road.add_lane(10)
        road.add_lane(20)
        width = road.width()
        expected_box = BoundingBox(Point(-15 - width / 2, -20 - width / 2),
                                   Point(40 + width / 2, 20 + width / 2))
        self.assertEqual(road.bounding_box(), expected_box)

    def test_bounding_box_for_road_with_one_lane_of_null_offset(self):
        road = Road.from_control_points([Point(15, 50), Point(-20, 10)])
        road.add_lane(0)
        expected_box = BoundingBox(Point(-22, 8), Point(17, 52))
        self.assertEqual(road.bounding_box(), expected_box)

    def test_bounding_box_for_road_with_one_lane_and_positive_offset(self):
        road = Road.from_control_points([Point(-10, 40), Point(5, -20)])
        road.add_lane(10)
        expected_box = BoundingBox(Point(-22, -32), Point(17, 52))
        self.assertEqual(road.bounding_box(), expected_box)

    def test_bounding_box_with_lanes_with_positive_and_negative_offsets(self):
        road = Road.from_control_points([Point(30, 25), Point(90, -30), Point(-25, 50)])
        road.add_lane(20)
        road.add_lane(-30)
        expected_box = BoundingBox(Point(-52, -57), Point(117, 77))
        self.assertEqual(road.bounding_box(), expected_box)

    def test_bounding_box_with_one_lane_with_null_width_and_offset(self):
        road = Road.from_control_points([Point(0, 0), Point(10, 10)])
        road.add_lane(0, 0)
        self.assertEqual(road.bounding_box(), BoundingBox(Point(0, 0), Point(10, 10)))

    def test_bounding_box_for_rode_with_one_node_and_null_width(self):
        point = Point(0, 0)
        road = Road.from_control_points([point])
        road.add_lane(0, 0)
        self.assertEqual(road.bounding_box(), BoundingBox(point, point))

    def test_bounding_box_for_road_with_one_node_and_positive_width(self):
        point = Point(10, 10)
        road = Road.from_control_points([point])
        road.add_lane(10)
        expected_box = BoundingBox(Point(-2, -2), Point(22, 22))
        self.assertEqual(road.bounding_box(), expected_box)

    def test_trim_redundant_nodes_single_segment(self):
        """Nothing to do in this case, as the road has a single segment"""
        points = [Point(0, 0), Point(100, 0)]
        road = Road.from_control_points(points)
        road.trim_redundant_nodes()
        expected_nodes = map(lambda point: RoadSimpleNode(point), points)
        self.assertEqual(road.nodes(), expected_nodes)

    def test_trim_redundant_nodes_no_collinear_segments(self):
        """Nothing to do in this case, as the existing segments in the road
        are not collinear"""
        points = [Point(0, 0), Point(100, 0), Point(200, 1)]
        road = Road.from_control_points(points)
        road.trim_redundant_nodes()
        expected_nodes = map(lambda point: RoadSimpleNode(point), points)
        self.assertEqual(road.nodes(), expected_nodes)

    def test_trim_redundant_nodes_collinear_segments(self):
        """Two collinear segments, where the midpoint is not an intersection.
        The middle point should be removed"""
        points = [Point(0, 0), Point(100, 0), Point(200, 0)]
        road = Road.from_control_points(points)

        before_trim_expected_nodes = map(lambda point: RoadSimpleNode(point), points)
        self.assertEqual(road.nodes(), before_trim_expected_nodes)

        road.trim_redundant_nodes()

        after_trim_expected_nodes = [RoadSimpleNode(Point(0, 0)), RoadSimpleNode(Point(200, 0))]
        self.assertEqual(road.nodes(), after_trim_expected_nodes)

    def test_trim_redundant_nodes_on_collinear_segments_with_intersection(self):
        """Two collinear segments, where the midpoint is an intersection.
        The middle point should not be removed, as that would remove the intersection"""

        city = City()
        city.add_intersection_at(Point(100, 0))
        city.add_road(Road.from_control_points([Point(100, 100), Point(100, 0)]))

        points = [Point(0, 0), Point(100, 0), Point(200, 0)]
        road = Road.from_control_points(points)
        city.add_road(road)

        expected_nodes = [
            RoadSimpleNode(Point(0, 0)),
            RoadIntersectionNode(Point(100, 0)),
            RoadSimpleNode(Point(200, 0)),
        ]
        self.assertEqual(road.nodes(), expected_nodes)
        road.trim_redundant_nodes()
        self.assertEqual(road.nodes(), expected_nodes)

    def test_trim_redundant_nodes_multiple_collinear_segments(self):
        """Multiple collinear segments to be trimmed, leaving just two segments"""
        points = [
            Point(0, 0),
            Point(10, 0),
            Point(20, 0),
            Point(50, 0),
            Point(100, 0),
            Point(110, 10),
            Point(150, 50),
            Point(200, 100)
        ]
        road = Road.from_control_points(points)

        before_trim_expected_nodes = map(lambda point: RoadSimpleNode(point), points)
        self.assertEqual(road.nodes(), before_trim_expected_nodes)

        road.trim_redundant_nodes()

        after_trim_expected_nodes = [
            RoadSimpleNode(Point(0, 0)),
            RoadSimpleNode(Point(100, 0)),
            RoadSimpleNode(Point(200, 100))
        ]
        self.assertEqual(road.nodes(), after_trim_expected_nodes)

    def test_trim_redundant_nodes_on_multiple_collinear_segments_with_one_intersection(self):
        """Two collinear segments, where the midpoint is an intersection.
        The middle point should not be removed, as that would remove the intersection"""

        city = City()
        city.add_intersection_at(Point(100, 0))
        city.add_road(Road.from_control_points([Point(100, 100), Point(100, 0)]))

        points = [
            Point(0, 0),
            Point(10, 0),
            Point(20, 0),
            Point(50, 0),
            Point(100, 0),
            Point(110, 0),
            Point(150, 0),
            Point(200, 0)
        ]
        road = Road.from_control_points(points)
        city.add_road(road)

        before_trim_expected_nodes = [
            RoadSimpleNode(Point(0, 0)),
            RoadSimpleNode(Point(10, 0)),
            RoadSimpleNode(Point(20, 0)),
            RoadSimpleNode(Point(50, 0)),
            RoadIntersectionNode(Point(100, 0)),
            RoadSimpleNode(Point(110, 0)),
            RoadSimpleNode(Point(150, 0)),
            RoadSimpleNode(Point(200, 0))
        ]
        self.assertEqual(road.nodes(), before_trim_expected_nodes)

        road.trim_redundant_nodes()

        after_trim_expected_nodes = [
            RoadSimpleNode(Point(0, 0)),
            RoadIntersectionNode(Point(100, 0)),
            RoadSimpleNode(Point(200, 0))
        ]

        self.assertEqual(road.nodes(), after_trim_expected_nodes)

    def test_trim_redundant_nodes_optional_angle_tolerance(self):
        """Two non-collinear segments, with 45 deg angle difference. Test
        with different angle tolerance"""
        points = [Point(0, 0), Point(100, 0), Point(200, 100)]
        before_trim_expected_nodes = map(lambda point: RoadSimpleNode(point), points)

        road = Road.from_control_points(points)
        self.assertEqual(road.nodes(), before_trim_expected_nodes)
        road.trim_redundant_nodes(44.5)
        self.assertEqual(road.nodes(), before_trim_expected_nodes)

        road = Road.from_control_points(points)
        self.assertEqual(road.nodes(), before_trim_expected_nodes)
        road.trim_redundant_nodes(45.5)
        self.assertEqual(road.nodes(), [RoadSimpleNode(Point(0, 0)), RoadSimpleNode(Point(200, 100))])

        road = Road.from_control_points(points)
        self.assertEqual(road.nodes(), before_trim_expected_nodes)
        road.trim_redundant_nodes(45.0)
        self.assertEqual(road.nodes(), [RoadSimpleNode(Point(0, 0)), RoadSimpleNode(Point(200, 100))])
