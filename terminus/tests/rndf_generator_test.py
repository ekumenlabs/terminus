import unittest

from geometry.point import Point
from models.city import City
from models.street import Street
from models.trunk import Trunk

from generators.rndf_generator import RNDFGenerator

import textwrap

class RNDFGeneratorTest(unittest.TestCase):

    def _generate_rndf(self, city):
        self.generator = RNDFGenerator(city, Point(45, 65))
        self.generated_contents = self.generator.generate()

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
        street = Street.from_points([
            Point(0, 0),
            Point(1000, 0),
            Point(2000, 0)
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
        1.1.1\t65.0\t45.0
        1.1.2\t65.0\t45.0171
        1.1.3\t65.0\t45.0342
        end_lane
        end_segment
        end_file""")
