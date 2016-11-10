from city_model import CityModel
from datetime import date


# For the time being, the city will be our Gazebo world
class City(CityModel):
    def __init__(self, name=None):
        super(City, self).__init__(name)
        self.ground_plane = None
        self.roads = []
        self.blocks = []
        self.buildings = []

    def set_ground_plane(self, ground_plane):
        self.ground_plane = ground_plane

    def add_road(self, road):
        self.roads.append(road)

    def roads_count(self):
        return len(self.roads)

    def add_block(self, block):
        self.blocks.append(block)

    def add_building(self, building):
        self.buildings.append(building)

    def accept(self, generator):
        generator.start_city(self)
        if self.ground_plane is not None:
            self.ground_plane.accept(generator)
        for road in self.roads:
            road.accept(generator)
        for block in self.blocks:
            block.accept(generator)
        for building in self.buildings:
            building.accept(generator)
        generator.end_city(self)
