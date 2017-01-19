from city_model import CityModel
import math
from simple_node import SimpleNode
from intersection_node import IntersectionNode
from lane import Lane
from shapely.geometry import LineString


class Road(CityModel):
    def __init__(self, width, name=None):
        super(Road, self).__init__(name)
        self.width = width
        self.nodes = []
        self.point_to_node = {}
        self.lanes = []
        self.cached_waypoints = None

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

    def add_lane(self, offset, width=5):
        self.lanes.append(Lane(self, width, offset))

    def add_point(self, point):
        node = SimpleNode(point)
        self.nodes.append(node)
        node.added_to(self)
        self.point_to_node[point] = node
        self.cached_waypoints = None

    def points_count(self):
        return len(self.nodes)

    def node_count(self):
        return len(self.nodes)

    def get_width(self):
        return self.width

    def set_width(self, width):
        self.width = width

    def get_waypoints(self):
        if self.cached_waypoints is None:
            self.cached_waypoints = []
            for node in self.nodes:
                self.cached_waypoints.extend(node.get_waypoints_for(self))
        return self.cached_waypoints

    def waypoints_count(self):
        return len(self.get_waypoints())

    def previous_node(self, node):
        index = self.nodes.index(node)
        if index - 1 >= 0:
            return self.nodes[index - 1]
        else:
            return None

    def following_node(self, node):
        index = self.nodes.index(node)
        if index + 1 < len(self.nodes):
            return self.nodes[index + 1]
        else:
            return None

    def dispose(self):
        for node in self.nodes:
            node.removed_from(self)

    def replace_node_at(self, point, new_node):
        index = self._index_of_node_at(point)
        old_node = self.nodes[index]
        self.nodes[index] = new_node
        new_node.added_to(self)
        old_node.removed_from(self)
        self.cached_waypoints = None

    def includes_point(self, point):
        return point in self.point_to_node

    def node_at(self, point):
        return self.point_to_node[point]

    def reverse(self):
        self.nodes.reverse()

    def be_two_way(self):
        pass

    def length(self, initial=0, final=None):
        distances = self.get_waypoint_distances()
        if final is None:
            return math.fsum(distances[initial:])
        return math.fsum(distances[initial:final])

    def get_waypoint_positions(self):
        return map(lambda waypoint: waypoint.center, self.get_waypoints())

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
        return map(lambda node: node.center, self.nodes)

    def geometry_as_line_string(self, decimal_places=5):
        # Shapely behaves weirdly with very precise coordinates sometimes,
        # so we round to 5 decimals by default
        # http://gis.stackexchange.com/questions/50399/how-best-to-fix-a-non-noded-intersection-problem-in-postgis
        # http://freigeist.devmag.net/r/691-rgeos-topologyexception-found-non-noded-intersection-between.html
        coords = map(lambda node: (round(node.center.x, decimal_places), round(node.center.y, decimal_places)), self.nodes)
        return LineString(coords)

    def _index_of_node_at(self, point):
        return next((index for index, node in enumerate(self.nodes) if node.center == point), None)

    def _add_node(self, node):
        self.nodes.append(node)
        node.added_to(self)
        self.cached_waypoints = None

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.width == other.width and \
            self.nodes == other.nodes

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.width, tuple(self.nodes)))

    def __repr__(self):
        return "%s: " % self.__class__.__name__ + \
            reduce(lambda acc, node: acc + "%s," % str(node), self.nodes, '')
