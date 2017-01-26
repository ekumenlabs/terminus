import unittest

from geometry.point import Point
from models.road import *
from models.street import Street
from models.trunk import Trunk
from models.city import City
from models.lane import Lane
from models.waypoint import Waypoint


class LaneTest(unittest.TestCase):
    '''
    Note: waypoints are identified as follows:
      - W: Normal waypoint.
      - I: Entry waypoint.
      - O: Exit waypoint.

    '''
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

    def test_geometry_extension_for_T_shaped_intersection_one_lane(self):
        '''
        Original Roads               Derived Lanes

                                     ------*------ (y=2)
        --------- (y=0)                    |
            |                        ------*------ (y=-2)
            |                              |

        In this case the lane of the vertical street needs to be extended to
        touch the upper lane of the trunk
        '''
        horizontal_street = Trunk.from_points(self.horizontal_points)
        vertical_street = Street.from_points([Point(0, 0), Point(0, -1000)])

        city = City()
        city.add_intersection_at(Point(0, 0))
        city.add_road(horizontal_street)
        city.add_road(vertical_street)

        lane = vertical_street.lanes[0]

        expected_points = [
            Point(0, 2),
            Point(0, -1000)
        ]
        self.assertPointCollectionsAreAlmostEquals(expected_points, lane.geometry())

    def test_geometry_extension_for_T_shaped_intersection_two_lanes(self):
        '''
        Original Roads               Derived Lanes

                                     ------*------ (y=5)
                                           |
                                     ------*------ (y=2)
        --------- (y=0)                    |
            |                        ------*------ (y=-2)
            |                              |

        In this case the lane of the vertical street needs to be extended to
        touch the upper lane of the road, which means extending it two lanes.
        '''
        horizontal_road = Road.from_points(self.horizontal_points)
        horizontal_road.add_lane(-5)
        horizontal_road.add_lane(-2)
        horizontal_road.add_lane(2)
        vertical_street = Street.from_points([Point(0, 0), Point(0, -1000)])

        city = City()
        city.add_intersection_at(Point(0, 0))
        city.add_road(horizontal_road)
        city.add_road(vertical_street)

        lane = vertical_street.lanes[0]

        expected_points = [
            Point(0, 5),
            Point(0, -1000)
        ]
        self.assertPointCollectionsAreAlmostEquals(expected_points, lane.geometry())

    def test_geometry_extension_for_L_shaped_intersection_two_lanes(self):
        '''
        Original Roads               Derived Lanes

                                    *--*-------- (y=2)
            *------ (y=0)           |  |
            |                       *--*------- (y=-2)
            |                       |  |
            |                       |  |
            (x=0)               (x=-2) (x=2)

        In this case both outer lanes of the intersection needs to be extended
        in order to close the external corner at (-2, 2).
        '''
        horizontal_trunk = Trunk.from_points([Point(0, 0), Point(1000, 0)])
        vertical_trunk = Trunk.from_points([Point(0, 0), Point(0, -1000)])

        city = City()
        city.add_intersection_at(Point(0, 0))
        city.add_road(horizontal_trunk)
        city.add_road(vertical_trunk)

        inner_horizontal_lane = horizontal_trunk.lanes[0]
        expected_points = [
            Point(-2, -2),
            Point(1000, -2)
        ]
        self.assertPointCollectionsAreAlmostEquals(expected_points, inner_horizontal_lane.geometry())

        outer_horizontal_lane = horizontal_trunk.lanes[1]
        expected_points = [
            Point(-2, 2),
            Point(1000, 2)
        ]
        self.assertPointCollectionsAreAlmostEquals(expected_points, outer_horizontal_lane.geometry())

        outer_vertical_lane = vertical_trunk.lanes[0]
        expected_points = [
            Point(-2, 2),
            Point(-2, -1000)
        ]
        self.assertPointCollectionsAreAlmostEquals(expected_points, outer_vertical_lane.geometry())

        inner_vertical_lane = vertical_trunk.lanes[1]
        expected_points = [
            Point(2, 2),
            Point(2, -1000)
        ]
        self.assertPointCollectionsAreAlmostEquals(expected_points, inner_vertical_lane.geometry())

    def test_get_waypoints_no_intersection(self):

        # No offset
        street = Street.from_points(self.horizontal_points)

        lane = Lane(street, 5, 0)
        expected_points = lane.geometry()
        expected_waypoints = map(lambda point: Waypoint(lane, lane, point), expected_points)
        self.assertEquals(expected_waypoints, lane.get_waypoints())

        # Positive offset
        lane = Lane(street, 5, 5)
        expected_points = lane.geometry()
        expected_waypoints = map(lambda point: Waypoint(lane, lane, point), expected_points)
        self.assertEquals(expected_waypoints, lane.get_waypoints())

        # Negative offset
        lane = Lane(street, 5, 5)
        expected_points = lane.geometry()
        expected_waypoints = map(lambda point: Waypoint(lane, lane, point), expected_points)
        self.assertEquals(expected_waypoints, lane.get_waypoints())

    def test_get_waypoints_single_intersection_no_offset(self):
        '''
                 |
                 |
            --*--+--*--
                 |
                 |
        '''
        horizontal_street = Street.from_points(self.horizontal_points)
        vertical_street = Street.from_points(self.vertical_points)

        city = City()
        city.add_intersection_at(Point(0, 0))
        city.add_road(horizontal_street)
        city.add_road(vertical_street)

        lane = horizontal_street.lanes[0]

        expected_waypoints = [
            Waypoint(lane, None, Point(-1000, 0)),
            Waypoint.exit(lane, None, Point(-5, 0)),
            Waypoint.entry(lane, None, Point(5, 0)),
            Waypoint(lane, None, Point(1000, 0))
        ]

        self.assertEquals(expected_waypoints, lane.get_waypoints())

    def test_get_waypoints_single_intersection_45_deg_no_offset(self):
        '''
                   /
                  /
            --*--+--*--
                /
               /
        '''
        horizontal_street = Street.from_points(self.horizontal_points)
        diagonal_street = Street.from_points(self.diagonal_points)

        city = City()
        city.add_intersection_at(Point(0, 0))
        city.add_road(horizontal_street)
        city.add_road(diagonal_street)

        lane = horizontal_street.lanes[0]

        expected_waypoints = [
            Waypoint(lane, None, Point(-1000, 0)),
            Waypoint.exit(lane, None, Point(-5, 0)),
            Waypoint.entry(lane, None, Point(5, 0)),
            Waypoint(lane, None, Point(1000, 0))
        ]

        self.assertEquals(expected_waypoints, lane.get_waypoints())

    def test_get_waypoints_complex_intersection_no_offset(self):
        '''
        Not that, even though there are three lanes in the same intersection,
        we get just two wayponints, as the relative distance to the intersection
        point is the same (and we shouldn't get two waypoints at the same point)

                 | /
                 |/
            --*--+--*--
                /|
               / |
        '''
        horizontal_street = Street.from_points(self.horizontal_points)
        vertical_street = Street.from_points(self.vertical_points)
        diagonal_street = Street.from_points(self.diagonal_points)

        city = City()
        city.add_intersection_at(Point(0, 0))
        city.add_road(horizontal_street)
        city.add_road(vertical_street)
        city.add_road(diagonal_street)

        lane = horizontal_street.lanes[0]

        expected_waypoints = [
            Waypoint(lane, None, Point(-1000, 0)),
            Waypoint.exit(lane, None, Point(-5, 0)),
            Waypoint.entry(lane, None, Point(5, 0)),
            Waypoint(lane, None, Point(1000, 0))
        ]

        self.assertEquals(expected_waypoints, lane.get_waypoints())

    def test_get_waypoints_single_intersection_two_lanes(self):
        '''
        Note that since the default lane width is 4 meters and we use 5 meters
        distance to define the crossing waypoints we will get first the two exit
        ones and then the two entry ones
                    |        |
                    ^        ^
                    |        |
            -->--O--+--O--I--+--I-->--
                    |        |
            -->--O--+--O--I--+--I-->--
                    |        |
                    ^        ^
                    |        |
        '''
        horizontal_trunk = Trunk.from_points(self.horizontal_points)
        vertical_trunk = Trunk.from_points(self.vertical_points)

        city = City()
        city.add_intersection_at(Point(0, 0))
        city.add_road(horizontal_trunk)
        city.add_road(vertical_trunk)

        horizontal_lane_1 = horizontal_trunk.lanes[0]
        horizontal_lane_2 = horizontal_trunk.lanes[1]

        expected_waypoints_lane_1 = [
            Waypoint(horizontal_lane_1, None, Point(-1000, -2)),
            Waypoint.exit(horizontal_lane_1, None, Point(-7, -2)),
            Waypoint.exit(horizontal_lane_1, None, Point(-2, -2)),
            Waypoint.entry(horizontal_lane_1, None, Point(2, -2)),
            Waypoint.entry(horizontal_lane_1, None, Point(7, -2)),
            Waypoint(horizontal_lane_1, None, Point(1000, -2))
        ]

        expected_waypoints_lane_2 = [
            Waypoint(horizontal_lane_2, None, Point(-1000, 2)),
            Waypoint.exit(horizontal_lane_2, None, Point(-7, 2)),
            Waypoint.exit(horizontal_lane_2, None, Point(-2, 2)),
            Waypoint.entry(horizontal_lane_2, None, Point(2, 2)),
            Waypoint.entry(horizontal_lane_2, None, Point(7, 2)),
            Waypoint(horizontal_lane_2, None, Point(1000, 2))
        ]

        self.assertEquals(expected_waypoints_lane_1, horizontal_lane_1.get_waypoints())
        self.assertEquals(expected_waypoints_lane_2, horizontal_lane_2.get_waypoints())

    def test_get_waypoints_single_intersection_two_lanes_overlapping(self):
        '''
        Make the lane be separated by using a 5 meters offset. With this value,
        the entry and exit waypoint should overlap.

                    |       |
                    ^       ^
                    |       |
            -->--O--+--I/O--+--I-->--
                    |       |
            -->--O--+--I/O--+--I-->--
                    |       |
                    ^       ^
                    |       |
        '''
        horizontal_trunk = Road.from_points(self.horizontal_points)
        horizontal_trunk.add_lane(5)
        horizontal_trunk.add_lane(-5)
        vertical_trunk = Road.from_points(self.vertical_points)
        vertical_trunk.add_lane(5)
        vertical_trunk.add_lane(-5)

        city = City()
        city.add_intersection_at(Point(0, 0))
        city.add_road(horizontal_trunk)
        city.add_road(vertical_trunk)

        horizontal_lane_1 = horizontal_trunk.lanes[0]
        horizontal_lane_2 = horizontal_trunk.lanes[1]

        expected_waypoints_lane_1 = [
            Waypoint(horizontal_lane_1, None, Point(-1000, -5)),
            Waypoint.exit(horizontal_lane_1, None, Point(-10, -5)),
            Waypoint.entry(horizontal_lane_1, None, Point(0, -5)),
            Waypoint.exit(horizontal_lane_1, None, Point(0, -5)),
            Waypoint.entry(horizontal_lane_1, None, Point(10, -5)),
            Waypoint(horizontal_lane_1, None, Point(1000, -5))
        ]

        expected_waypoints_lane_2 = [
            Waypoint(horizontal_lane_2, None, Point(-1000, 5)),
            Waypoint.exit(horizontal_lane_2, None, Point(-10, 5)),
            Waypoint.entry(horizontal_lane_2, None, Point(0, 5)),
            Waypoint.exit(horizontal_lane_2, None, Point(0, 5)),
            Waypoint.entry(horizontal_lane_2, None, Point(10, 5)),
            Waypoint(horizontal_lane_2, None, Point(1000, 5))
        ]

        self.assertEquals(expected_waypoints_lane_1, horizontal_lane_1.get_waypoints())
        self.assertEquals(expected_waypoints_lane_2, horizontal_lane_2.get_waypoints())

    def test_get_waypoints_single_intersection_two_lanes_big_offset(self):
        '''
        Finally, separate the lanes more than 5 meters. Then we should get the
        O-I-O-I sequence in the waypoints.

                    |        |
                    ^        ^
                    |        |
            -->--O--+--I--O--+--I-->--
                    |        |
            -->--O--+--I--O--+--I-->--
                    |        |
                    ^        ^
                    |        |
        '''
        horizontal_trunk = Road.from_points(self.horizontal_points)
        horizontal_trunk.add_lane(7)
        horizontal_trunk.add_lane(-7)
        vertical_trunk = Road.from_points(self.vertical_points)
        vertical_trunk.add_lane(7)
        vertical_trunk.add_lane(-7)

        city = City()
        city.add_intersection_at(Point(0, 0))
        city.add_road(horizontal_trunk)
        city.add_road(vertical_trunk)

        horizontal_lane_1 = horizontal_trunk.lanes[0]
        horizontal_lane_2 = horizontal_trunk.lanes[1]

        expected_waypoints_lane_1 = [
            Waypoint(horizontal_lane_1, None, Point(-1000, -7)),
            Waypoint.exit(horizontal_lane_1, None, Point(-12, -7)),
            Waypoint.entry(horizontal_lane_1, None, Point(-2, -7)),
            Waypoint.exit(horizontal_lane_1, None, Point(2, -7)),
            Waypoint.entry(horizontal_lane_1, None, Point(12, -7)),
            Waypoint(horizontal_lane_1, None, Point(1000, -7))
        ]

        expected_waypoints_lane_2 = [
            Waypoint(horizontal_lane_2, None, Point(-1000, 7)),
            Waypoint.exit(horizontal_lane_2, None, Point(-12, 7)),
            Waypoint.entry(horizontal_lane_2, None, Point(-2, 7)),
            Waypoint.exit(horizontal_lane_2, None, Point(2, 7)),
            Waypoint.entry(horizontal_lane_2, None, Point(12, 7)),
            Waypoint(horizontal_lane_2, None, Point(1000, 7))
        ]

        self.assertEquals(expected_waypoints_lane_1, horizontal_lane_1.get_waypoints())
        self.assertEquals(expected_waypoints_lane_2, horizontal_lane_2.get_waypoints())

    def test_get_waypoints_T_shaped_intersection_two_lanes_exit_only(self):
        '''

            -->--O--W---O--W---->--
                    |      |
            -->--O--W--IO--W--I-->--
                    |      |
                    v      v
                    |      |
        '''
        horizontal_trunk = Road.from_points(self.horizontal_points)
        horizontal_trunk.add_lane(-7)
        horizontal_trunk.add_lane(7)
        vertical_trunk = Road.from_points([Point(0, 0), Point(0, -1000)])
        vertical_trunk.add_lane(7)
        vertical_trunk.add_lane(-7)

        city = City()
        city.add_intersection_at(Point(0, 0))
        city.add_road(horizontal_trunk)
        city.add_road(vertical_trunk)

        horizontal_lane_1 = horizontal_trunk.lanes[0]
        horizontal_lane_2 = horizontal_trunk.lanes[1]

        expected_waypoints_lane_1 = [
            Waypoint(horizontal_lane_1, None, Point(-1000, 7)),
            Waypoint.exit(horizontal_lane_1, None, Point(-12, 7)),
            Waypoint(horizontal_lane_1, None, Point(-7, 7)),
            Waypoint.exit(horizontal_lane_1, None, Point(2, 7)),
            Waypoint(horizontal_lane_1, None, Point(7, 7)),
            Waypoint(horizontal_lane_1, None, Point(1000, 7))
        ]

        expected_waypoints_lane_2 = [
            Waypoint(horizontal_lane_2, None, Point(-1000, -7)),
            Waypoint.exit(horizontal_lane_2, None, Point(-12, -7)),
            Waypoint.entry(horizontal_lane_2, None, Point(-2, -7)),
            Waypoint.exit(horizontal_lane_2, None, Point(2, -7)),
            Waypoint.entry(horizontal_lane_2, None, Point(12, -7)),
            Waypoint(horizontal_lane_2, None, Point(1000, -7))
        ]

        self.assertEquals(expected_waypoints_lane_1, horizontal_lane_1.get_waypoints())
        self.assertEquals(expected_waypoints_lane_2, horizontal_lane_2.get_waypoints())

    def test_get_waypoints_L_shaped_intersection_two_lanes_exit_only(self):
        '''
            |     |
            v     v
            |     |
            O     O
            |\    |\
            |-I-O---I-------->----
            |    \|
            |    I/O
            |     |
            O     O
            |\    |\
            --I-----I--------->----
        '''
        vertical_trunk = Road.from_points([Point(0, 1000), Point(0, 0)])
        vertical_trunk.add_lane(7)
        vertical_trunk.add_lane(-7)
        horizontal_trunk = Road.from_points([Point(0, 0), Point(1000, 0)])
        horizontal_trunk.add_lane(7)
        horizontal_trunk.add_lane(-7)

        city = City()
        city.add_intersection_at(Point(0, 0))
        city.add_road(horizontal_trunk)
        city.add_road(vertical_trunk)

        vertical_lane_1 = vertical_trunk.lanes[0]

        expected_waypoints = [
            Waypoint(vertical_lane_1, None, Point(-7, 1000)),
            Waypoint.exit(vertical_lane_1, None, Point(-7, 12)),
            Waypoint(vertical_lane_1, None, Point(-7, 7)),
            Waypoint.exit(vertical_lane_1, None, Point(-7, -2)),
            Waypoint(vertical_lane_1, None, Point(-7, -7)),
        ]
        self.assertEquals(expected_waypoints, vertical_lane_1.get_waypoints())

        vertical_lane_2 = vertical_trunk.lanes[1]

        expected_waypoints = [
            Waypoint(vertical_lane_2, None, Point(7, 1000)),
            Waypoint.exit(vertical_lane_2, None, Point(7, 12)),
            Waypoint.entry(vertical_lane_2, None, Point(7, 2)),
            Waypoint.exit(vertical_lane_2, None, Point(7, -2)),
            Waypoint(vertical_lane_2, None, Point(7, -7)),
        ]
        self.assertEquals(expected_waypoints, vertical_lane_2.get_waypoints())

        horizontal_lane_1 = horizontal_trunk.lanes[0]

        expected_waypoints = [
            Waypoint(horizontal_lane_1, None, Point(-7, -7)),
            Waypoint.entry(horizontal_lane_1, None, Point(-2, -7)),
            Waypoint(horizontal_lane_1, None, Point(7, -7)),
            Waypoint.entry(horizontal_lane_1, None, Point(12, -7)),
            Waypoint(horizontal_lane_1, None, Point(1000, -7)),
        ]
        self.assertEquals(expected_waypoints, horizontal_lane_1.get_waypoints())

        horizontal_lane_2 = horizontal_trunk.lanes[1]

        expected_waypoints = [
            Waypoint(horizontal_lane_2, None, Point(-7, 7)),
            Waypoint.entry(horizontal_lane_2, None, Point(-2, 7)),
            Waypoint.exit(horizontal_lane_2, None, Point(2, 7)),
            Waypoint.entry(horizontal_lane_2, None, Point(12, 7)),
            Waypoint(horizontal_lane_2, None, Point(1000, 7)),
        ]
        self.assertEquals(expected_waypoints, horizontal_lane_2.get_waypoints())

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
