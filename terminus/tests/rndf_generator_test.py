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

import unittest

from geometry.point import Point
from geometry.latlon import LatLon
from models.city import City
from models.road import *
from models.street import Street
from models.trunk import Trunk

from generators.rndf_generator import RNDFGenerator

from test_cities_generator import TestCitiesGenerator

import textwrap


class RNDFGeneratorTest(unittest.TestCase):

    def setUp(self):
        # print full diff in test output
        self.maxDiff = None
        self.test_generator = TestCitiesGenerator()

    def _generate_rndf(self, city):
        self.generator = RNDFGenerator(city, LatLon(10, 65))
        self.generated_contents = self.generator.generate()
        # print "###########################################"
        # print self.generated_contents
        # print "###########################################"

    def _assert_contents_are(self, expected_contents):
        expected = textwrap.dedent(expected_contents)[1:]
        self.assertMultiLineEqual(self.generated_contents, expected)

    def test_empty_city(self):
        city = self.test_generator.empty_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tEmpty
        num_segments\t0
        num_zones\t0
        format_version\t1.0
        end_file""")

    def test_simple_street(self):
        city = self.test_generator.simple_street_city()
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
        num_waypoints\t2
        lane_width\t13
        1.1.1\t10.000000\t65.000000
        1.1.2\t10.000000\t65.001824
        end_lane
        end_segment
        end_file""")

    def test_cross_intersection(self):
        city = self.test_generator.cross_intersection_city()
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
        lane_width\t13
        exit\t1.1.2\t2.1.3
        1.1.1\t10.000000\t64.999088
        1.1.2\t10.000000\t64.999936
        1.1.3\t10.000000\t65.000064
        1.1.4\t10.000000\t65.000912
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t4
        lane_width\t13
        exit\t2.1.2\t1.1.3
        2.1.1\t10.000904\t65.000000
        2.1.2\t10.000063\t65.000000
        2.1.3\t9.999937\t65.000000
        2.1.4\t9.999096\t65.000000
        end_lane
        end_segment
        end_file""")

    def test_L_intersection(self):
        city = self.test_generator.L_intersection_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tL intersection
        num_segments\t2
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t3
        lane_width\t13
        exit\t1.1.2\t2.1.2
        1.1.1\t10.000904\t65.000000
        1.1.2\t10.000063\t65.000000
        1.1.3\t10.000000\t65.000000
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t3
        lane_width\t13
        2.1.1\t10.000000\t65.000000
        2.1.2\t10.000000\t65.000064
        2.1.3\t10.000000\t65.000912
        end_lane
        end_segment
        end_file""")

    def test_Y_intersection_one_to_many(self):
        city = self.test_generator.Y_intersection_one_to_many_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tY intersection - One to many
        num_segments\t3
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t3
        lane_width\t13
        exit\t1.1.2\t2.1.2
        exit\t1.1.2\t3.1.2
        1.1.1\t10.000904\t65.000000
        1.1.2\t10.000063\t65.000000
        1.1.3\t10.000000\t65.000000
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t3
        lane_width\t13
        2.1.1\t10.000000\t65.000000
        2.1.2\t9.999955\t64.999955
        2.1.3\t9.999096\t64.999088
        end_lane
        end_segment
        segment\t3
        num_lanes\t1
        segment_name\ts3
        lane\t3.1
        num_waypoints\t3
        lane_width\t13
        3.1.1\t10.000000\t65.000000
        3.1.2\t9.999955\t65.000045
        3.1.3\t9.999096\t65.000912
        end_lane
        end_segment
        end_file""")

    def test_Y_intersection_many_to_one(self):
        city = self.test_generator.Y_intersection_many_to_one_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tY intersection - Many to one
        num_segments\t3
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t3
        lane_width\t13
        1.1.1\t10.000000\t65.000000
        1.1.2\t10.000063\t65.000000
        1.1.3\t10.000904\t65.000000
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t3
        lane_width\t13
        exit\t2.1.2\t1.1.2
        2.1.1\t9.999096\t64.999088
        2.1.2\t9.999955\t64.999955
        2.1.3\t10.000000\t65.000000
        end_lane
        end_segment
        segment\t3
        num_lanes\t1
        segment_name\ts3
        lane\t3.1
        num_waypoints\t3
        lane_width\t13
        exit\t3.1.2\t1.1.2
        3.1.1\t9.999096\t65.000912
        3.1.2\t9.999955\t65.000045
        3.1.3\t10.000000\t65.000000
        end_lane
        end_segment
        end_file""")

    def test_T_intersection_out_city(self):
        city = self.test_generator.T_intersection_out_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tT intersection out
        num_segments\t2
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t3
        lane_width\t13
        exit\t1.1.2\t2.1.2
        1.1.1\t10.000000\t64.999088
        1.1.2\t10.000000\t64.999936
        1.1.3\t10.000000\t65.000912
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t3
        lane_width\t13
        2.1.1\t10.000000\t65.000000
        2.1.2\t9.999937\t65.000000
        2.1.3\t9.999096\t65.000000
        end_lane
        end_segment
        end_file""")

    def test_T_intersection_in_city(self):
        city = self.test_generator.T_intersection_in_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tT intersection in
        num_segments\t2
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t3
        lane_width\t13
        1.1.1\t10.000000\t64.999088
        1.1.2\t10.000000\t65.000064
        1.1.3\t10.000000\t65.000912
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t3
        lane_width\t13
        exit\t2.1.2\t1.1.2
        2.1.1\t9.999096\t65.000000
        2.1.2\t9.999937\t65.000000
        2.1.3\t10.000000\t65.000000
        end_lane
        end_segment
        end_file""")

    def test_two_non_collinear_segments_border_city(self):
        city = self.test_generator.two_non_collinear_segments_border_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tNon collinear segments - Border
        num_segments\t1
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t4
        lane_width\t13
        1.1.1\t10.000000\t64.999909
        1.1.2\t10.000000\t65.000000
        1.1.3\t10.000018\t65.000091
        1.1.4\t10.000063\t65.000182
        end_lane
        end_segment
        end_file""")

    def test_two_non_collinear_segments_less_than_border_city(self):
        city = self.test_generator.two_non_collinear_segments_less_than_border_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tNon collinear segments - Less than border
        num_segments\t1
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t4
        lane_width\t13
        1.1.1\t10.000000\t64.999909
        1.1.2\t10.000000\t65.000000
        1.1.3\t10.000018\t65.000036
        1.1.4\t10.000063\t65.000182
        end_lane
        end_segment
        end_file""")

    def test_S_road_city(self):
        city = self.test_generator.S_road_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tS road
        num_segments\t1
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t4
        lane_width\t13
        1.1.1\t10.000000\t65.000000
        1.1.2\t10.000000\t65.000456
        1.1.3\t10.000136\t65.000456
        1.1.4\t10.000136\t65.000912
        end_lane
        end_segment
        end_file""")
