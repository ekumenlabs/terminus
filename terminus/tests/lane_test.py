import unittest

from geometry.point import Point
from models.road import *
from models.street import Street
from models.lane import Lane


class LaneTest(unittest.TestCase):
    def setUp(self):
        self.horizontal_points = [Point(-1000, 0), Point(0, 0), Point(1000, 0)]
        self.vertical_points = [Point(0, -1000), Point(0, 0), Point(0, 1000)]
        self.diagonal_points = [Point(-1000, -1000), Point(0, 0), Point(1000, 1000)]

    def test_geometry_for_straight_streets_no_offset(self):
        geometries = [
            self.horizontal_points,
            self.vertical_points,
            self.diagonal_points
        ]
        for points in geometries:
            street = Street.from_points(points)
            lane = Lane(street, 5, 0)
            self.assertEquals(points, lane.geometry())

    def test_geometry_for_straight_streets_positive_offset(self):
        street = Street.from_points(self.horizontal_points)
        lane = Lane(street, 5, 5)
        expected_points = [Point(-1000, -5), Point(0, -5), Point(1000, -5)]
        self.assertPointCollectionsAreAlmostEquals(expected_points, lane.geometry())

        street = Street.from_points(self.vertical_points)
        lane = Lane(street, 5, 5)
        expected_points = [Point(5, -1000), Point(5, 0), Point(5, 1000)]
        self.assertPointCollectionsAreAlmostEquals(expected_points, lane.geometry())

        # Note that 5 is the hypotenuse in this case , so 5^2 = a^2 + b^2.
        # Since we are working on a 45 deg line, 25 = 2 * a^2 and hence
        # delta_x = delta_y ~= 3.53553390593
        street = Street.from_points(self.diagonal_points)
        lane = Lane(street, 5, 5)
        expected_points = [
            Point(-996.464466094, -1003.53553391),
            Point(3.53553390593, -3.53553390593),
            Point(1003.53553390593, 996.464466094)
        ]
        self.assertPointCollectionsAreAlmostEquals(expected_points, lane.geometry())

    def test_geometry_for_straight_streets_negative_offset(self):
        street = Street.from_points(self.horizontal_points)
        lane = Lane(street, 5, -5)
        expected_points = [Point(-1000, 5), Point(0, 5), Point(1000, 5)]
        self.assertPointCollectionsAreAlmostEquals(expected_points, lane.geometry())

        street = Street.from_points(self.vertical_points)
        lane = Lane(street, 5, -5)
        expected_points = [Point(-5, -1000), Point(-5, 0), Point(-5, 1000)]
        self.assertPointCollectionsAreAlmostEquals(expected_points, lane.geometry())

        # Note that 5 is the hypotenuse in this case , so 5^2 = a^2 + b^2.
        # Since we are working on a 45 deg line, 25 = 2 * a^2 and hence
        # delta_x = delta_y ~= 3.53553390593
        street = Street.from_points(self.diagonal_points)
        lane = Lane(street, 5, -5)
        expected_points = [
            Point(-1003.53553391, -996.464466094),
            Point(-3.53553390593, 3.53553390593),
            Point(996.464466094, 1003.53553390593)
        ]
        self.assertPointCollectionsAreAlmostEquals(expected_points, lane.geometry())

    def test_geometry_for_90_deg_corner(self):
        ''' *----*
                 |
                 |
                 *
        '''
        street = Street.from_points([
            Point(100, 100),
            Point(200, 100),
            Point(200, 0)
        ])

        inner_lane = Lane(street, 5, 5)
        inner_points = [
            Point(100, 95),
            Point(195, 95),
            Point(195, 0)
        ]
        self.assertPointCollectionsAreAlmostEquals(inner_points, inner_lane.geometry())

        outer_lane = Lane(street, 5, -5)
        outer_points = [
            Point(100, 105),
            Point(205, 105),
            Point(205, 0)
        ]
        self.assertPointCollectionsAreAlmostEquals(outer_points, outer_lane.geometry())

    def test_geometry_for_45_deg_corner(self):
        ''' *----*
                  \
                   \
                    *
                    |
                    |
                    *
        '''
        street = Street.from_points([
            Point(100, 100),
            Point(200, 100),
            Point(300, 0),
            Point(300, -100)
        ])

        inner_lane = Lane(street, 5, 5)
        inner_points = [
            Point(100, 95),
            Point(197.9289321, 95),
            Point(295, -2.0710678),
            Point(295, -100)
        ]
        self.assertPointCollectionsAreAlmostEquals(inner_points, inner_lane.geometry())

        outer_lane = Lane(street, 5, -5)
        outer_points = [
            Point(100, 105),
            Point(202.0710678, 105),
            Point(305, 2.0710678),
            Point(305, -100)
        ]
        self.assertPointCollectionsAreAlmostEquals(outer_points, outer_lane.geometry())

    def test_geometry_for_U_shaped_street(self):
        ''' *    *
            |    |
            |    |
            *----*
        '''
        street = Street.from_points([
            Point(100, 100),
            Point(100, 0),
            Point(200, 0),
            Point(200, 100)
        ])

        inner_lane = Lane(street, 5, -5)
        inner_points = [
            Point(105, 100),
            Point(105, 5),
            Point(195, 5),
            Point(195, 100)
        ]
        self.assertPointCollectionsAreAlmostEquals(inner_points, inner_lane.geometry())

        outer_lane = Lane(street, 5, 5)
        outer_points = [
            Point(95, 100),
            Point(95, -5),
            Point(205, -5),
            Point(205, 100)
        ]
        self.assertPointCollectionsAreAlmostEquals(outer_points, outer_lane.geometry())

    def test_geometry_for_almost_square_shaped_street(self):
        ''' * ---*
            |    |
            |    |
            *----*
        '''
        street = Street.from_points([
            Point(100, 100),
            Point(100, 0),
            Point(200, 0),
            Point(200, 100),
            Point(110, 100),
        ])

        inner_lane = Lane(street, 5, -5)
        inner_points = [
            Point(105, 100),
            Point(105, 5),
            Point(195, 5),
            Point(195, 95),
            Point(110, 95)
        ]
        self.assertPointCollectionsAreAlmostEquals(inner_points, inner_lane.geometry())

        outer_lane = Lane(street, 5, 5)
        outer_points = [
            Point(95, 100),
            Point(95, -5),
            Point(205, -5),
            Point(205, 105),
            Point(110, 105)
        ]
        self.assertPointCollectionsAreAlmostEquals(outer_points, outer_lane.geometry())

    def assertPointCollectionsAreAlmostEquals(self, collection1, collection2):
        if (len(collection1) != len(collection2)):
            # Fail with standard error
            self.assertEquals(collection1, collection2)

        for point1, point2 in zip(collection1, collection2):
            self.assertPointsAreAlmostEquals(point1, point2)

    def assertPointsAreAlmostEquals(self, point1, point2):
        self.assertAlmostEquals(point1.x, point2.x, 1)
        self.assertAlmostEquals(point1.y, point2.y, 1)
        self.assertAlmostEquals(point1.z, point2.z, 1)
