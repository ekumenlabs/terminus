"""
/*
 * Copyright (C) 2017 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
"""
import unittest

import yaml

from generators.monolane_generator import MonolaneGenerator

from test_cities_generator import TestCitiesGenerator


class MonolaneGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.test_generator = TestCitiesGenerator()

    def generate_monolane(self, city):
        self.generator = MonolaneGenerator(city)
        self.generated_contents = self.generator.generate()
        self.yaml_dict = yaml.load(self.generated_contents)
        monolane_dict = self.yaml_dict['maliput_monolane_builder']
        self.standard_checks(city, monolane_dict)
        return monolane_dict

    def standard_checks(self, city, monolane_dict):
        self.assertEqual(city.name, monolane_dict['id'])
        # Ensure each road is somewhat represented in the point names.
        all_point_names = list(monolane_dict['points'].keys())
        for road in city.roads:
            self.assertTrue(
                any([x for x in all_point_names if road.name in x]),
                msg="The name for road '{}' does not appear in any point names.".format(road.name))
        # For now groups are always empty.
        self.assertEqual(0, len(monolane_dict['groups']))

    def test_empty_city(self):
        city = self.test_generator.empty_city()

        monolane_dict = self.generate_monolane(city)

        self.assertEqual(0, len(monolane_dict['points']))
        self.assertEqual(0, len(monolane_dict['connections']))

    def test_simple_street(self):
        city = self.test_generator.simple_street_city()

        monolane_dict = self.generate_monolane(city)

        self.assertEqual(3, len(monolane_dict['points']))
        self.assertEqual(2, len(monolane_dict['connections']))

    def test_cross_intersection(self):
        city = self.test_generator.cross_intersection_city()

        monolane_dict = self.generate_monolane(city)

        self.assertEqual(6, len(monolane_dict['points']))
        self.assertEqual(4, len(monolane_dict['connections']))
        # Make sure two of the points are part of the intersection.
        self.assertEqual(2, len([x for x in monolane_dict['points'] if 'Intersection' in x]))
        # Make sure there is only one intersection, i.e. no Intersection-2, only Intersection-1.
        self.assertFalse(any([x for x in monolane_dict['points'] if 'Intersection-2' in x]))

    def test_L_intersection(self):
        city = self.test_generator.L_intersection_city()

        monolane_dict = self.generate_monolane(city)

        self.assertEqual(4, len(monolane_dict['points']))
        self.assertEqual(2, len(monolane_dict['connections']))
        # Make sure two of the points are part of the intersection.
        self.assertEqual(2, len([x for x in monolane_dict['points'] if 'Intersection' in x]))
        # Make sure there is only one intersection, i.e. no Intersection-2, only Intersection-1.
        self.assertFalse(any([x for x in monolane_dict['points'] if 'Intersection-2' in x]))

    def test_Y_intersection_one_to_many(self):
        city = self.test_generator.Y_intersection_one_to_many_city()

        monolane_dict = self.generate_monolane(city)

        self.assertEqual(6, len(monolane_dict['points']))
        self.assertEqual(3, len(monolane_dict['connections']))
        # Make sure two of the points are part of the intersection.
        self.assertEqual(3, len([x for x in monolane_dict['points'] if 'Intersection' in x]))
        # Make sure there is only one intersection, i.e. no Intersection-2, only Intersection-1.
        self.assertFalse(any([x for x in monolane_dict['points'] if 'Intersection-2' in x]))

    def test_Y_intersection_many_to_one(self):
        city = self.test_generator.Y_intersection_many_to_one_city()

        monolane_dict = self.generate_monolane(city)

        self.assertEqual(6, len(monolane_dict['points']))
        self.assertEqual(3, len(monolane_dict['connections']))
        # Make sure two of the points are part of the intersection.
        self.assertEqual(3, len([x for x in monolane_dict['points'] if 'Intersection' in x]))
        # Make sure there is only one intersection, i.e. no Intersection-2, only Intersection-1.
        self.assertFalse(any([x for x in monolane_dict['points'] if 'Intersection-2' in x]))
