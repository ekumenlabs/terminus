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

    # Converted to Lane
    def get_waypoints_for(self, lane):
        waypoints = []
        predecessor = lane.previous_node(self)
        successor = lane.following_node(self)
        add_exit_waypoint = predecessor is not None and \
            any(lane.following_node(self) is not None for lane in self.involved_roads_except(lane))
        add_entry_waypoint = successor is not None and \
            any(lane.previous_node(self) is not None for lane in self.involved_roads_except(lane))

        if add_exit_waypoint:
            point = LineString([self.center.to_shapely_point(), predecessor.center.to_shapely_point()]).interpolate(5)
            waypoint = Waypoint(lane, self, Point.from_shapely(point))
            waypoint.be_exit()
            waypoints.append(waypoint)

        if not add_entry_waypoint or not add_exit_waypoint:
            waypoints.append(Waypoint(lane, self, self.center))

        if add_entry_waypoint:
            point = LineString([self.center.to_shapely_point(), successor.center.to_shapely_point()]).interpolate(5)
            waypoint = Waypoint(lane, self, Point.from_shapely(point))
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
