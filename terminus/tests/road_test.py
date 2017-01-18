import unittest

from geometry.point import Point
from geometry.latlon import LatLon
from models.road import Road
from models.street import Street
import math


class RoadTest(unittest.TestCase):

    def test_get_waypoint_positions(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Street.from_points(points)
        self.assertEqual(road.get_waypoint_positions(), points)

    def test_get_waypoint_distances(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        distances = [1.0, 1.0]
        road = Street.from_points(points)
        self.assertEqual(road.get_waypoint_distances(), distances)

    def test_get_waypoints_yaws(self):
        points = [Point(0.0, 0.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        yaws = [math.pi / 4.0, 0.0]
        road = Street.from_points(points)
        self.assertEqual(road.get_waypoints_yaws(), yaws)

    def test_leght_full(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Street.from_points(points)
        self.assertEqual(road.length(), 2.0)

    def test_leght_partial_from_beginning(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Street.from_points(points)
        self.assertEqual(road.length(0, 1), 1.0)

    def test_leght_partial_to_end(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Street.from_points(points)
        self.assertEqual(road.length(1), 1.0)

    def test_leght_empty(self):
        points = [Point(0.0, 1.0), Point(1.0, 1.0), Point(2.0, 1.0)]
        road = Street.from_points(points)
        self.assertEqual(road.length(1, 1), 0.0)
