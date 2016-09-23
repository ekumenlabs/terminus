from city import City
from road import Street, Trunk
from point import Point
from block import Block
from building import Building

class SimpleCityBuilder(object):

    def get_city(self):
        size = 3
        city = City()

        self._create_street_matrix(city, size)
        self._create_surrounding_ring_road(city, size)
        self._create_blocks(city, size)
        self._create_bildings(city, size)
        return city

    def _create_street_matrix(self, city, size):
        for x in range(1, size):
            road = Street(str(x))
            road.add_segment(Point(0, x*100, 0))
            road.add_segment(Point(100 * size, x*100, 0))
            city.add_road(road)

        for x in range(1, size):
            road = Street(str(x))
            road.add_segment(Point(x*100, 0, 0))
            road.add_segment(Point(x*100, 100 * size, 0))
            city.add_road(road)

    def _create_surrounding_ring_road(self, city, size):
        ring_road_1 = Street('RingRoad1')
        ring_road_1.add_segment(Point(-2.5, 0, 0))
        ring_road_1.add_segment(Point(size*100+2.5, 0, 0))
        city.add_road(ring_road_1)

        ring_road_2 = Street('RingRoad2')
        ring_road_2.add_segment(Point(size*100, 0, 0))
        ring_road_2.add_segment(Point(size*100, size*100, 0))
        city.add_road(ring_road_2)

        ring_road_3 = Street('RingRoad3')
        ring_road_3.add_segment(Point(-2.5, size*100, 0))
        ring_road_3.add_segment(Point(size*100+2.5, size*100, 0))
        city.add_road(ring_road_3)

        ring_road_4 = Street('RingRoad4')
        ring_road_4.add_segment(Point(0, 0, 0))
        ring_road_4.add_segment(Point(0, size*100, 0))
        city.add_road(ring_road_4)

    def _create_blocks(self, city, size):
        for x in range(size):
            for y in range(size):
                block = Block(Point(x*100+50, y*100+50, 0))
                city.add_block(block)

    def _create_bildings(self, city, size):
        for x in range(size):
            for y in range(size):
              for block_x in range(6):
                  for block_y in range(6):
                    building = Building(Point(x*100+block_x*15+12, y*100+block_y*15+12, 0))
                    city.add_building(building)
