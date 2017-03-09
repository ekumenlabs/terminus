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
from models.block import Block
from models.building import Building
from models.ground_plane import GroundPlane
from models.road import *

from builders.abstract_city_builder import AbstractCityBuilder


class SimpleCityBuilder(AbstractCityBuilder):

    def get_city(self):
        # Must be odd
        size = 5
        city = City()
        self.multiplier = 100

        self._create_ground_plane(city, size)
        self._setup_intersections(city, size)
        self._create_inner_streets(city, size)
        self._create_surrounding_ring_road(city, size)
        self._create_blocks(city, size)
        self._create_buildings(city, size)
        return city

    def _setup_intersections(self, city, size):
        self.intersections = [[Point(self.multiplier * x, self.multiplier * y, 0)
                              for y in range(size)] for x in range(size)]

        for x in range(size - 1):
            self.intersections[x][0] = self.intersections[x][0] + Point(0, -2)
        self.intersections[size - 1][0] = self.intersections[size - 1][0] + Point(2, -2)

        for y in range(1, size):
            self.intersections[size - 1][y] = self.intersections[size - 1][y] + Point(2, 0)

        for x in range(size - 1):
            self.intersections[size - x - 1][size - 1] = self.intersections[size - x - 1][size - 1] + Point(0, 2)
        self.intersections[0][size - 1] = self.intersections[0][size - 1] + Point(-2, 2)

        for y in range(1, size):
            self.intersections[0][size - y - 1] = self.intersections[0][size - y - 1] + Point(-2, 0)

        for x in range(size):
            for y in range(size):
                city.add_intersection_at(self.intersections[x][y])

    def _create_ground_plane(self, city, size):
        ground_plane_size = size * self.multiplier
        ground_plane = GroundPlane(ground_plane_size,
                                   Point(ground_plane_size / 2,
                                         ground_plane_size / 2,
                                         0),
                                   'ground_plane')
        city.set_ground_plane(ground_plane)

    def _create_inner_streets(self, city, size):

        # Vertical
        for x in range(1, size - 1):
            road = Street()
            for y in range(size):
                road.add_point(self.intersections[x][y])
            city.add_road(road)

        # Horizontal
        for y in range(1, size - 1):
            road = Street()
            for x in range(size):
                road.add_point(self.intersections[x][y])
            city.add_road(road)

        # Diagonals
        road = Street()
        for i in range(size):
            road.add_point(self.intersections[i][i])
        city.add_road(road)

        road = Street()
        for i in range(size):
            road.add_point(self.intersections[i][size - i - 1])
        city.add_road(road)

    def _create_surrounding_ring_road(self, city, size):
        ring_road_1 = Street(name='RingRoad1')
        for x in range(size):
            ring_road_1.add_point(self.intersections[x][0])
        city.add_road(ring_road_1)

        ring_road_2 = Street(name='RingRoad2')
        for y in range(size):
            ring_road_2.add_point(self.intersections[size - 1][y])
        city.add_road(ring_road_2)

        ring_road_3 = Street(name='RingRoad3')
        for x in range(size):
            ring_road_3.add_point(self.intersections[size - x - 1][size - 1])
        city.add_road(ring_road_3)

        ring_road_4 = Street(name='RingRoad4')
        for y in range(size):
            ring_road_4.add_point(self.intersections[0][size - y - 1])
        city.add_road(ring_road_4)

    def _create_blocks(self, city, size):
        blocks_count = size - 1
        block_size = 96
        inital_offset = 50
        street_width = 4
        half_street_width = street_width / 2.0
        triangle_delta = 93

        for x in range(blocks_count):
            for y in range(blocks_count):
                if x == y:
                    origin = Point(street_width + 1 + x * self.multiplier,
                                   half_street_width + y * self.multiplier, 0)
                    vertices = [Point(0, 0, 0), Point(triangle_delta, 0, 0), Point(triangle_delta, triangle_delta, 0)]
                    block = Block(origin, vertices)
                    city.add_block(block)

                    origin = Point(half_street_width + x * self.multiplier,
                                   street_width + 1 + y * self.multiplier, 0)
                    vertices = [Point(0, 0, 0), Point(0, triangle_delta, 0), Point(triangle_delta, triangle_delta, 0)]
                    block = Block(origin, vertices)
                    city.add_block(block)
                elif x + y == blocks_count - 1:
                    origin = Point(half_street_width + x * self.multiplier,
                                   half_street_width + y * self.multiplier, 0)
                    vertices = [Point(0, 0, 0), Point(triangle_delta, 0, 0), Point(0, triangle_delta, 0)]
                    block = Block(origin, vertices)
                    city.add_block(block)

                    origin = Point((x + 1) * self.multiplier - half_street_width,
                                   street_width + 1 + y * self.multiplier, 0)
                    vertices = [Point(0, 0, 0), Point(0, triangle_delta, 0), Point(-triangle_delta, triangle_delta, 0)]
                    block = Block(origin, vertices)
                    city.add_block(block)
                else:
                    origin = Point(inital_offset + x * self.multiplier,
                                   inital_offset + y * self.multiplier, 0)
                    block = Block.square(origin, block_size)
                    city.add_block(block)

    def _create_buildings(self, city, size):
        blocks_count = size - 1
        building_spacing = 18
        for x in range(blocks_count):
            for y in range(blocks_count):
                for block_x in range(3):
                    for block_y in range(3):
                        pos = Point(x * self.multiplier + block_x * 30 + building_spacing,
                                    y * self.multiplier + block_y * 30 + building_spacing, 0)
                        if abs(pos.y - pos.x) > building_spacing and \
                           abs(pos.y + pos.x - self.multiplier * blocks_count) > building_spacing:
                            building = Building.square(pos, 20, 40)
                            city.add_building(building)
