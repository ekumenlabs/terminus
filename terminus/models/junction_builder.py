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
import math
from collections import OrderedDict

from geometry.circle import Circle
from geometry.point import Point
from geometry.path import Path

from waypoint import Waypoint
from waypoint_connection import WaypointConnection

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JunctionNotSatisfied(Exception):
    pass


class JunctionBuilder(object):

    def __init__(self, road_node, mapped_intersection_center, geometry_class):
        self._road_node = road_node
        self._mapped_intersection_center = mapped_intersection_center
        self._geometry_class = geometry_class

    def lanes(self):
        return self._road_node.involved_lanes()

    def mapped_intersection_center(self):
        return self._mapped_intersection_center

    def intersection_center(self):
        return self._road_node.center

    def add_connections_to_lanes(self):
        lane_pairs = self._create_lane_pairs()
        try:
            connections = self._fulfill_intersection_with_single_length(lane_pairs)
        except JunctionNotSatisfied:
            connections = self._fulfill_intersection_with_adaptive_approach(lane_pairs)

        waypoints_by_lane = OrderedDict()

        for lane in self.lanes():
            waypoints_by_lane[lane] = OrderedDict()

        for connection in connections:
            exit_waypoint = connection.start_waypoint()
            exit_waypoint.add_out_connection(connection)
            if exit_waypoint in waypoints_by_lane[exit_waypoint.lane()]:
                existing_waypoint = waypoints_by_lane[exit_waypoint.lane()][hash(exit_waypoint)]
                connection._start_waypoint = existing_waypoint
                connection._waypoints[0] = existing_waypoint
            else:
                waypoints_by_lane[exit_waypoint.lane()][hash(exit_waypoint)] = exit_waypoint

            entry_waypoint = connection.end_waypoint()
            entry_waypoint.add_in_connection(connection)
            if entry_waypoint in waypoints_by_lane[entry_waypoint.lane()]:
                existing_waypoint = waypoints_by_lane[entry_waypoint.lane()][hash(entry_waypoint)]
                connection._end_waypoint = existing_waypoint
                connection._waypoints[-1] = existing_waypoint
            else:
                waypoints_by_lane[entry_waypoint.lane()][hash(entry_waypoint)] = entry_waypoint

        for lane, waypoints in waypoints_by_lane.iteritems():
            geometry = lane._lane_geometry(self._geometry_class)
            geometry.resolve_intersection(self._road_node, set(waypoints.values()))

    def _create_lane_pairs(self):
        lane_pairs = OrderedDict()
        node = self._road_node
        entry_lanes = []
        exit_lanes = []
        for lane in self.lanes():
            if lane.starts_on(node) and not lane.ends_on(node):
                entry_lanes.append(lane)
            elif lane.ends_on(node) and not lane.starts_on(node):
                exit_lanes.append(lane)
            else:
                entry_lanes.append(lane)
                exit_lanes.append(lane)

        for exit_lane in exit_lanes:
            for entry_lane in entry_lanes:
                if exit_lane.road() is not entry_lane.road():
                    lane_pairs[(exit_lane, entry_lane)] = None
        return lane_pairs

    def _fulfill_intersection_with_single_length(self, lane_pairs):
        radius_candidates = [5.0, 5.5, 6.0, 4.5, 6.5, 7.0]
        for radius in radius_candidates:
            try:
                lane_pairs_copy = lane_pairs.copy()
                return self._fulfill_intersections_with_circle_of_radius(radius, lane_pairs)
            except JunctionNotSatisfied:
                pass
        raise JunctionNotSatisfied()

    def _fulfill_intersections_with_circle_of_radius(self, radius, lane_pairs):
        return self._create_lane_intersections(radius, lane_pairs).values()

    def _create_lane_intersections(self, radius, lane_pairs, strict=True):
        intersections = OrderedDict()
        mapped_intersection_center = self.mapped_intersection_center()
        intersection_center = self.intersection_center()
        circle = Circle(intersection_center, radius)
        node = self._road_node
        for lane in self.lanes():
            path = lane.path_for(self._geometry_class)
            path_intersections = path.find_intersection(circle)

            indexed_intersections = OrderedDict()
            for intersection in path_intersections:
                point = intersection.closest_point_to(mapped_intersection_center)
                rounded_point = point.rounded_to(7)
                indexed_intersections[rounded_point] = point
            path_intersections = indexed_intersections.values()
            intersections[lane] = self._get_waypoints_for_intersections(lane, path_intersections)

        for (exit_lane, entry_lane) in lane_pairs.keys():
            exit_waypoint = None
            entry_waypoint = None
            try:
                exit_waypoint = self._get_exit_waypoint_from_intersections(intersections[exit_lane])
                entry_waypoint = self._get_entry_waypoint_from_intersections(intersections[entry_lane])
            # TODO: Improve this way of handling errors
            except RuntimeError as error:
                if strict:
                    raise JunctionNotSatisfied()

            if exit_waypoint and entry_waypoint:

                if exit_waypoint.center().almost_equal_to(entry_waypoint.center(), 5):
                    raise JunctionNotSatisfied()

                primitive = self._geometry_class.connect(exit_waypoint, entry_waypoint)

                if strict and (not primitive or not primitive.is_valid_path_connection()):
                    raise JunctionNotSatisfied()

                if primitive:
                    lane_pairs[(exit_lane, entry_lane)] = WaypointConnection(exit_waypoint, entry_waypoint, primitive)

        return lane_pairs

    def _get_waypoints_for_intersections(self, lane, points):
        new_waypoints = OrderedDict()
        waypoints = []
        for point in points:
            geometry = lane._lane_geometry(self._geometry_class)
            path = lane.path_for(self._geometry_class)
            waypoint = geometry.waypoint_at_point(point)
            if not waypoint:
                heading = path.heading_at_point(point)
                waypoint = Waypoint(lane, point, heading, self._road_node)
                new_waypoints[(lane, point.rounded_to(5))] = waypoint
            waypoints.append(waypoint)
        return waypoints

    def _get_exit_waypoint_from_intersections(self, intersections):
        for waypoint in intersections:
            heading_vector = waypoint.heading_vector()
            waypoint_to_intersection = self.mapped_intersection_center() - waypoint.center()
            if waypoint_to_intersection.norm_squared() < 1e-2:
                raise RuntimeError("Too close")
            angle = heading_vector.angle(waypoint_to_intersection)
            if abs(angle) < 90.0:
                return waypoint
        raise RuntimeError("Expecting to find intersection")

    def _get_entry_waypoint_from_intersections(self, intersections):
        for waypoint in intersections:
            heading_vector = waypoint.heading_vector()
            waypoint_to_intersection = self.mapped_intersection_center() - waypoint.center()
            if waypoint_to_intersection.norm_squared() < 1e-2:
                raise RuntimeError("Too close")
            angle = heading_vector.angle(waypoint_to_intersection)
            if abs(angle) >= 90.0:
                return waypoint
        raise RuntimeError("Expecting to find intersection")

    def _fulfill_intersection_with_adaptive_approach(self, lane_pairs):
        up = [x / 2.0 for x in range(10, 31)]  # [5.0, 5.5, 6.0, ...]
        down = [x / 2.0 for x in reversed(range(1, 10))]  # [4.5, 4.0, ...]
        radius_candidates = up + down
        lane_pairs_copy = lane_pairs.copy()

        for radius in radius_candidates:
            lane_pairs_copy = self._fill_missing_connections(radius, lane_pairs_copy, True)

        for radius in radius_candidates:
            lane_pairs_copy = self._fill_missing_connections(radius, lane_pairs_copy, False)

        connections = []

        for (exit_lane, entry_lane), connection in lane_pairs_copy.iteritems():
            if connection:
                connections.append(connection)
            else:
                logger.warn("Missing connection between {0} and {1}".format(exit_lane, entry_lane))

        return connections

    def _fill_missing_connections(self, radius, lane_pairs, strict):
        missing_connections = OrderedDict()
        for lanes, connection in lane_pairs.iteritems():
            if connection is None:
                missing_connections[lanes] = None

        if not missing_connections:
            return lane_pairs

        try:
            new_connections = self._create_lane_intersections(radius, missing_connections, strict)
            for lanes, connection in new_connections.iteritems():
                if connection is not None:
                    lane_pairs[lanes] = connection
            return lane_pairs

        except JunctionNotSatisfied:
            return lane_pairs
