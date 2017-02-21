from city_model import CityModel
from datetime import date
from road_intersection_node import RoadIntersectionNode
from geometry.bounding_box import BoundingBox
from road import Road
from building import Building
from block import Block
from ground_plane import GroundPlane


# For the time being, the city will be our Gazebo world
class City(CityModel):
    def __init__(self, name=None):
        super(City, self).__init__(name)
        self.ground_plane = None
        self.roads = []
        self.blocks = []
        self.buildings = []
        self.intersections = {}

    def set_ground_plane(self, ground_plane):
        self.ground_plane = ground_plane

    def add_road(self, road):
        self.roads.append(road)
        # We assume there will be globally way more intersections than nodes
        # in a street
        for node in road.get_nodes():
            if node.center in self.intersections:
                intersection = self.intersections[node.center]
                road.replace_node_at(node.center, intersection)

    def roads_count(self):
        return len(self.roads)

    def add_block(self, block):
        self.blocks.append(block)

    def add_building(self, building):
        self.buildings.append(building)

    def add_intersection_at(self, point):
        if point not in self.intersections:
            intersection = RoadIntersectionNode(point)
            # Register intersection
            self.intersections[point] = intersection
            # Add to it existing roads that include that point
            for road in self.roads:
                if road.includes_point(point):
                    road.replace_node_at(point, intersection)

    def bounding_box(self):
        road_boxes = self._box_list_from_list(self.roads)
        roads_bounding_box = BoundingBox.from_boxes(road_boxes)
        block_boxes = self._box_list_from_list(self.blocks)
        blocks_bounding_box = BoundingBox.from_boxes(block_boxes)
        building_boxes = self._box_list_from_list(self.buildings)
        buildings_bounding_box = BoundingBox.from_boxes(building_boxes)
        if self.ground_plane is not None:
            groung_plane_bounding_box = self.ground_plane.bounding_box()
            return BoundingBox.from_boxes([roads_bounding_box, blocks_bounding_box,
                                           buildings_bounding_box,
                                           groung_plane_bounding_box])
        else:
            return BoundingBox.from_boxes([roads_bounding_box, blocks_bounding_box,
                                           buildings_bounding_box])

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

    def _box_list_from_list(self, lst):
        return map(lambda x: x.bounding_box(), lst)
