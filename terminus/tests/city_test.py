import unittest
import mock

from geometry.point import Point
from models.street import Street
from models.trunk import Trunk
from models.ground_plane import GroundPlane
from models.road import Road
from models.building import Building
from models.block import Block
from models.city import City
from models.road_simple_node import RoadSimpleNode
from models.road_intersection_node import RoadIntersectionNode
from geometry.bounding_box import BoundingBox


class CityTest(unittest.TestCase):

    def test_accept_with_ground_plane(self):
     	city = self.city
        road = mock.Mock()
        ground_plane = mock.Mock()
        building = mock.Mock()
        block = mock.Mock()
        city.add_road(road)
        city.add_building(building)
        city.set_ground_plane(ground_plane)
        city.add_block(block)
        generator_mock = mock.Mock()
        city_calls = [mock.call.start_city(city), mock.call.end_city(city)]
        city.accept(generator_mock)
        generator_mock.assert_has_calls(city_calls)
        road.accept.assert_called()
        ground_plane.accept.assert_called()
        building.accept.assert_called()
        block.accept.assert_called()

    def test_accept_without_ground_plane(self):
        city = City()
        road = mock.Mock()
        building = mock.Mock()
        block = mock.Mock()
        city.add_road(road)
        city.add_building(building)
        city.add_block(block)
        generator_mock = mock.Mock()
        city_calls = [mock.call.start_city(city), mock.call.end_city(city)]
        city.accept(generator_mock)
        generator_mock.assert_has_calls(city_calls)
        road.accept.assert_called()
        building.accept.assert_called()
        block.accept.assert_called()

    def setUp(self):
        self.city = City()

    def test_add_intersection_at_on_single_street(self):
        '''Even if we only add a single street (hence there is no other
        street to intersect with) the intersection is created'''

        self.city.add_intersection_at(Point(0, 0))
        street = Street.from_points([Point(0, 0), Point(100, 0)])
        self.city.add_road(street)
        self.assertEquals(street.get_nodes()[0], RoadIntersectionNode.on(0, 0))
        self.assertEquals(street.get_nodes()[1], RoadSimpleNode.on(100, 0))

    def test_add_intersection_at_is_order_independent(self):
        '''No matter if we create the intersection before or after adding the
        street, the nodes are properly setup'''

        self.city.add_intersection_at(Point(0, 0))
        street = Street.from_points([Point(0, 0), Point(100, 0)])
        self.city.add_road(street)
        self.city.add_intersection_at(Point(100, 0))
        self.assertEquals(street.get_nodes()[0], RoadIntersectionNode.on(0, 0))
        self.assertEquals(street.get_nodes()[1], RoadIntersectionNode.on(100, 0))

    def test_add_intersection_at_on_two_streets(self):
        '''Check that both streets get the intersection node and that
        the same node is shared between them'''

        self.city.add_intersection_at(Point(0, 0))
        street1 = Street.from_points([Point(0, 0), Point(100, 0)])
        street2 = Street.from_points([Point(0, 0), Point(100, 100)])
        self.city.add_road(street1)
        self.city.add_road(street2)
        expected_node = RoadIntersectionNode.on(0, 0)
        self.assertEquals(street1.get_nodes()[0], expected_node)
        self.assertEquals(street2.get_nodes()[0], expected_node)
        self.assertTrue(street1.get_nodes()[0] is street2.get_nodes()[0])

    def test_add_intersection_at_on_different_z_order(self):
        '''Check that the z component of the point does make a difference'''

        self.city.add_intersection_at(Point(0, 0))
        street1 = Street.from_points([Point(0, 0), Point(100, 0)])
        street2 = Street.from_points([Point(0, 0, 1), Point(100, 100)])
        self.city.add_road(street1)
        self.city.add_road(street2)
        self.assertEquals(street1.get_nodes()[0], RoadIntersectionNode.on(0, 0))
        self.assertEquals(street2.get_nodes()[0], RoadSimpleNode.on(0, 0, 1))

    def test_bounding_box_with_ground_plane(self):
        building = Building.square(Point(35, 45), 10, 10)
        block = Block.square(Point(-75, -45), 10)
        street = Street.from_points([Point(60, -20), Point(80, -20)])
        ground_plane = GroundPlane(30, Point(15, 15))
        city = City()
        city.set_ground_plane(ground_plane)
        city.add_road(street)
        city.add_block(block)
        city.add_building(building)
        self.assertEqual(city.bounding_box(), BoundingBox(Point(-80, -50), Point(82, 50, 10)))

    def test_bounding_box_without_ground_plane(self):
        building = Building(Point(35, 10), [Point(-5, -10), Point(5, -10),
                                            Point(5, 10), Point(-5, 10)], 25)
        block = Block(Point(-45, 70), [Point(-15, -10), Point(15, -10),
                                       Point(15, 10), Point(-15, 10)])
        road = Road.from_points([Point(-20, -10), Point(0, 30)])
        road.add_lane(0, 20)
        city = City()
        city.add_road(road)
        city.add_block(block)
        city.add_building(building)
        self.assertEqual(city.bounding_box(), BoundingBox(Point(-60, -20), Point(40, 80, 25)))
