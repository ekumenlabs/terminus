from geometry.point import Point

from models.city import City
from models.street import Street
from models.trunk import Trunk
from models.block import Block
from models.building import Building
from models.ground_plane import GroundPlane
from models.road import *


class SimpleCityBuilder(object):

    def get_city(self):
        # Must be even
        size = 5
        city = City()
        self.multiplier = 100

        self._create_ground_plane(city, size)
        self._setup_junctions(size)
        self._create_inner_streets(city, size)
        self._create_surrounding_ring_road(city, size)
        self._create_blocks(city, size)
        self._create_buildings(city, size)
        return city

    def _setup_junctions(self, size):
        self.junctions = [[IntersectionNode.on(self.multiplier * x, self.multiplier * y, 0)
                           for y in range(size)] for x in range(size)]

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
                road.add_node(self.junctions[x][y])
            city.add_road(road)

        # Horizontal
        for y in range(1, size - 1):
            road = Street()
            for x in range(size):
                road.add_node(self.junctions[x][y])
            city.add_road(road)

        # Diagonals
        road = Street()
        for i in range(size):
            road.add_node(self.junctions[i][i])
        city.add_road(road)

        road = Street()
        for i in range(size):
            road.add_node(self.junctions[i][size - i - 1])
        city.add_road(road)

    def _create_surrounding_ring_road(self, city, size):
        ring_road_1 = Street(name='RingRoad1')
        for x in range(size):
            ring_road_1.add_node(self.junctions[x][0])
        city.add_road(ring_road_1)

        ring_road_2 = Street(name='RingRoad2')
        for y in range(size):
            ring_road_2.add_node(self.junctions[size - 1][y])
        city.add_road(ring_road_2)

        ring_road_3 = Street(name='RingRoad3')
        for x in range(size):
            ring_road_3.add_node(self.junctions[size - x - 1][size - 1])
        city.add_road(ring_road_3)

        ring_road_4 = Street(name='RingRoad4')
        for y in range(size):
            ring_road_4.add_node(self.junctions[0][size - y - 1])
        city.add_road(ring_road_4)

    # FIX: Make this dependent of the size
    def _create_blocks(self, city, size):
        block = Block.square(Point(150, 50, 0), 95)
        city.add_block(block)

        block = Block.square(Point(150, 250, 0), 95)
        city.add_block(block)

        block = Block.square(Point(50, 150, 0), 95)
        city.add_block(block)

        block = Block.square(Point(250, 150, 0), 95)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(91.5, 0, 0), Point(91.5, 91.5, 0)]
        block = Block(Point(6, 2.5, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(91.5, 0, 0), Point(0, -91.5, 0)]
        block = Block(Point(2.5, 97.5, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(91.5, 0, 0), Point(91.5, 91.5, 0)]
        block = Block(Point(200 + 6, 200 + 2.5, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(91.5, 0, 0), Point(0, -91.5, 0)]
        block = Block(Point(200 + 2.5, 200 + 97.5, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(91.5, 0, 0), Point(91.5, -91.5, 0)]
        block = Block(Point(200 + 6, 95 + 2.5, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(91.5, 0, 0), Point(0, 91.5, 0)]
        block = Block(Point(200 + 2.5, 2.5, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(91.5, 0, 0), Point(91.5, -91.5, 0)]
        block = Block(Point(6, 200 + 95 + 2.5, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(91.5, 0, 0), Point(0, 91.5, 0)]
        block = Block(Point(2.5, 200 + 2.5, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(88, 0, 0), Point(88 / 2, -44, 0)]
        block = Block(Point(self.multiplier + 6, 200 - 2.5, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(88, 0, 0), Point(88 / 2, 44, 0)]
        block = Block(Point(self.multiplier + 6, self.multiplier + 2.5, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(0, 88, 0), Point(44, 88 / 2, 0)]
        block = Block(Point(self.multiplier + 2.5, self.multiplier + 6, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(0, 88, 0), Point(-44, 88 / 2, 0)]
        block = Block(Point(200 - 2.5, self.multiplier + 6, 0), vertices)
        city.add_block(block)

    def _create_buildings(self, city, size):
        for x in range(size):
            for y in range(size):
                for block_x in range(6):
                    for block_y in range(6):
                        pos = Point(x * self.multiplier + block_x * 15 + 12,
                                    y * 100 + block_y * 15 + 12, 0)
                        if abs(pos.y + pos.x - 300.0) > 12.0 and\
                                abs(pos.y - pos.x) > 12.0:
                            building = Building(pos, 10, 40)
                            city.add_building(building)
