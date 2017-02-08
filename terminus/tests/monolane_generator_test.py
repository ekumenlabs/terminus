import unittest

import yaml

from generators.monolane_generator import MonolaneGenerator

from common_generator_test_cases import generate_cross_intersection_city
from common_generator_test_cases import generate_empty_city
from common_generator_test_cases import generate_L_intersection_city
from common_generator_test_cases import generate_simple_street_city
from common_generator_test_cases import generate_Y_intersection_one_to_many_city
from common_generator_test_cases import generate_Y_intersection_many_to_one_city


class MonolaneGeneratorTest(unittest.TestCase):

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
        city = generate_empty_city()

        monolane_dict = self.generate_monolane(city)

        self.assertEqual(0, len(monolane_dict['points']))
        self.assertEqual(0, len(monolane_dict['connections']))

    def test_simple_street(self):
        city = generate_simple_street_city()

        monolane_dict = self.generate_monolane(city)

        self.assertEqual(3, len(monolane_dict['points']))
        self.assertEqual(2, len(monolane_dict['connections']))

    def test_cross_intersection(self):
        city = generate_cross_intersection_city()

        monolane_dict = self.generate_monolane(city)

        self.assertEqual(6, len(monolane_dict['points']))
        self.assertEqual(4, len(monolane_dict['connections']))
        # Make sure two of the points are part of the intersection.
        self.assertEqual(2, len([x for x in monolane_dict['points'] if 'Intersection' in x]))
        # Make sure there is only one intersection, i.e. no Intersection-2, only Intersection-1.
        self.assertFalse(any([x for x in monolane_dict['points'] if 'Intersection-2' in x]))

    def test_L_intersection(self):
        city = generate_L_intersection_city()

        monolane_dict = self.generate_monolane(city)

        self.assertEqual(4, len(monolane_dict['points']))
        self.assertEqual(2, len(monolane_dict['connections']))
        # Make sure two of the points are part of the intersection.
        self.assertEqual(2, len([x for x in monolane_dict['points'] if 'Intersection' in x]))
        # Make sure there is only one intersection, i.e. no Intersection-2, only Intersection-1.
        self.assertFalse(any([x for x in monolane_dict['points'] if 'Intersection-2' in x]))

    def test_Y_intersection_one_to_many(self):
        city = generate_Y_intersection_one_to_many_city()

        monolane_dict = self.generate_monolane(city)

        self.assertEqual(6, len(monolane_dict['points']))
        self.assertEqual(3, len(monolane_dict['connections']))
        # Make sure two of the points are part of the intersection.
        self.assertEqual(3, len([x for x in monolane_dict['points'] if 'Intersection' in x]))
        # Make sure there is only one intersection, i.e. no Intersection-2, only Intersection-1.
        self.assertFalse(any([x for x in monolane_dict['points'] if 'Intersection-2' in x]))

    def test_Y_intersection_many_to_one(self):
        city = generate_Y_intersection_many_to_one_city()

        monolane_dict = self.generate_monolane(city)

        self.assertEqual(6, len(monolane_dict['points']))
        self.assertEqual(3, len(monolane_dict['connections']))
        # Make sure two of the points are part of the intersection.
        self.assertEqual(3, len([x for x in monolane_dict['points'] if 'Intersection' in x]))
        # Make sure there is only one intersection, i.e. no Intersection-2, only Intersection-1.
        self.assertFalse(any([x for x in monolane_dict['points'] if 'Intersection-2' in x]))
