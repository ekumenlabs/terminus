import unittest
import mock

from geometry.point import Point
from models.street import Street
from models.trunk import Trunk
from models.ground_plane import GroundPlane
from models.building import Building
from models.block import Block
from models.city import City


class CityModelTest(unittest.TestCase):

    def test_street(self):
        street = Street()
        generator_mock = mock.Mock()
        street.accept(generator_mock)
        calls = [mock.call.start_street(street), mock.call.end_street(street)]
        generator_mock.assert_has_calls(calls)

    def test_trunk(self):
        trunk = Trunk()
        generator_mock = mock.Mock()
        trunk.accept(generator_mock)
        calls = [mock.call.start_trunk(trunk), mock.call.end_trunk(trunk)]
        generator_mock.assert_has_calls(calls)

    def test_ground_plane(self):
        plane = GroundPlane(1, Point(0, 0, 0))
        generator_mock = mock.Mock()
        plane.accept(generator_mock)
        calls = [mock.call.start_ground_plane(plane), mock.call.end_ground_plane(plane)]
        generator_mock.assert_has_calls(calls)

    def test_building(self):
        vertices = [Point(0, 0, 0), Point(0, 1, 0), Point(1, 0, 0)]
        building = Building(Point(0, 0, 0), vertices)
        generator_mock = mock.Mock()
        building.accept(generator_mock)
        calls = [mock.call.start_building(building), mock.call.end_building(building)]
        generator_mock.assert_has_calls(calls)

    def test_block(self):
        vertices = [Point(0, 0, 0), Point(0, 1, 0), Point(1, 0, 0)]
        block = Block(Point(0, 0, 0), vertices)
        generator_mock = mock.Mock()
        block.accept(generator_mock)
        calls = [mock.call.start_block(block), mock.call.end_block(block)]
        generator_mock.assert_has_calls(calls)

    def test_city(self):
        city = City()
        road = mock.Mock()
        ground_plane = mock.Mock()
        building = mock.Mock()
        block = mock.Mock()
        city.add_road(road)
        city.add_building(building)
        city.set_ground_plane(ground_plane)
        city.add_block(block)
        generator_mock = mock.Mock()
        city.accept(generator_mock)
        city_calls = [mock.call.start_city(city), mock.call.end_city(city)]
        generator_mock.assert_has_calls(city_calls)
        road.accept.assert_called()
        ground_plane.accept.assert_called()
        building.accept.assert_called()
        block.accept.assert_called()
