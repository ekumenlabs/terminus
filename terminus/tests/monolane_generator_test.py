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

from generators.monolane_generator import MonolaneGenerator

from test_cities_generator import TestCitiesGenerator


class MonolaneGeneratorTest(unittest.TestCase):

    def setUp(self):
        # print full diff in test output
        self.maxDiff = None
        self.test_generator = TestCitiesGenerator()

    def _generate_yaml(self, city):
        self.generator = MonolaneGenerator(city)
        self.generated_contents = self.generator.generate()
        # print "###########################################"
        # print self.generated_contents
        # print "###########################################"

    def _assert_core_contents_are(self, name, expected_core_contents):
        expected_contents = """
        # -*- yaml -*-
        ---
        # distances are meters; angles are degrees.
        maliput_monolane_builder:
          id: {0}
          lane_bounds: [-2, 2]
          driveable_bounds: [-4, 4]
          position_precision: 0.01
          orientation_precision: 0.5{1}\n""".format(name, expected_core_contents)
        expected = textwrap.dedent(expected_contents)[1:]
        self.assertMultiLineEqual(self.generated_contents, expected)

    def test_empty_city(self):
        city = self.test_generator.empty_city()
        self._generate_yaml(city)
        self._assert_core_contents_are("Empty", """
          points: {}
          connections: {}
          groups: {}""")

    def test_simple_street(self):
        city = self.test_generator.simple_street_city()
        self._generate_yaml(city)
        self._assert_core_contents_are("Single street", """
          points:
            s1_1_1:
              xypoint: [0.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_2:
              xypoint: [200.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
          connections:
            s1_1_1-s1_1_2: {start: points.s1_1_1, length: 200.0, explicit_end: points.s1_1_2}
          groups: {}""")

    def test_cross_intersection(self):
        city = self.test_generator.cross_intersection_city()
        self._generate_yaml(city)
        self._assert_core_contents_are("Cross", """
          points:
            s1_1_1:
              xypoint: [-100.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_2:
              xypoint: [-7.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_3:
              xypoint: [7.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_4:
              xypoint: [100.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_1:
              xypoint: [0.0, 100.0, -90.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_2:
              xypoint: [0.0, 7.0, -90.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_3:
              xypoint: [0.0, -7.0, -90.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_4:
              xypoint: [0.0, -100.0, -90.0]
              zpoint: [0.0, 0, 0, 0]
          connections:
            s1_1_1-s1_1_2: {start: points.s1_1_1, length: 93.0, explicit_end: points.s1_1_2}
            s1_1_2-s2_1_3:
              start: points.s1_1_2
              arc: [7.0, -90.0]
              explicit_end: points.s2_1_3
            s1_1_2-s1_1_3: {start: points.s1_1_2, length: 14.0, explicit_end: points.s1_1_3}
            s1_1_3-s1_1_4: {start: points.s1_1_3, length: 93.0, explicit_end: points.s1_1_4}
            s2_1_1-s2_1_2: {start: points.s2_1_1, length: 93.0, explicit_end: points.s2_1_2}
            s2_1_2-s1_1_3:
              start: points.s2_1_2
              arc: [7.0, 90.0]
              explicit_end: points.s1_1_3
            s2_1_2-s2_1_3: {start: points.s2_1_2, length: 14.0, explicit_end: points.s2_1_3}
            s2_1_3-s2_1_4: {start: points.s2_1_3, length: 93.0, explicit_end: points.s2_1_4}
          groups: {}""")

    def test_L_intersection(self):
        city = self.test_generator.L_intersection_city()
        self._generate_yaml(city)
        self._assert_core_contents_are("L intersection", """
          points:
            s1_1_1:
              xypoint: [0.0, 100.0, -90.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_2:
              xypoint: [0.0, 7.0, -90.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_3:
              xypoint: [0.0, 0.0, -90.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_1:
              xypoint: [0.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_2:
              xypoint: [7.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_3:
              xypoint: [100.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
          connections:
            s1_1_1-s1_1_2: {start: points.s1_1_1, length: 93.0, explicit_end: points.s1_1_2}
            s1_1_2-s2_1_2:
              start: points.s1_1_2
              arc: [7.0, 90.0]
              explicit_end: points.s2_1_2
            s2_1_2-s2_1_3: {start: points.s2_1_2, length: 93.0, explicit_end: points.s2_1_3}
          groups: {}""")

    def test_Y_intersection_one_to_many(self):
        city = self.test_generator.Y_intersection_one_to_many_city()
        self._generate_yaml(city)
        self._assert_core_contents_are("Y intersection - One to many", """
          points:
            s1_1_1:
              xypoint: [0.0, 100.0, -90.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_2:
              xypoint: [0.0, 7.0, -90.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_3:
              xypoint: [0.0, 0.0, -90.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_1:
              xypoint: [0.0, 0.0, -135.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_2:
              xypoint: [-4.9497475, -4.9497475, -135.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_3:
              xypoint: [-100.0, -100.0, -135.0]
              zpoint: [0.0, 0, 0, 0]
            s3_1_1:
              xypoint: [0.0, 0.0, -45.0]
              zpoint: [0.0, 0, 0, 0]
            s3_1_2:
              xypoint: [4.9497475, -4.9497475, -45.0]
              zpoint: [0.0, 0, 0, 0]
            s3_1_3:
              xypoint: [100.0, -100.0, -45.0]
              zpoint: [0.0, 0, 0, 0]
          connections:
            s1_1_1-s1_1_2: {start: points.s1_1_1, length: 93.0, explicit_end: points.s1_1_2}
            s1_1_2-s2_1_2:
              start: points.s1_1_2
              arc: [16.8994949, -45.0]
              explicit_end: points.s2_1_2
            s1_1_2-s3_1_2:
              start: points.s1_1_2
              arc: [16.8994949, 45.0]
              explicit_end: points.s3_1_2
            s2_1_2-s2_1_3: {start: points.s2_1_2, length: 134.4213562373095, explicit_end: points.s2_1_3}
            s3_1_2-s3_1_3: {start: points.s3_1_2, length: 134.4213562373095, explicit_end: points.s3_1_3}
          groups: {}""")

    def test_Y_intersection_many_to_one(self):
        city = self.test_generator.Y_intersection_many_to_one_city()
        self._generate_yaml(city)
        self._assert_core_contents_are("Y intersection - Many to one", """
          points:
            s1_1_1:
              xypoint: [0.0, 0.0, 90.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_2:
              xypoint: [0.0, 7.0, 90.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_3:
              xypoint: [0.0, 100.0, 90.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_1:
              xypoint: [-100.0, -100.0, 45.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_2:
              xypoint: [-4.9497475, -4.9497475, 45.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_3:
              xypoint: [0.0, 0.0, 45.0]
              zpoint: [0.0, 0, 0, 0]
            s3_1_1:
              xypoint: [100.0, -100.0, 135.0]
              zpoint: [0.0, 0, 0, 0]
            s3_1_2:
              xypoint: [4.9497475, -4.9497475, 135.0]
              zpoint: [0.0, 0, 0, 0]
            s3_1_3:
              xypoint: [0.0, 0.0, 135.0]
              zpoint: [0.0, 0, 0, 0]
          connections:
            s1_1_2-s1_1_3: {start: points.s1_1_2, length: 93.0, explicit_end: points.s1_1_3}
            s2_1_1-s2_1_2: {start: points.s2_1_1, length: 134.4213562373095, explicit_end: points.s2_1_2}
            s2_1_2-s1_1_2:
              start: points.s2_1_2
              arc: [16.8994949, 45.0]
              explicit_end: points.s1_1_2
            s3_1_1-s3_1_2: {start: points.s3_1_1, length: 134.4213562373095, explicit_end: points.s3_1_2}
            s3_1_2-s1_1_2:
              start: points.s3_1_2
              arc: [16.8994949, -45.0]
              explicit_end: points.s1_1_2
          groups: {}""")

    def test_T_intersection_out_city(self):
        city = self.test_generator.T_intersection_out_city()
        self._generate_yaml(city)
        self._assert_core_contents_are("T intersection out", """
          points:
            s1_1_1:
              xypoint: [-100.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_2:
              xypoint: [-7.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_3:
              xypoint: [100.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_1:
              xypoint: [0.0, 0.0, -90.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_2:
              xypoint: [0.0, -7.0, -90.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_3:
              xypoint: [0.0, -100.0, -90.0]
              zpoint: [0.0, 0, 0, 0]
          connections:
            s1_1_1-s1_1_2: {start: points.s1_1_1, length: 93.0, explicit_end: points.s1_1_2}
            s1_1_2-s2_1_2:
              start: points.s1_1_2
              arc: [7.0, -90.0]
              explicit_end: points.s2_1_2
            s1_1_2-s1_1_3: {start: points.s1_1_2, length: 107.0, explicit_end: points.s1_1_3}
            s2_1_2-s2_1_3: {start: points.s2_1_2, length: 93.0, explicit_end: points.s2_1_3}
          groups: {}""")

    def test_T_intersection_in_city(self):
        city = self.test_generator.T_intersection_in_city()
        self._generate_yaml(city)
        self._assert_core_contents_are("T intersection in", """
          points:
            s1_1_1:
              xypoint: [-100.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_2:
              xypoint: [7.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_3:
              xypoint: [100.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_1:
              xypoint: [0.0, -100.0, 90.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_2:
              xypoint: [0.0, -7.0, 90.0]
              zpoint: [0.0, 0, 0, 0]
            s2_1_3:
              xypoint: [0.0, 0.0, 90.0]
              zpoint: [0.0, 0, 0, 0]
          connections:
            s1_1_1-s1_1_2: {start: points.s1_1_1, length: 107.0, explicit_end: points.s1_1_2}
            s1_1_2-s1_1_3: {start: points.s1_1_2, length: 93.0, explicit_end: points.s1_1_3}
            s2_1_1-s2_1_2: {start: points.s2_1_1, length: 93.0, explicit_end: points.s2_1_2}
            s2_1_2-s1_1_2:
              start: points.s2_1_2
              arc: [7.0, -90.0]
              explicit_end: points.s1_1_2
          groups: {}""")

    def test_two_non_collinear_segments_city(self):
        city = self.test_generator.non_collinear_segments_city()
        self._generate_yaml(city)
        self._assert_core_contents_are("Non collinear segments - Standard", """
          points:
            s1_1_1:
              xypoint: [-100.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_2:
              xypoint: [-5.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_3:
              xypoint: [4.7891314, 1.4367394, 16.699244233993625]
              zpoint: [0.0, 0, 0, 0]
            s1_1_4:
              xypoint: [100.0, 30.0, 16.699244233993625]
              zpoint: [0.0, 0, 0, 0]
          connections:
            s1_1_1-s1_1_2: {start: points.s1_1_1, length: 95.0, explicit_end: points.s1_1_2}
            s1_1_2-s1_1_3:
              start: points.s1_1_2
              arc: [34.0671775, 16.6992442]
              explicit_end: points.s1_1_3
            s1_1_3-s1_1_4: {start: points.s1_1_3, length: 99.4030650891055, explicit_end: points.s1_1_4}
          groups: {}""")

    def test_two_non_collinear_segments_border_city(self):
        city = self.test_generator.two_non_collinear_segments_border_city()
        self._generate_yaml(city)
        self._assert_core_contents_are("Non collinear segments - Border", """
          points:
            s1_1_1:
              xypoint: [-10.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_2:
              xypoint: [-5.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_3:
              xypoint: [4.9029034, 0.9805807, 11.309932474019142]
              zpoint: [0.0, 0, 0, 0]
            s1_1_4:
              xypoint: [5.0970966, 1.0194193, 11.309932474019142]
              zpoint: [0.0, 0, 0, 0]
            s1_1_5:
              xypoint: [14.472136, 4.236068, 26.565051177079678]
              zpoint: [0.0, 0, 0, 0]
            s1_1_6:
              xypoint: [20.0, 7.0, 26.565051177079678]
              zpoint: [0.0, 0, 0, 0]
          connections:
            s1_1_1-s1_1_2: {start: points.s1_1_1, length: 5.0, explicit_end: points.s1_1_2}
            s1_1_2-s1_1_3:
              start: points.s1_1_2
              arc: [50.4950976, 11.3099325]
              explicit_end: points.s1_1_3
            s1_1_3-s1_1_4: {start: points.s1_1_3, length: 0.19803902718558075, explicit_end: points.s1_1_4}
            s1_1_4-s1_1_5:
              start: points.s1_1_4
              arc: [37.3362571, 15.2551187]
              explicit_end: points.s1_1_5
            s1_1_5-s1_1_6: {start: points.s1_1_5, length: 6.180339887498981, explicit_end: points.s1_1_6}
          groups: {}""")

    def test_two_non_collinear_segments_less_than_border_city(self):
        city = self.test_generator.two_non_collinear_segments_less_than_border_city()
        self._generate_yaml(city)
        self._assert_core_contents_are("Non collinear segments - Less than border", """
          points:
            s1_1_1:
              xypoint: [-10.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_2:
              xypoint: [-2.236068, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_3:
              xypoint: [2.0, 1.0, 26.56505117707799]
              zpoint: [0.0, 0, 0, 0]
            s1_1_4:
              xypoint: [6.1342821, 2.6669632, 17.35402463626132]
              zpoint: [0.0, 0, 0, 0]
            s1_1_5:
              xypoint: [20.0, 7.0, 17.35402463626132]
              zpoint: [0.0, 0, 0, 0]
          connections:
            s1_1_1-s1_1_2: {start: points.s1_1_1, length: 7.76393202250021, explicit_end: points.s1_1_2}
            s1_1_2-s1_1_3:
              start: points.s1_1_2
              arc: [9.472136, 26.5650512]
              explicit_end: points.s1_1_3
            s1_1_3-s1_1_4:
              start: points.s1_1_3
              arc: [27.758298, -9.2110265]
              explicit_end: points.s1_1_4
            s1_1_4-s1_1_5: {start: points.s1_1_4, length: 14.526986636740412, explicit_end: points.s1_1_5}
          groups: {}""")

    def test_S_road_city(self):
        city = self.test_generator.S_road_city()
        self._generate_yaml(city)
        self._assert_core_contents_are("S road", """
          points:
            s1_1_1:
              xypoint: [0.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_2:
              xypoint: [45.0, 0.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_3:
              xypoint: [50.0, 5.0, 90.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_4:
              xypoint: [50.0, 10.0, 90.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_5:
              xypoint: [55.0, 15.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
            s1_1_6:
              xypoint: [100.0, 15.0, 0.0]
              zpoint: [0.0, 0, 0, 0]
          connections:
            s1_1_1-s1_1_2: {start: points.s1_1_1, length: 45.0, explicit_end: points.s1_1_2}
            s1_1_2-s1_1_3:
              start: points.s1_1_2
              arc: [5.0, 90.0]
              explicit_end: points.s1_1_3
            s1_1_3-s1_1_4: {start: points.s1_1_3, length: 5.000000000000001, explicit_end: points.s1_1_4}
            s1_1_4-s1_1_5:
              start: points.s1_1_4
              arc: [5.0, -90.0]
              explicit_end: points.s1_1_5
            s1_1_5-s1_1_6: {start: points.s1_1_5, length: 45.0, explicit_end: points.s1_1_6}
          groups: {}""")
