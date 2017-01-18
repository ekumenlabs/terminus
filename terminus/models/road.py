from geometry.point import Point
from shapely.geometry import LineString
from city_model import CityModel
import math


class Road(CityModel):
    def __init__(self, width, name=None):
        super(Road, self).__init__(name)
        self.width = width
        self.nodes = []
        self.point_to_node = {}
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

    def add_point(self, point):
        node = SimpleNode(point)
        self.nodes.append(node)
        node.added_to(self)
        self.point_to_node[point] = node
        self.cached_waypoints = None

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
        distances = []
        for i in range(len(points) - 1):
            distances.append(points[i].distance_to(points[i + 1]))
        return distances

    def get_waypoints_yaws(self):
        points = self.get_waypoint_positions()
        yaws = []
        for i in range(len(points) - 1):
            yaws.append(points[i].yaw(points[i + 1]))
        return yaws

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


class RoadNode(object):
    def __init__(self, center, name=None):
        self.center = center
        self.name = name

    @classmethod
    def on(cls, *args, **kwargs):
        return cls(Point(*args, **kwargs))

    def get_waypoints_for(self, road):
        raise NotImplementedError()

    def added_to(self, road):
        raise NotImplementedError()

    def removed_from(self, road):
        raise NotImplementedError()

    def connected_waypoints_for(self, waypoint):
        raise NotImplementedError()

    def involved_roads(self):
        raise NotImplementedError()

    def __ne__(self, other):
        return not self.__eq__(other)


class SimpleNode(RoadNode):

    def added_to(self, road):
        self.road = road

    def removed_from(self, road):
        self.road = None

    def get_waypoints_for(self, road):
        if (self.road is not road):
            return None
        return [Waypoint(road, self, self.center)]

    def connected_waypoints_for(self, waypoint):
        return []

    def involved_roads(self):
        return [self.road]

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.center == other.center

    def __hash__(self):
        return hash((self.__class__, self.center))

    def __repr__(self):
        return "SimpleNode @ " + str(self.center)


class IntersectionNode(RoadNode):

    def __init__(self, center, name=None):
        super(IntersectionNode, self).__init__(center, name)
        self.roads = []

    def added_to(self, road):
        self.add_road(road)

    def add_road(self, road):
        self.roads.append(road)

    def removed_from(self, road):
        self.roads.remove(road)

    def get_waypoints_for(self, road):
        waypoints = []
        predecessor = road.previous_node(self)
        successor = road.following_node(self)
        has_predecessor = predecessor is not None
        has_successor = successor is not None

        if has_predecessor:
            point = LineString([self.center.to_shapely_point(), predecessor.center.to_shapely_point()]).interpolate(5)
            waypoint = Waypoint(road, self, Point.from_shapely(point))
            waypoint.be_exit()
            waypoints.append(waypoint)

        if not has_predecessor or not has_successor:
            waypoints.append(Waypoint(road, self, self.center))

        if has_successor:
            point = LineString([self.center.to_shapely_point(), successor.center.to_shapely_point()]).interpolate(5)
            waypoint = Waypoint(road, self, Point.from_shapely(point))
            waypoint.be_entry()
            waypoints.append(waypoint)

        return waypoints

    def connected_waypoints_for(self, source_waypoint):
        roads = filter(lambda r: r is not source_waypoint.road, self.roads)
        connections = []
        for road in roads:
            for waypoint in self.get_entry_waypoints_for(road):
                if source_waypoint is not waypoint:
                    connections.append(waypoint)
        return connections

    def get_entry_waypoints_for(self, road):
        return filter(lambda waypoint: waypoint.is_entry(), self.get_waypoints_for(road))

    def get_exit_waypoints_for(self, road):
        return filter(lambda waypoint: waypoint.is_exit(), self.get_waypoints_for(road))

    def involved_roads(self):
        return self.roads

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.center == other.center

    def __hash__(self):
        return hash((self.__class__, self.center))

    def __repr__(self):
        return "IntersectionNode @ " + str(self.center)


class Waypoint(object):
    def __init__(self, road, source_node, center):
        self.road = road
        self.source_node = source_node
        self.center = center
        self.be_reference()

    def is_exit(self):
        return self.type.is_exit()

    def is_entry(self):
        return self.type.is_entry()

    def be_entry(self):
        self.type = EntryPoint()

    def be_exit(self):
        self.type = ExitPoint()

    def be_reference(self):
        self.type = ReferencePoint()

    def connected_waypoints(self):
        return self.source_node.connected_waypoints_for(self)

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and \
               (self.type == other.type) and \
               (self.center == other.center) and \
               (self.source_node == other.source_node) and \
               (self.road == other.road)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.type, self.center, self.road, self.source_node))

    def __repr__(self):
        return str(id(self)) + str(self.type) + "Waypoint at " + str(self.center)


class WaypointType(object):
    def is_exit(self):
        raise NotImplementedError()

    def is_entry(self):
        raise NotImplementedError()

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__class__)


class ReferencePoint(WaypointType):
    def is_exit(self):
        return False

    def is_entry(self):
        return False

    def __repr__(self):
        return ""


class EntryPoint(WaypointType):
    def is_exit(self):
        return False

    def is_entry(self):
        return True

    def __repr__(self):
        return "[ENTRY] "


class ExitPoint(WaypointType):
    def is_exit(self):
        return True

    def is_entry(self):
        return False

    def __repr__(self):
        return "[EXIT] "
