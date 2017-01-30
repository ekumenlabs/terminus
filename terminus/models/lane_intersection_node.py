from geometry.point import Point
from lane_node import LaneNode
from shapely.geometry import LineString
from waypoint import Waypoint

class LaneIntersectionNode(LaneNode):

    def __init__(self, center, main_lane, road_node):
        self.lanes = []
        super(LaneIntersectionNode, self).__init__(center, main_lane, road_node)

    def added_to(self, lane):
        self.lanes.append(lane)

    def involved_lanes(self):
        return self.lanes

    def get_waypoints_for(self, lane):
        waypoints = []
        lane_node = lane.find_node_matching(self)
        predecessor = lane.previous_node(lane_node)
        successor = lane.following_node(lane_node)

        requires_exit_waypoint = any(other_lane.following_node(lane_node) is not None for other_lane in lane_node.involved_lanes_except(lane))
        requires_entry_waypoint = any(other_lane.previous_node(lane_node) is not None for other_lane in lane_node.involved_lanes_except(lane))

        add_exit_waypoint = requires_exit_waypoint and predecessor is not None
        add_entry_waypoint = requires_entry_waypoint and successor is not None

        if add_exit_waypoint:
            point = LineString([lane_node.center.to_shapely_point(), predecessor.center.to_shapely_point()]).interpolate(5)
            waypoint = Waypoint(lane, lane_node, Point.from_shapely(point))
            waypoint.be_exit()
            waypoints.append(waypoint)

        if (not add_entry_waypoint or not add_exit_waypoint):
            waypoints.append(Waypoint(lane, lane_node, lane_node.center))

        if add_entry_waypoint:
            point = LineString([lane_node.center.to_shapely_point(), successor.center.to_shapely_point()]).interpolate(5)
            waypoint = Waypoint(lane, lane_node, Point.from_shapely(point))
            waypoint.be_entry()
            waypoints.append(waypoint)

        return waypoints

    def connected_waypoints_for(self, source_waypoint):
        lanes = filter(lambda lane: lane is not source_waypoint.lane, self.lanes)
        connections = []
        for lane in lanes:
            for waypoint in self.get_entry_waypoints_for(lane):
                # if source_waypoint is not waypoint:
                connections.append(waypoint)
        return connections

    def __repr__(self):
        return "LaneIntersectionNode @ " + str(self.center)
