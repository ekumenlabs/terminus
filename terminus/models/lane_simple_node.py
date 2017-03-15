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

from lane_node import LaneNode
from waypoint import Waypoint
from geometry.point import Point
from geometry.line_segment import LineSegment
from shapely.geometry import LineString


class LaneSimpleNode(LaneNode):

    def __init__(self, center, main_lane, road_node):
        self.lane = None
        super(LaneSimpleNode, self).__init__(center, main_lane, road_node)

    def added_to(self, lane):
        self.lane = lane

    def involved_lane(self):
        return [self.lane]

    def is_intersection(self):
        return False

    def get_waypoints_for(self, lane):
        if (self.lane is not lane):
            return None

        previous_node = lane.previous_node(self)
        following_node = lane.following_node(self)
        if previous_node is None or following_node is None:
            return [Waypoint(lane, self, self.center)]
        else:
            previous_vector = self.center - previous_node.center
            following_vector = following_node.center - self.center
            # If they are colinear
            if previous_vector.cross_product(following_vector) == Point(0.0, 0.0, 0.0):
                return [Waypoint(lane, self, self.center)]
            else:
                previous_segment = LineSegment(previous_node.center, self.center)
                following_segment = LineSegment(following_node.center, self.center)

                delta = min((previous_segment.length() / 2.0) - 0.1, (following_segment.length() / 2.0) - 0.1, 5)

                point = LineString([self.center.to_shapely_point(), previous_node.center.to_shapely_point()]).interpolate(delta)
                previous_waypoint_center = Point.from_shapely(point)
                previous_waypoint = Waypoint(lane, self, previous_waypoint_center)
                previous_waypoint.be_arc_start_connection()

                point = LineString([self.center.to_shapely_point(), following_node.center.to_shapely_point()]).interpolate(delta)
                following_waypoint_center = Point.from_shapely(point)
                following_waypoint = Waypoint(lane, self, following_waypoint_center)
                following_waypoint.be_arc_end_connection()

        return [previous_waypoint, following_waypoint]

    def connected_waypoints_for(self, waypoint):
        return []

    def __repr__(self):
        return "LaneSimpleNode @ " + str(self.center) + " " + str(self.source)
