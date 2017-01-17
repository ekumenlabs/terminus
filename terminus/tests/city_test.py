import unittest

from geometry.point import Point
from models.city import City
from models.road import *
from models.street import Street


class CityTest(unittest.TestCase):

    def setUp(self):
        self.city = City()

    def test_add_intersection_at_on_single_street(self):
        '''Even if we only add a single street (hence there is no other
        street to intersect with) the intersection is created'''

        self.city.add_intersection_at(Point(0, 0))
        street = Street.from_points([Point(0, 0), Point(100, 0)])
        self.city.add_road(street)
        self.assertEquals(street.nodes[0], IntersectionNode.on(0, 0))
        self.assertEquals(street.nodes[1], SimpleNode.on(100, 0))

    def test_add_intersection_at_is_order_independent(self):
        '''No matter if we create the intersection before or after adding the
        street, the nodes are properly setup'''

        self.city.add_intersection_at(Point(0, 0))
        street = Street.from_points([Point(0, 0), Point(100, 0)])
        self.city.add_road(street)
        self.city.add_intersection_at(Point(100, 0))
        self.assertEquals(street.nodes[0], IntersectionNode.on(0, 0))
        self.assertEquals(street.nodes[1], IntersectionNode.on(100, 0))

    def test_add_intersection_at_on_two_streets(self):
        '''Check that both streets get the intersection node and that
        the same node is shared between them'''

        self.city.add_intersection_at(Point(0, 0))
        street1 = Street.from_points([Point(0, 0), Point(100, 0)])
        street2 = Street.from_points([Point(0, 0), Point(100, 100)])
        self.city.add_road(street1)
        self.city.add_road(street2)
        expected_node = IntersectionNode.on(0, 0)
        self.assertEquals(street1.nodes[0], expected_node)
        self.assertEquals(street2.nodes[0], expected_node)
        self.assertTrue(street1.nodes[0] is street2.nodes[0])

    def test_add_intersection_at_on_different_z_order(self):
        '''Check that the z component of the point does make a difference'''

        self.city.add_intersection_at(Point(0, 0))
        street1 = Street.from_points([Point(0, 0), Point(100, 0)])
        street2 = Street.from_points([Point(0, 0, 1), Point(100, 100)])
        self.city.add_road(street1)
        self.city.add_road(street2)
        self.assertEquals(street1.nodes[0], IntersectionNode.on(0, 0))
        self.assertEquals(street2.nodes[0], SimpleNode.on(0, 0, 1))
