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

    def __init__(self, lane, path_geometry, builder):
        self._lane = lane
        self._geometry = path_geometry
        self._primitives = []
        self._builder = builder
        self._build_prmitives()

    def geometry(self):
        return self._geometry

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
        for waypoint in geometry.waypoints(lane, self._builder):
            waypoints[waypoint.center().rounded()] = waypoint
        road_nodes = road.nodes()
        intersection_nodes = filter(lambda node: node.is_intersection(), road_nodes)
        intersection_waypoints = []
        for node in intersection_nodes:
            other_roads = node.involved_roads_except(road)
            other_lanes = []
            for other_road in other_roads:
                other_lanes.extend(other_road.lanes())
            for other_lane in other_lanes:
                intersections = self._intersecting_waypoints_at(node, lane, geometry, other_lane, other_lane.geometry_using(self._builder.__class__))
                for intersection_waypoint in intersections:
                    rounded_point = intersection_waypoint.center().rounded()
                    if rounded_point in waypoints:
                        existing_waypoint = waypoints[rounded_point]
                        existing_waypoint.add_connections_from(intersection_waypoint)
                    else:
                        waypoints[rounded_point] = intersection_waypoint
        waypoint_collection = waypoints.values()
        return sorted(waypoint_collection,
                      key=lambda waypoint: geometry.offset_for_point(waypoint.center()))

    def _intersecting_waypoints_at(self, road_node, source_lane, source_geometry, target_lane, target_geometry):
        intersections = set()
        intersection_control_point = road_node.center

        for source_element in source_geometry.elements():
            for target_element in target_geometry.elements():
                intersection = source_element.find_intersection(target_element)
                if intersection:
                    intersections.add(intersection)

        if not intersections:
            logger.warn("Couldn't find intersection between geometries")
            logger.warn("ROAD NODE: {0}".format(road_node))
            logger.warn("SOURCE: {0}".format(source_geometry))
            logger.warn("TARGET: {0}".format(target_geometry))
            return []

        intersections = list(intersections)

        if len(intersections) > 1:
            logger.warn("Multiple intersections found between geometries")
            logger.warn("ROAD NODE: {0}".format(road_node))
            logger.warn("SOURCE: {0}".format(source_geometry))
            logger.warn("TARGET: {0}".format(target_geometry))
            logger.warn("INTERSECTIONS: {0}".format(intersections))
            intersections = sorted(intersections,
                                   key=lambda point: point.squared_distance_to(intersection_control_point))

        intersection = intersections[0]
        waypoints = []

        out_connection = self._find_connection(7, road_node, intersection, target_lane, target_geometry, source_lane, source_geometry)

        if out_connection:
            entry_waypoint, exit_waypoint, connection = out_connection
            exit_waypoint.add_out_connection(connection)
            waypoints.append(exit_waypoint)

        in_connection = self._find_connection(7, road_node, intersection, source_lane, source_geometry, target_lane, target_geometry)

        if in_connection:
            entry_waypoint, exit_waypoint, connection = in_connection
            entry_waypoint.add_in_connection(connection)
            waypoints.append(entry_waypoint)

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

    def _find_connection(self, minimum_offset, road_node, intersection, source_lane, source_geometry, target_lane, target_geometry):

        source_offset = source_geometry.offset_for_point(intersection)
        source_length = source_geometry.length()

        target_offset = target_geometry.offset_for_point(intersection)
        target_length = target_geometry.length()

        connection_offset = minimum_offset

        while True:
            if (source_offset + connection_offset <= source_length) and (target_offset >= connection_offset):
                entry_offset = source_offset + connection_offset
                entry_point = source_geometry.point_at_offset(entry_offset)
                entry_heading = source_geometry.heading_at_offset(entry_offset)
                entry_waypoint = Waypoint(source_lane, source_geometry, entry_point, entry_heading, road_node)

                exit_offset = target_offset - connection_offset
                exit_point = target_geometry.point_at_offset(exit_offset)
                exit_heading = target_geometry.heading_at_offset(exit_offset)
                exit_waypoint = Waypoint(target_lane, target_geometry, exit_point, exit_heading, road_node)

                connection = self._connect(exit_waypoint, entry_waypoint)

                if connection is None:
                    connection_offset += 0.5
                else:
                    return (entry_waypoint, exit_waypoint, connection)
            else:
                return None

    def _connect(self, exit_waypoint, entry_waypoint):
        primitive = self._builder.connect_waypoints(exit_waypoint, entry_waypoint)
        if primitive.is_valid_path_connection():
            # TODO: We should start using asserts
            if not primitive.end_point().almost_equal_to(entry_waypoint.center(), 7):
                message_template = "Bad connection between {0} and {1} using {2}\nExpecting {3} but {4} given"
                message = message_template.format(exit_waypoint, entry_waypoint, primitive, entry_waypoint.center(), primitive.end_point())
                raise ValueError(message)
            return WaypointConnection(exit_waypoint, entry_waypoint, primitive)
        else:
            return None
