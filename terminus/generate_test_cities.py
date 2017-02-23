#!/usr/bin/python
import os

from geometry.latlon import LatLon

from tests.test_cities_generator import TestCitiesGenerator
from city_generation_process import CityGenerationProcess

from slugify import slugify

# For the time being we use an arbitrary (lat, lon) as the origin
RNDF_ORIGIN = LatLon(10, 65)


# Just a mock to satisfy the generation process interface
class SampleBuilder(object):
    def __init__(self, city):
        self.city = city

    def get_city(self):
        return self.city

    def name(self):
        return "SampleBuilder for {0}".format(self.city.name)

test_cities = TestCitiesGenerator().all_cities()

for city in test_cities:
    builder = SampleBuilder(city)
    path = 'generated_worlds/tests/'
    name = slugify(city.name, separator="_")
    process = CityGenerationProcess(builder, RNDF_ORIGIN, path, True, name)
    process.run()
