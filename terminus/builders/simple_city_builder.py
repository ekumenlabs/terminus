from shapely.geometry import Point

from models.city import City
from models.street import Street
from models.trunk import Trunk
from models.block import Block
from models.building import Building
from models.ground_plane import GroundPlane


class SimpleCityBuilder(object):

    def get_city(self):
        size = 3
        city = City()

        self._create_ground_plane(city, size)
        self._create_inner_streets(city, size)
        self._create_surrounding_ring_road(city, size)
        self._create_blocks(city, size)
        self._create_buildings(city, size)
        return city

    def _create_ground_plane(self, city, size):
        ground_plane_size = size*100
        ground_plane = GroundPlane(ground_plane_size,
                                   Point(ground_plane_size/2,
                                         ground_plane_size/2,
                                         0),
                                   'ground_plane')
        city.set_ground_plane(ground_plane)

    def _create_inner_streets(self, city, size):
        # West-East streets
        for x in range(1, size):
            road = Street()
            road.add_point(Point(0, x*100, 0))
            road.add_point(Point(100 * size, x*100, 0))
            city.add_road(road)

        # North-South streets
        for x in range(1, size):
            road = Street()
            road.add_point(Point(x*100, 0, 0))
            road.add_point(Point(x*100, 100 * size, 0))
            city.add_road(road)

        # Diagonal streets
        road = Street()
        road.add_point(Point(0, 0, 0))
        road.add_point(Point(100*size, 100*size, 0))
        city.add_road(road)
        road = Street()
        road.add_point(Point(100*size, 0, 0))
        road.add_point(Point(0, 100*size, 0))
        city.add_road(road)

    def _create_surrounding_ring_road(self, city, size):
        ring_road_1 = Street('RingRoad1')
        ring_road_1.add_point(Point(-2.5, 0, 0))
        ring_road_1.add_point(Point(size*100+2.5, 0, 0))
        city.add_road(ring_road_1)

        ring_road_2 = Street('RingRoad2')
        ring_road_2.add_point(Point(size*100, 0, 0))
        ring_road_2.add_point(Point(size*100, size*100, 0))
        city.add_road(ring_road_2)

        ring_road_3 = Street('RingRoad3')
        ring_road_3.add_point(Point(-2.5, size*100, 0))
        ring_road_3.add_point(Point(size*100+2.5, size*100, 0))
        city.add_road(ring_road_3)

        ring_road_4 = Street('RingRoad4')
        ring_road_4.add_point(Point(0, 0, 0))
        ring_road_4.add_point(Point(0, size*100, 0))
        city.add_road(ring_road_4)

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

        vertices = [Point(0, 0, 0), Point(88, 0, 0), Point(88/2, -44, 0)]
        block = Block(Point(100 + 6, 200 - 2.5, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(88, 0, 0), Point(88/2, 44, 0)]
        block = Block(Point(100 + 6, 100 + 2.5, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(0, 88, 0), Point(44, 88/2, 0)]
        block = Block(Point(100 + 2.5, 100 + 6, 0), vertices)
        city.add_block(block)

        vertices = [Point(0, 0, 0), Point(0, 88, 0), Point(-44, 88/2, 0)]
        block = Block(Point(200 - 2.5, 100 + 6, 0), vertices)
        city.add_block(block)

    def _create_buildings(self, city, size):
        for x in range(size):
            for y in range(size):
                for block_x in range(6):
                    for block_y in range(6):
                        pos = Point(x*100+block_x*15+12,
                                    y*100+block_y*15+12, 0)
                        if abs(pos.y + pos.x - 300.0) > 12.0 and\
                                abs(pos.y - pos.x) > 12.0:
                            building = Building(pos, 10, 40)
                            city.add_building(building)
