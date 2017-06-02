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
from models.trunk import Trunk


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

    def broken_intersection_on_one_lane_city(self):
        """
                      (0,50)
                        |
                        |    __--- (50,20)
        (-50,0) ------- + ---
                        |
                        |
                      (0,-50)
        """
        city = City("Broken intersection - One lane")

        s1 = Street.from_control_points([Point(-50, 0), Point(0, 0), Point(50, 20)])
        s1.name = "s1"

        s2 = Street.from_control_points([Point(0, -50), Point(0, 0), Point(0, 50)])
        s2.name = "s2"

        city.add_intersection_at(Point(0, 0))

        city.add_road(s1)
        city.add_road(s2)

        return city

    def broken_intersection_on_two_lanes_city(self):
        """
                      (10,50)
                         |
                        |    __--- (50,20)
        (-50,0) ------- + ---
                        |
                        |
                      (0,-50)
        """
        city = City("Broken intersection - Two lanes")

        s1 = Street.from_control_points([Point(-50, 0), Point(0, 0), Point(50, 20)])
        s1.name = "s1"

        s2 = Street.from_control_points([Point(0, -50), Point(0, 0), Point(10, 50)])
        s2.name = "s2"

        city.add_intersection_at(Point(0, 0))

        city.add_road(s1)
        city.add_road(s2)

        return city

    def road_ends_in_intersection_city(self):
        """
        When using smooth geometries, the original intersection point (0,0) does
        not exist anymore as a place for the roads to intersect (it should be
        replaced by an arc or similar). Since s2 dies on (0,0) the road geometry
        has to be extended to touch the new s1 geometry.

                             __--- (50,30)
        (-50,0) ------- + ---
                        |
                        |
                      (0,-50)
        """
        city = City("Road ends in intersection")

        s1 = Street.from_control_points([Point(-50, 0), Point(0, 0), Point(50, 30)])
        s1.name = "s1"

        s2 = Street.from_control_points([Point(0, -50), Point(0, 0)])
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

    def collinear_streets_city(self):
        """
         --->---+--->---
        """
        city = City("Collinear streets")

        s1 = Street.from_control_points([
            Point(0, 0),
            Point(50, 0)
        ])

        s2 = Street.from_control_points([
            Point(50, 0),
            Point(100, 0)
        ])

        city.add_road(s1)
        city.add_road(s2)

        city.add_intersection_at(Point(50, 0))

        return city


    def trunk_to_street_city(self):
        """
         ---<---
               +-->---
         --->--+
        """
        city = City("Trunk to street")

        trunk = Trunk.from_control_points([
            Point(0, 0),
            Point(50, 0)
        ])

        street = Street.from_control_points([
            Point(50, 0),
            Point(100, 0)
        ])

        city.add_road(trunk)
        city.add_road(street)

        city.add_intersection_at(Point(50, 0))

        return city

    def trunk_from_street_city(self):
        """
         ---<---
               +---<---
         --->--+
        """
        city = City("Trunk from street")

        trunk = Trunk.from_control_points([
            Point(0, 0),
            Point(50, 0)
        ])

        street = Street.from_control_points([
            Point(100, 0),
            Point(50, 0)
        ])

        city.add_road(trunk)
        city.add_road(street)

        city.add_intersection_at(Point(50, 0))

        return city
