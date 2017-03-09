"""
Copyright (C) 2017 Open Source Robotics Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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

        has_predecessor = predecessor is not None
        has_successor = successor is not None

        requires_exit_waypoint = any(other_lane.following_node(lane_node) is not None for other_lane in lane_node.involved_lanes_except(lane))
        requires_entry_waypoint = any(other_lane.previous_node(lane_node) is not None for other_lane in lane_node.involved_lanes_except(lane))

        if has_predecessor and has_successor:
            predecessor_vector = self.center - predecessor.center
            successor_vector = successor.center - self.center
            are_segments_colinear = predecessor_vector.cross_product(successor_vector) == Point(0.0, 0.0, 0.0)
            delta = min((predecessor_vector.norm() / 2.0) - 0.1, (successor_vector.norm() / 2.0) - 0.1, 5)
        else:
            are_segments_colinear = True
            if has_predecessor:
                predecessor_vector = self.center - predecessor.center
                delta = min((predecessor_vector.norm() / 2.0) - 0.1, 5)
            elif has_successor:
                successor_vector = successor.center - self.center
                delta = min((successor_vector.norm() / 2.0) - 0.1, 5)

        add_predecessor_waypoint = has_predecessor and (requires_exit_waypoint or not are_segments_colinear)
        add_successor_waypoint = has_successor and (requires_entry_waypoint or not are_segments_colinear)

        if add_predecessor_waypoint:
            point = LineString([lane_node.center.to_shapely_point(), predecessor.center.to_shapely_point()]).interpolate(delta)
            waypoint = Waypoint(lane, lane_node, Point.from_shapely(point))
            if requires_exit_waypoint:
                waypoint.be_exit()
            if has_successor and not are_segments_colinear:
                waypoint.be_arc_start_connection()
            waypoints.append(waypoint)

        if (not add_predecessor_waypoint or not add_successor_waypoint):
            waypoints.append(Waypoint(lane, lane_node, lane_node.center))

        if add_successor_waypoint:
            point = LineString([lane_node.center.to_shapely_point(), successor.center.to_shapely_point()]).interpolate(delta)
            waypoint = Waypoint(lane, lane_node, Point.from_shapely(point))
            if requires_entry_waypoint:
                waypoint.be_entry()
            if has_predecessor and not are_segments_colinear:
                waypoint.be_arc_end_connection()
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
        return "LaneIntersectionNode @ " + str(self.center) + " " + str(self.source)
