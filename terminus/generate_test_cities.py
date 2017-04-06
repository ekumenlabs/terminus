#!/usr/bin/python

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

test_cities = TestCitiesGenerator().non_empty_cities()

for city in test_cities:
    builder = SampleBuilder(city)
    path = 'terminus/tests/samples/'
    name = slugify(city.name, separator="_")
    process = CityGenerationProcess(builder, RNDF_ORIGIN, path, True, name)
    process.run()
