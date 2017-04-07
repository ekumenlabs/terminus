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

    def non_empty_cities(self):
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
        street = Street.from_control_points([
            Point(0, 0),
            Point(100, 0),
            Point(200, 0)
        ])
        street.name = "s1"
        city.add_road(street)
        return city

    def cross_intersection_city(self):
        """
                  (0,100)
                    |
        (-100,0) -- + -- (100,0)
                    |
                  (0,-100)
        """
        city = City("Cross")

        s1 = Street.from_control_points([Point(-100, 0), Point(0, 0), Point(100, 0)])
        s1.name = "s1"

        s2 = Street.from_control_points([Point(0, 100), Point(0, 0), Point(0, -100)])
        s2.name = "s2"

        city.add_intersection_at(Point(0, 0))

        city.add_road(s1)
        city.add_road(s2)

        return city

    def L_intersection_city(self):
        """
            (0,100)
               |
               + -- (100,0)
        """
        city = City("L intersection")

        s1 = Street.from_control_points([Point(0, 100), Point(0, 0)])
        s1.name = "s1"

        s2 = Street.from_control_points([Point(0, 0), Point(100, 0)])
        s2.name = "s2"

        city.add_intersection_at(Point(0, 0))

        city.add_road(s1)
        city.add_road(s2)

        return city

    def Y_intersection_one_to_many_city(self):
        """
                  (0,100)
                    |
                    |
                    +
                   / \
                  /   \
         (-100,-100) (100,-100)
        """
        city = City("Y intersection - One to many")

        s1 = Street.from_control_points([Point(0, 100), Point(0, 0)])
        s1.name = "s1"

        s2 = Street.from_control_points([Point(0, 0), Point(-100, -100)])
        s2.name = "s2"

        s3 = Street.from_control_points([Point(0, 0), Point(100, -100)])
        s3.name = "s3"

        city.add_intersection_at(Point(0, 0))

        city.add_road(s1)
        city.add_road(s2)
        city.add_road(s3)

        return city

    def Y_intersection_many_to_one_city(self):
        """
                  (0,100)
                    |
                    |
                    +
                   / \
                  /   \
         (-100,-100) (100,-100)
        """
        city = City("Y intersection - Many to one")

        s1 = Street.from_control_points([Point(0, 0), Point(0, 100)])
        s1.name = "s1"

        s2 = Street.from_control_points([Point(-100, -100), Point(0, 0)])
        s2.name = "s2"

        s3 = Street.from_control_points([Point(100, -100), Point(0, 0)])
        s3.name = "s3"

        city.add_road(s1)
        city.add_road(s2)
        city.add_road(s3)

        city.add_intersection_at(Point(0, 0))

        return city

    def T_intersection_out_city(self):
        """
        (-100,0) -- + -- (100,0)
                    |
                  (0,-100)
        """
        city = City("T intersection out")

        s1 = Street.from_control_points([Point(-100, 0), Point(0, 0), Point(100, 0)])
        s1.name = "s1"

        s2 = Street.from_control_points([Point(0, 0), Point(0, -100)])
        s2.name = "s2"

        city.add_intersection_at(Point(0, 0))

        city.add_road(s1)
        city.add_road(s2)

        return city

    def T_intersection_in_city(self):
        """
        (-100,0) -- + -- (100,0)
                    |
                  (0,-100)
        """
        city = City("T intersection in")

        s1 = Street.from_control_points([Point(-100, 0), Point(0, 0), Point(100, 0)])
        s1.name = "s1"

        s2 = Street.from_control_points([Point(0, -100), Point(0, 0)])
        s2.name = "s2"

        city.add_intersection_at(Point(0, 0))

        city.add_road(s1)
        city.add_road(s2)

        return city

    def non_collinear_segments_city(self):
        """
        (-100,0) -- (0,0) -- (100,30)
        """
        city = City("Non collinear segments - Standard")

        s1 = Street.from_control_points([Point(-100, 0), Point(0, 0), Point(100, 30)])
        s1.name = "s1"

        city.add_road(s1)

        return city

    def two_non_collinear_segments_border_city(self):
        """
        (-10,0) -- (0,0) -- (10,2) -- (20,4)
        """
        city = City("Non collinear segments - Border")

        s1 = Street.from_control_points([Point(-10, 0), Point(0, 0), Point(10, 2), Point(20, 7)])
        s1.name = "s1"

        city.add_road(s1)

        return city

    def two_non_collinear_segments_less_than_border_city(self):
        """
        (-10,0) -- (0,0) -- (10,2) -- (20,4)
        """
        city = City("Non collinear segments - Less than border")

        s1 = Street.from_control_points([Point(-10, 0), Point(0, 0), Point(4, 2), Point(20, 7)])
        s1.name = "s1"

        city.add_road(s1)

        return city

    def S_road_city(self):
        """
              (50,12) *------- (100, 12)
                      |
                      |
            (0, 0) ---* (50,0)
        """
        city = City("S road")

        s1 = Street.from_control_points([
            Point(0, 0),
            Point(50, 0),
            Point(50, 15),
            Point(100, 15)
        ])
        s1.name = "s1"

        city.add_road(s1)

        return city
