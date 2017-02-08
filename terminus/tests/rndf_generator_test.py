import unittest

from geometry.point import Point
from geometry.latlon import LatLon
from models.city import City
from models.road import *
from models.street import Street
from models.trunk import Trunk

from generators.rndf_generator import RNDFGenerator

from common_generator_test_cases import generate_cross_intersection_city
from common_generator_test_cases import generate_empty_city
from common_generator_test_cases import generate_L_intersection_city
from common_generator_test_cases import generate_simple_street_city
from common_generator_test_cases import generate_Y_intersection_one_to_many_city
from common_generator_test_cases import generate_Y_intersection_many_to_one_city

import textwrap


class RNDFGeneratorTest(unittest.TestCase):

    def setUp(self):
        # print full diff in test output
        self.maxDiff = None

    def _generate_rndf(self, city):
        self.generator = RNDFGenerator(city, LatLon(45, 65))
        self.generated_contents = self.generator.generate()
        # print "###########################################"
        # print self.generated_contents
        # print "###########################################"

    def _assert_contents_are(self, expected_contents):
        expected = textwrap.dedent(expected_contents)[1:]
        self.assertMultiLineEqual(self.generated_contents, expected)

    def test_empty_city(self):
        city = generate_empty_city()
        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tEmpty
        num_segments\t0
        num_zones\t0
        format_version\t1.0
        end_file""")

    def test_simple_street(self):
        city = generate_simple_street_city()
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
        lane_width\t13
        1.1.1\t45.000000\t65.000000
        1.1.2\t45.000000\t65.012704
        1.1.3\t45.000000\t65.025408
        end_lane
        end_segment
        end_file""")

    def test_cross_intersection(self):
        """
             (0,1)
        (-1,0) + (1,0)
             (0,-1)
        """
        city = generate_cross_intersection_city()

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
        1.1.1\t45.000000\t64.987296
        1.1.2\t45.000000\t64.999936
        1.1.3\t45.000000\t65.000064
        1.1.4\t45.000000\t65.012704
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t4
        lane_width\t13
        exit\t2.1.2\t1.1.3
        2.1.1\t45.008983\t65.000000
        2.1.2\t45.000045\t65.000000
        2.1.3\t44.999955\t65.000000
        2.1.4\t44.991017\t65.000000
        end_lane
        end_segment
        end_file""")

    def test_L_intersection(self):
        """
             (0,1)
               +  (1,0)
        """
        city = generate_L_intersection_city()

        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tLCross
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
        1.1.1\t45.008983\t65.000000
        1.1.2\t45.000045\t65.000000
        1.1.3\t45.000000\t65.000000
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t3
        lane_width\t13
        2.1.1\t45.000000\t65.000000
        2.1.2\t45.000000\t65.000064
        2.1.3\t45.000000\t65.012704
        end_lane
        end_segment
        end_file""")

    def test_Y_intersection_one_to_many(self):
        """
                  (0,1)
                    +
            (-1,-1)   (1,-1)
        """
        city = generate_Y_intersection_one_to_many_city()

        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tYCross
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
        1.1.1\t45.008983\t65.000000
        1.1.2\t45.000045\t65.000000
        1.1.3\t45.000000\t65.000000
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t3
        lane_width\t13
        2.1.1\t45.000000\t65.000000
        2.1.2\t44.999968\t64.999955
        2.1.3\t44.991017\t64.987296
        end_lane
        end_segment
        segment\t3
        num_lanes\t1
        segment_name\ts3
        lane\t3.1
        num_waypoints\t3
        lane_width\t13
        3.1.1\t45.000000\t65.000000
        3.1.2\t44.999968\t65.000045
        3.1.3\t44.991017\t65.012704
        end_lane
        end_segment
        end_file""")

    def test_Y_intersection_many_to_one(self):
        """
                  (0,1)
                    +
            (-1,-1)   (1,-1)
        """
        city = generate_Y_intersection_many_to_one_city()

        self._generate_rndf(city)
        self._assert_contents_are("""
        RNDF_name\tYCross Many to One
        num_segments\t3
        num_zones\t0
        format_version\t1.0
        segment\t1
        num_lanes\t1
        segment_name\ts1
        lane\t1.1
        num_waypoints\t3
        lane_width\t13
        1.1.1\t45.000000\t65.000000
        1.1.2\t45.000045\t65.000000
        1.1.3\t45.008983\t65.000000
        end_lane
        end_segment
        segment\t2
        num_lanes\t1
        segment_name\ts2
        lane\t2.1
        num_waypoints\t3
        lane_width\t13
        exit\t2.1.2\t1.1.2
        2.1.1\t44.991017\t64.987296
        2.1.2\t44.999968\t64.999955
        2.1.3\t45.000000\t65.000000
        end_lane
        end_segment
        segment\t3
        num_lanes\t1
        segment_name\ts3
        lane\t3.1
        num_waypoints\t3
        lane_width\t13
        exit\t3.1.2\t1.1.2
        3.1.1\t44.991017\t65.012704
        3.1.2\t44.999968\t65.000045
        3.1.3\t45.000000\t65.000000
        end_lane
        end_segment
        end_file""")
