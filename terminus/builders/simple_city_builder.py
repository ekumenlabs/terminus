from shapely.geometry import Point

from models.city import City
from models.road import Street, Trunk
from models.block import Block
from models.building import Building
from models.ground_plane import GroundPlane


class SimpleCityBuilder(object):

    def get_city(self):
        size = 3
        city = City()

        self._create_ground_plane(city, size)
        self._create_street_matrix(city, size)
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

    def _create_street_matrix(self, city, size):
        for x in range(1, size):
            road = Street()
            road.add_point(Point(0, x*100, 0))
            road.add_point(Point(100 * size, x*100, 0))
            city.add_road(road)

        for x in range(1, size):
            road = Street()
            road.add_point(Point(x*100, 0, 0))
            road.add_point(Point(x*100, 100 * size, 0))
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
        for x in range(size):
            for y in range(size):
                block = Block.square(Point(x*100+50, y*100+50, 0), 95)
                city.add_block(block)

    def _create_buildings(self, city, size):
        for x in range(size):
            for y in range(size):
                for block_x in range(6):
                    for block_y in range(6):
                        building = Building(Point(x*100+block_x*15+12,
                                                  y*100+block_y*15+12,
                                                  0),
                                            10, 40)
                        city.add_building(building)
