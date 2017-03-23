import unittest
import mock

from models.city_statistics import CityStatistics
from models.city import City
from geometry.point import Point
from models.street import Street
from models.trunk import Trunk


class CityStatisticsTest(unittest.TestCase):

    def test_empty_city(self):
        city = City()
        stats = CityStatistics(city)
        values = stats.run()
        self.assertEquals(values['roads_count'], 0)
        self.assertEquals(values['lanes_count'], 0)
        self.assertEquals(values['buildings_count'], 0)
        self.assertEquals(values['blocks_count'], 0)
        self.assertEquals(values['intersections_count'], 0)
        self.assertEquals(values['lane_waypoints_count'], 0)
        self.assertEquals(values['lane_intersections_count'], 0)
        self.assertEquals(values['average_lane_intersections'], 0)
        self.assertEquals(values['average_lane_waypoints'], 0)

    def test_sample_city(self):
        city = City()

        city.add_road(Street.from_control_points([Point(-100, 0), Point(0, 0), Point(100, 0)]))
        city.add_road(Street.from_control_points([Point(0, 100), Point(0, 0), Point(0, -100)]))
        city.add_intersection_at(Point(0, 0))

        city.add_road(Street.from_control_points([Point(-10, 200), Point(0, 200), Point(10, 220), Point(20, 270)]))

        stats = CityStatistics(city)
        values = stats.run()
        self.assertEquals(values['roads_count'], 3)
        self.assertEquals(values['lanes_count'], 3)
        self.assertEquals(values['buildings_count'], 0)
        self.assertEquals(values['blocks_count'], 0)
        self.assertEquals(values['lane_waypoints_count'], 14)
        self.assertEquals(values['lane_intersections_count'], 4)
        self.assertEquals(values['average_lane_intersections'], 4.0 / 3.0)
        self.assertEquals(values['average_lane_waypoints'], 14.0 / 3.0)
