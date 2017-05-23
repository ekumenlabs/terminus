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

from geometry.path import Path
from geometry.line_segment import LineSegment

from waypoint import Waypoint
from lane_geometry import LaneGeometry


class PolylineGeometry(LaneGeometry):

    @classmethod
    def build_path_and_waypoints(cls, lane, mapped_centers):
        if lane.road_nodes_count() < 2:
            raise ValueError("At least two nodes are required to build a geometry")

        road_nodes = lane.road_nodes()
        node_pairs = zip(road_nodes, road_nodes[1:])
        path = Path()
        waypoints = []
        for start_node, end_node in node_pairs:
            start_point = mapped_centers[start_node]
            end_point = mapped_centers[end_node]
            segment = LineSegment(start_point, end_point)
            path.add_element(segment)
            waypoints.append(cls._new_waypoint(lane, segment, start_node))
        # The last waypoint is missing, as we have been processing the
        # start of each segment
        waypoint = cls._new_waypoint(lane, path.last_element(), road_nodes[-1], False)
        waypoints.append(waypoint)
        return (path, waypoints)

    @classmethod
    def connect(cls, exit_waypoint, entry_waypoint):
        return LineSegment(exit_waypoint.center(), entry_waypoint.center())
