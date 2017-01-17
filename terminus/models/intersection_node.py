from geometry.point import Point
from road_node import RoadNode
from shapely.geometry import LineString
from waypoint import Waypoint


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
