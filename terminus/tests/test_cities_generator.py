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

from geometry.point import Point
from models.city import City
from models.street import Street


class TestCitiesGenerator(object):

    def all_cities(self):
        cities = []
        for element in dir(self):
            attribute = getattr(self, element)
            if element != 'empty_city' and element.endswith('_city') and \
               hasattr(attribute, '__call__'):
                cities.append(attribute())
        return cities

    def empty_city(self):
        return City("Empty")

    def simple_street_city(self):
        city = City("Single street")
        street = Street.from_points([
            Point(0, 0),
            Point(100, 0),
            Point(200, 0)
        ])
        street.name = "s1"
        city.add_road(street)
        return city

    def cross_intersection_city(self):
        """
             (0,1)
        (-1,0) + (1,0)
             (0,-1)
        """
        city = City("Cross")

        s1 = Street.from_points([Point(-100, 0), Point(0, 0), Point(100, 0)])
        s1.name = "s1"

        s2 = Street.from_points([Point(0, 100), Point(0, 0), Point(0, -100)])
        s2.name = "s2"

        city.add_intersection_at(Point(0, 0))

        city.add_road(s1)
        city.add_road(s2)

        return city

    def L_intersection_city(self):
        """
             (0,1)
               +  (1,0)
        """
        city = City("LCross")

        s1 = Street.from_points([Point(0, 100), Point(0, 0)])
        s1.name = "s1"

        s2 = Street.from_points([Point(0, 0), Point(100, 0)])
        s2.name = "s2"

        city.add_intersection_at(Point(0, 0))

        city.add_road(s1)
        city.add_road(s2)

        return city

    def Y_intersection_one_to_many_city(self):
        """
                  (0,1)
                    +
            (-1,-1)   (1,-1)
        """
        city = City("YCross")

        s1 = Street.from_points([Point(0, 100), Point(0, 0)])
        s1.name = "s1"

        s2 = Street.from_points([Point(0, 0), Point(-100, -100)])
        s2.name = "s2"

        s3 = Street.from_points([Point(0, 0), Point(100, -100)])
        s3.name = "s3"

        city.add_intersection_at(Point(0, 0))

        city.add_road(s1)
        city.add_road(s2)
        city.add_road(s3)

        return city

    def Y_intersection_many_to_one_city(self):
        """
                  (0,1)
                    +
            (-1,-1)   (1,-1)
        """
        city = City("YCross Many to One")

        s1 = Street.from_points([Point(0, 0), Point(0, 100)])
        s1.name = "s1"

        s2 = Street.from_points([Point(-100, -100), Point(0, 0)])
        s2.name = "s2"

        s3 = Street.from_points([Point(100, -100), Point(0, 0)])
        s3.name = "s3"

        city.add_road(s1)
        city.add_road(s2)
        city.add_road(s3)

        city.add_intersection_at(Point(0, 0))

        return city
