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

        '''
        this test couldn't be implemented yet:

    def test_node_bounding_boxes(self):
        road = Road()
        node_1 = RoadNode(Point(10, 20))
        node_2 = RoadNode(Point(-15, 10))
        node_3 = RoadNode(Point(40, -20))
        road._add_node(node_1)
        road._add_node(node_2)
        road._add_node(node_3)
        road.add_lane(10)
        road.add_lane(20)
        width = road.width()
        expected_box = BoundingBox(Point(-15 - width / 2, -20 - width / 2),
                                    Point(40 + width / 2, 20 + width / 2))
        self.assertEqual(road.road_bounding_box(), expected_box)
        '''
