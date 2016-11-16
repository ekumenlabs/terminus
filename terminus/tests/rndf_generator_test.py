import unittest

from geometry.point import Point
from models.city import City
from models.road import *
from models.street import Street
from models.trunk import Trunk

from generators.rndf_generator import RNDFGenerator

import textwrap


class RNDFGeneratorTest(unittest.TestCase):

    def _generate_rndf(self, city):
        self.generator = RNDFGenerator(city, Point(45, 65))
        self.generated_contents = self.generator.generate()
        # print "###########################################"
        # print self.generated_contents
        # print "###########################################"

    def _assert_contents_are(self, expected_contents):
        expected = textwrap.dedent(expected_contents)[1:]
        self.assertMultiLineEqual(self.generated_contents, expected)

    def test_empty_city(self):
        city = City("Empty")
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tEmpty
        num_segments\t0
        num_zones\t0
        format_version\t1.0
        end_file""")

    def test_simple_street(self):
        city = City("Single street")
        street = Street.from_nodes([
            SimpleNode.on(0, 0),
            SimpleNode.on(1000, 0),
            SimpleNode.on(2000, 0)
        ])
        street.name = "s1"
        city.add_road(street)
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tSingle street
        num_segments\t1
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t3
        lane_width\t5
        1.1.1\t45.000000\t65.000000
        1.1.2\t45.008983\t65.000000
        1.1.3\t45.017966\t65.000000
        end_lane
        end_segment
        end_file""")

    def test_cross_junction(self):

        """
             (0,1)
        (-1,0) + (1,0)
             (0,-1)
        """
        city = City("Cross")
        junction = JunctionNode.on(0, 0)

        s1 = Street.from_nodes([
            SimpleNode.on(-1000, 0),
            junction,
            SimpleNode.on(1000, 0)
        ])
        s1.name = "s1"

        s2 = Street.from_nodes([
            SimpleNode.on(0, 1000),
            junction,
            SimpleNode.on(0, -1000)
        ])
        s2.name = "s2"
        city.add_road(s1)
        city.add_road(s2)

        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tCross
        num_segments\t2
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t4
        lane_width\t5
        exit\t1.1.2\t2.1.3
        1.1.1\t44.991017\t65.000000
        1.1.2\t44.999955\t65.000000
        1.1.3\t45.000045\t65.000000
        1.1.4\t45.008983\t65.000000
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t4
        lane_width\t5
        exit\t2.1.2\t1.1.3
        2.1.1\t45.000000\t65.017100
        2.1.2\t45.000000\t65.000086
        2.1.3\t45.000000\t64.999914
        2.1.4\t45.000000\t64.982900
        end_lane
        end_segment
        end_file""")
