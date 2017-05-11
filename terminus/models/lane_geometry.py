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
from geometry.path import Path

from junction_builder import JunctionBuilder
from waypoint import Waypoint
from waypoint_connection import WaypointConnection

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LaneGeometry(object):

    def __init__(self, lane):
        self._lane = lane
        self._path, self._waypoints = self._build_path_and_waypoints(lane)
        self._center_to_waypoint = self._build_waypoint_table()
        self._simplify_path()
        self._waypoints = self._remove_redundant_waypoints()
        self._unresolved_intersections = self._create_unresolved_intersections()
        self._inner_connections = self._build_inner_connections()

    def species(self):
        return self.__class__

    def lane(self):
        return self._lane

    def road(self):
        return self.lane().road()

    def road_nodes(self):
        return self.lane().road_nodes()

    def path(self):
        return self._path

    def waypoints(self):
        if not self._are_all_intersections_resolved():
            self._resolve_intersections()
        return self._waypoints

    def inner_connections(self):
        if not self._are_all_intersections_resolved():
            self._resolve_intersections()
        return self._inner_connections

    def waypoint_at_point(self, point):
        return self._center_to_waypoint.get(point.rounded_to(5), None)

    def resolve_intersection(self, road_node, waypoints):
        # Mark as resolved
        self._unresolved_intersections.remove(road_node)

        # Add new waypoints
        new_waypoints = waypoints - set(self._waypoints)
        new_waypoints = sorted(new_waypoints,
                               key=lambda waypoint: self.path().offset_for_point(waypoint.center()))

        new_waypoints_clone = list(new_waypoints)

        # We need to manually sort to account for overlapping waypoints
        # TODO: Review this
        waypoints_index = 0
        merged_waypoints = []
        current_waypoint_offset = 0.0
        while new_waypoints:
            new_waypoint = new_waypoints.pop(0)
            new_waypoint_offset = self.path().offset_for_point(new_waypoint.center())

            current_waypoint = self._waypoints[waypoints_index]
            current_waypoint_offset = self.path().offset_for_point(current_waypoint.center(), current_waypoint_offset)

            while current_waypoint_offset < new_waypoint_offset:
                merged_waypoints.append(current_waypoint)
                waypoints_index += 1
                current_waypoint = self._waypoints[waypoints_index]
                current_waypoint_offset = self.path().offset_for_point(current_waypoint.center(), current_waypoint_offset)

            merged_waypoints.append(new_waypoint)

        while waypoints_index < len(self._waypoints):
            current_waypoint = self._waypoints[waypoints_index]
            merged_waypoints.append(current_waypoint)
            waypoints_index += 1

        self._waypoints = merged_waypoints

        # Accommodate new waypoints in path
        self._path = self._path.split_in(self._waypoints)

        # Rebuild inner connections
        self._inner_connections = self._build_inner_connections()

    @classmethod
    def _new_waypoint(cls, lane, primitive, node, use_start=True):
        if use_start:
            point, heading = primitive.start_point(), primitive.start_heading()
        else:
            point, heading = primitive.end_point(), primitive.end_heading()
        return Waypoint(lane, point, heading, node)

    def _path_for(self, lane):
        return self.species().build_path_and_waypoints(lane)[0]

    def _simplify_path(self):
        self._path.simplify()

    def _build_waypoint_table(self):
        center_to_waypoint = {}
        for waypoint in self._waypoints:
            center_to_waypoint[waypoint.center().rounded_to(5)] = waypoint
        return center_to_waypoint

    def _build_inner_connections(self):
        connections = []
        waypoint_index = 0
        for element in self.path():
            start_waypoint = self._waypoints[waypoint_index]
            waypoint_index += 1
            end_waypoint = self._waypoints[waypoint_index]
            connections.append(WaypointConnection(start_waypoint, end_waypoint, element))
        return connections

    def _remove_redundant_waypoints(self):
        # Some waypoints may no longer be included in the path geometry
        # due to simplification approximating the geometry. If so, remove them
        in_waypoints = []
        for waypoint in self._waypoints:
            waypoint_center = waypoint.center()
            if self._path.includes_point(waypoint_center):
                in_waypoints.append(waypoint)

        # Now remove the waypoints that lay in between the geometry
        trimmed_waypoints = []
        element_index = 0
        for waypoint in in_waypoints:
            waypoint_center = waypoint.center()
            current_element = self._path.element_at(element_index)
            while not current_element.includes_point(waypoint_center):
                element_index += 1
                current_element = self._path.element_at(element_index)
            if current_element.start_point() == waypoint_center or \
               current_element.end_point() == waypoint_center:
                trimmed_waypoints.append(waypoint)
        return trimmed_waypoints

    def _create_unresolved_intersections(self):
        return filter(lambda node: node.is_intersection(), self.road_nodes())

    def _are_all_intersections_resolved(self):
        return len(self._unresolved_intersections) == 0

    def _build_path_and_waypoints(self, lane):
        return self.species().build_path_and_waypoints(lane)

    def _resolve_intersections(self):
        self._build_missing_intersections()

    def _build_missing_intersections(self):
        lane = self.lane()
        # We will be removing items as we iterate, so make a copy
        for node in list(self._unresolved_intersections):
            builder = JunctionBuilder(node, self.species())
            builder.add_connections_to_lanes()
