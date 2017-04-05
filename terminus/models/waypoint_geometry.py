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

from waypoint import Waypoint
from waypoint_connection import WaypointConnection

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WaypointGeometry(object):

    def __init__(self, lane, path_geometry):
        self._lane = lane
        self._geometry = path_geometry
        self._primitives = []
        self._build_prmitives()

    def waypoints_count(self):
        return len(self._waypoints)

    def waypoints(self):
        return self._waypoints

    def connections(self):
        return self._connections

    def _build_prmitives(self):
        self._waypoints = self._build_waypoints()
        self._waypoints = self._remove_redundant_waypoints()
        self._split_geometry = self._geometry.split_in(self._waypoints)
        self._connections = self._build_connections()

    def _build_waypoints(self):
        lane = self._lane
        road = lane.road()
        geometry = self._geometry
        waypoints = {}
        for waypoint in geometry.waypoints(lane):
            waypoints[waypoint.center().rounded_to(7)] = waypoint
        road_nodes = road.nodes()
        intersection_nodes = filter(lambda node: node.is_intersection(), road_nodes)
        intersection_waypoints = []
        for node in intersection_nodes:
            other_roads = node.involved_roads_except(road)
            other_lanes = []
            for other_road in other_roads:
                other_lanes.extend(other_road.lanes())
            for other_lane in other_lanes:
                intersections = self._intersecting_waypoints_at(node, lane, geometry, other_lane, other_lane.lines_and_arcs_geometry())
                for intersection_waypoint in intersections:
                    rounded_point = intersection_waypoint.center().rounded_to(7)
                    if rounded_point in waypoints:
                        existing_waypoint = waypoints[rounded_point]
                        existing_waypoint.add_connections_from(intersection_waypoint)
                    else:
                        waypoints[rounded_point] = intersection_waypoint
        waypoint_collection = waypoints.values()
        return sorted(waypoint_collection,
                      key=lambda waypoint: geometry.offset_for_point(waypoint.center()))

    def _intersecting_waypoints_at(self, road_node, source_lane, source_geometry, target_lane, target_geometry):
        intersections = []
        intersection_control_point = road_node.center

        for source_element in source_geometry.elements():
            for target_element in target_geometry.elements():
                intersection = source_element.find_intersection(target_element)
                if intersection:
                    intersections.append(intersection)

        if not intersections:
            logger.warn("Couldn't find intersection between geometries")
            logger.warn("ROAD NODE: {0}".format(road_node))
            logger.warn("SOURCE: {0}".format(source_geometry))
            logger.warn("TARGET: {0}".format(target_geometry))
            return []

        intersections = sorted(intersections,
                               key=lambda point: point.squared_distance_to(intersection_control_point))
        intersection = intersections[0]

        source_path_offset = source_geometry.offset_for_point(intersection)
        source_path_length = source_geometry.length()

        target_path_offset = target_geometry.offset_for_point(intersection)
        target_path_length = target_geometry.length()

        waypoints = []

        initial_connection_offset = 7

        connection_offset = initial_connection_offset
        while True:
            if (source_path_offset >= connection_offset) and (target_path_offset + connection_offset <= target_path_length):
                exit_offset = source_path_offset - connection_offset
                exit_point = source_geometry.point_at_offset(exit_offset)
                exit_heading = source_geometry.heading_at_offset(exit_offset)
                exit_waypoint = Waypoint(source_lane, source_geometry, exit_point, exit_heading, road_node)

                entry_offset = target_path_offset + connection_offset
                entry_point = target_geometry.point_at_offset(entry_offset)
                entry_heading = target_geometry.heading_at_offset(entry_offset)
                entry_waypoint = Waypoint(target_lane, target_geometry, entry_point, entry_heading, road_node)

                connection = self._connect(exit_waypoint, entry_waypoint)

                if connection is None:
                    connection_offset += 0.5
                else:
                    exit_waypoint.add_out_connection(self._connect(exit_waypoint, entry_waypoint))
                    waypoints.append(exit_waypoint)
                    break
            else:
                break

        connection_offset = initial_connection_offset
        while True:
            if (source_path_offset + connection_offset <= source_path_length) and (target_path_offset >= connection_offset):
                entry_offset = source_path_offset + connection_offset
                entry_point = source_geometry.point_at_offset(entry_offset)
                entry_heading = source_geometry.heading_at_offset(entry_offset)
                entry_waypoint = Waypoint(source_lane, source_geometry, entry_point, entry_heading, road_node)

                exit_offset = target_path_offset - connection_offset
                exit_point = target_geometry.point_at_offset(exit_offset)
                exit_heading = target_geometry.heading_at_offset(exit_offset)
                exit_waypoint = Waypoint(target_lane, target_geometry, exit_point, exit_heading, road_node)

                connection = self._connect(exit_waypoint, entry_waypoint)

                if connection is None:
                    connection_offset += 0.5
                else:
                    entry_waypoint.add_in_connection(connection)
                    waypoints.append(entry_waypoint)
                    break
            else:
                break

        return waypoints

    def _build_connections(self):
        waypoint_index = 0
        connections = []
        for element in self._split_geometry.elements():
            start_waypoint = self._waypoints[waypoint_index]
            waypoint_index += 1
            end_waypoint = self._waypoints[waypoint_index]
            connections.append(WaypointConnection(start_waypoint, end_waypoint, element))
        return connections

    def _remove_redundant_waypoints(self):
        trimmed_waypoints = []
        waypoint_index = 0
        for element in self._geometry.elements():
            current_waypoint = self._waypoints[waypoint_index]
            element_waypoints = []
            while current_waypoint.center() != element.end_point():
                element_waypoints.append(current_waypoint)
                waypoint_index += 1
                current_waypoint = self._waypoints[waypoint_index]
            element_waypoints.append(current_waypoint)
            # At this point, except for the first and last waypoint, all
            # intermediate waypoints that are not intersections are redundant
            trimmed_waypoints.append(element_waypoints.pop(0))
            while len(element_waypoints) > 1:
                waypoint = element_waypoints.pop(0)
                if waypoint.is_intersection():
                    trimmed_waypoints.append(waypoint)
        trimmed_waypoints.append(element_waypoints.pop(0))
        return trimmed_waypoints

    def _connect(self, exit_waypoint, entry_waypoint):
        primitive = self._geometry.connect_waypoints(exit_waypoint, entry_waypoint)
        if primitive.is_valid_path_connection():
            return WaypointConnection(exit_waypoint, entry_waypoint, primitive)
        else:
            return None
