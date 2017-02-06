import math
from shapely.geometry import LineString
from geometry.point import Point
from geometry.bounding_box import BoundingBox

from city_model import CityModel
from road_simple_node import RoadSimpleNode
from road_intersection_node import RoadIntersectionNode
from lane_intersection_node import LaneIntersectionNode
from lane import Lane
from road_node import RoadNode


class Road(CityModel):
    def __init__(self, name=None):
        super(Road, self).__init__(name)
        self._nodes = []
        self._point_to_node = {}
        self._lanes = []

    @classmethod
    def from_nodes(cls, array_of_nodes):
        '''Please use the `from_points` class method if possible. This method
        will be deprecated in the future'''
        road = cls()
        for node in array_of_nodes:
            road._add_node(node)
        return road

    @classmethod
    def from_points(cls, array_of_points):
        road = cls()
        for point in array_of_points:
            road.add_point(point)
        return road

    def width(self):
        external_offsets = map(lambda lane: lane.external_offset(), self.get_lanes())
        return abs(min(external_offsets)) + abs(max(external_offsets))

    def add_lane(self, offset, width=4):
        self._lanes.append(Lane(self, width, offset))

    def lane_count(self):
        return len(self._lanes)

    def get_lanes(self):
        return self._lanes

    def add_point(self, point):
        node = RoadSimpleNode(point)
        self._add_node(node)
        self._point_to_node[point] = node

    def points_count(self):
        return len(self._nodes)

    def get_nodes(self):
        return self._nodes

    def get_node_at(self, index):
        return self._nodes[index]

    def node_count(self):
        return len(self._nodes)

    def first_node(self):
        return self._nodes[0]

    def last_node(self):
        return self._nodes[-1]

    def is_first_node(self, node):
        return self.first_node() is node

    def is_last_node(self, node):
        return self.last_node() is node

    def replace_node_at(self, point, new_node):
        index = self._index_of_node_at(point)
        old_node = self._nodes[index]
        self._nodes[index] = new_node
        new_node.added_to(self)
        old_node.removed_from(self)

    def includes_point(self, point):
        return point in self._point_to_node

    def reverse(self):
        self._nodes.reverse()

    def be_two_way(self):
        pass

    def length(self, initial=0, final=None):
        distances = self.get_waypoint_distances()
        if final is None:
            return math.fsum(distances[initial:])
        return math.fsum(distances[initial:final])

    def waypoints_count(self):
        return len(self.get_nodes())

    def get_waypoint_positions(self):
        return map(lambda waypoint: waypoint.center, self._nodes)

    def get_waypoint_distances(self):
        points = self.get_waypoint_positions()
        if len(points) == 1:
            return [0.0]
        point_pairs = zip(points, points[1:])
        return map(lambda point_pair: point_pair[0].distance_to(point_pair[1]), point_pairs)

    def get_waypoints_yaws(self):
        points = self.get_waypoint_positions()
        if len(points) == 1:
            return [0.0]
        point_pairs = zip(points, points[1:])
        return map(lambda point_pair: point_pair[0].yaw(point_pair[1]), point_pairs)

    def geometry(self):
        return map(lambda node: node.center, self._nodes)

    def geometry_as_line_string(self):
        coords = map(lambda node: node.center.to_tuple(), self._nodes)
        return LineString(coords)

    def _index_of_node_at(self, point):
        return next((index for index, node in enumerate(self._nodes) if node.center == point), None)

    def _add_node(self, node):
        self._nodes.append(node)
        node.added_to(self)

    def node_bounding_boxes(self):
        return map((lambda node: node.bounding_box(self.width())), self._nodes)

    def bounding_box(self):
        node_bounding_boxes = self.node_bounding_boxes()
        return BoundingBox.from_boxes(node_bounding_boxes)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.width() == other.width() and \
            self._nodes == other._nodes

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.width(), tuple(self._nodes)))

    def __repr__(self):
        return "%s: " % self.__class__.__name__ + \
            reduce(lambda acc, node: acc + "%s," % str(node), self._nodes, '')
