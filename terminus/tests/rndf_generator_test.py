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
import textwrap

from geometry.point import Point
from geometry.latlon import LatLon
from models.city import City
from models.road import *
from models.street import Street
from models.trunk import Trunk

from generators.rndf_generator import RNDFGenerator

from test_cities_generator import TestCitiesGenerator


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
        RNDF_name\tSingle_street
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
        1.1.2\t10.000000\t64.999954
        1.1.3\t10.000000\t65.000046
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
        2.1.2\t10.000045\t65.000000
        2.1.3\t9.999955\t65.000000
        2.1.4\t9.999096\t65.000000
        end_lane
        end_segment
        end_file""")

    def test_L_intersection(self):
        city = self.test_generator.L_intersection_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tL_intersection
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
        1.1.2\t10.000045\t65.000000
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
        2.1.2\t10.000000\t65.000046
        2.1.3\t10.000000\t65.000912
        end_lane
        end_segment
        end_file""")

    def test_Y_intersection_one_to_many(self):
        city = self.test_generator.Y_intersection_one_to_many_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tY_intersection_One_to_many
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
        1.1.2\t10.000045\t65.000000
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
        2.1.2\t9.999968\t64.999968
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
        3.1.2\t9.999968\t65.000032
        3.1.3\t9.999096\t65.000912
        end_lane
        end_segment
        end_file""")

    def test_Y_intersection_many_to_one(self):
        city = self.test_generator.Y_intersection_many_to_one_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tY_intersection_Many_to_one
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
        1.1.2\t10.000045\t65.000000
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
        2.1.2\t9.999968\t64.999968
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
        3.1.2\t9.999968\t65.000032
        3.1.3\t10.000000\t65.000000
        end_lane
        end_segment
        end_file""")

    def test_T_intersection_out_city(self):
        city = self.test_generator.T_intersection_out_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tT_intersection_out
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
        1.1.2\t10.000000\t64.999954
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
        2.1.2\t9.999955\t65.000000
        2.1.3\t9.999096\t65.000000
        end_lane
        end_segment
        end_file""")

    def test_T_intersection_in_city(self):
        city = self.test_generator.T_intersection_in_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tT_intersection_in
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
        1.1.2\t10.000000\t65.000046
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
        2.1.2\t9.999955\t65.000000
        2.1.3\t10.000000\t65.000000
        end_lane
        end_segment
        end_file""")

    def test_broken_intersection_on_one_lane_city(self):
        city = self.test_generator.broken_intersection_on_one_lane_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tBroken_intersection_One_lane
        num_segments\t2
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t5
        lane_width\t13
        exit\t1.1.2\t2.1.3
        1.1.1\t10.000000\t64.999544
        1.1.2\t10.000000\t64.999954
        1.1.3\t10.000000\t65.000000
        1.1.4\t10.000017\t65.000042
        1.1.5\t10.000181\t65.000456
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t4
        lane_width\t13
        exit\t2.1.2\t1.1.4
        2.1.1\t9.999548\t65.000000
        2.1.2\t9.999955\t65.000000
        2.1.3\t10.000045\t65.000000
        2.1.4\t10.000452\t65.000000
        end_lane
        end_segment
        end_file""")

    def test_broken_intersection_on_two_lanes_city(self):
        city = self.test_generator.broken_intersection_on_two_lanes_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tBroken_intersection_Two_lanes
        num_segments\t2
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t5
        lane_width\t13
        exit\t1.1.2\t2.1.4
        1.1.1\t10.000000\t64.999544
        1.1.2\t10.000000\t64.999954
        1.1.3\t10.000000\t65.000000
        1.1.4\t10.000017\t65.000042
        1.1.5\t10.000181\t65.000456
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t5
        lane_width\t13
        exit\t2.1.2\t1.1.4
        2.1.1\t9.999548\t65.000000
        2.1.2\t9.999955\t65.000000
        2.1.3\t10.000000\t65.000000
        2.1.4\t10.000044\t65.000009
        2.1.5\t10.000452\t65.000091
        end_lane
        end_segment
        end_file""")

    def test_road_ends_in_intersection_city(self):
        city = self.test_generator.road_ends_in_intersection_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tRoad_ends_in_intersection
        num_segments\t2
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t4
        lane_width\t13
        1.1.1\t10.000000\t64.999544
        1.1.2\t10.000000\t65.000000
        1.1.3\t10.000023\t65.000039
        1.1.4\t10.000271\t65.000456
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t3
        lane_width\t13
        exit\t2.1.2\t1.1.3
        2.1.1\t9.999548\t65.000000
        2.1.2\t9.999955\t65.000000
        2.1.3\t10.000000\t65.000000
        end_lane
        end_segment
        end_file""")

    def test_two_non_collinear_segments_city(self):
        city = self.test_generator.non_collinear_segments_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tNon_collinear_segments_Standard
        num_segments\t1
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t3
        lane_width\t13
        1.1.1\t10.000000\t64.999088
        1.1.2\t10.000000\t65.000000
        1.1.3\t10.000271\t65.000912
        end_lane
        end_segment
        end_file""")

    def test_two_non_collinear_segments_border_city(self):
        city = self.test_generator.two_non_collinear_segments_border_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tNon_collinear_segments_Border
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
        RNDF_name\tNon_collinear_segments_Less_than_border
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
        RNDF_name\tS_road
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

    def test_trunk_to_street_city(self):
        city = self.test_generator.trunk_to_street_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tTrunk_to_street
        num_segments\t2
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t2
        segment_name\tt1
        lane\t1.1
        num_waypoints\t2
        lane_width\t13
        1.1.1\t10.000018\t65.000456
        1.1.2\t10.000018\t65.000000
        end_lane
        lane\t1.2
        num_waypoints\t3
        lane_width\t13
        exit\t1.2.2\t2.1.2
        1.2.1\t9.999982\t65.000000
        1.2.2\t9.999982\t65.000414
        1.2.3\t9.999982\t65.000456
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts1
        lane\t2.1
        num_waypoints\t3
        lane_width\t13
        2.1.1\t10.000000\t65.000456
        2.1.2\t10.000000\t65.000502
        2.1.3\t10.000000\t65.000912
        end_lane
        end_segment
        end_file""")

    def test_trunk_from_street_city(self):
        city = self.test_generator.trunk_from_street_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tTrunk_from_street
        num_segments\t2
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t2
        segment_name\tt1
        lane\t1.1
        num_waypoints\t3
        lane_width\t13
        1.1.1\t10.000018\t65.000456
        1.1.2\t10.000018\t65.000414
        1.1.3\t10.000018\t65.000000
        end_lane
        lane\t1.2
        num_waypoints\t2
        lane_width\t13
        1.2.1\t9.999982\t65.000000
        1.2.2\t9.999982\t65.000456
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts1
        lane\t2.1
        num_waypoints\t3
        lane_width\t13
        exit\t2.1.2\t1.1.2
        2.1.1\t10.000000\t65.000912
        2.1.2\t10.000000\t65.000502
        2.1.3\t10.000000\t65.000456
        end_lane
        end_segment
        end_file""")

    def test_collinear_streets_city(self):
        city = self.test_generator.collinear_streets_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tCollinear_streets
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
        1.1.1\t10.000000\t65.000000
        1.1.2\t10.000000\t65.000410
        1.1.3\t10.000000\t65.000456
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t3
        lane_width\t13
        2.1.1\t10.000000\t65.000456
        2.1.2\t10.000000\t65.000502
        2.1.3\t10.000000\t65.000912
        end_lane
        end_segment
        end_file""")
