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


class IntersectionNotFound(Exception):
    pass


class JunctionNotSatisfied(Exception):
    pass


class JunctionBuilder(object):

    def __init__(self, road_node, geometry_class):
        self._road_node = road_node
        self._geometry_class = geometry_class

    def lanes(self):
        return self._road_node.involved_lanes()

    def intersection_center(self):
        return self._road_node.center

    def add_connections_to_lanes(self):
        try:
            connections = self._fulfill_intersection_with_single_length()
        except JunctionNotSatisfied:
            connections = self._fulfill_intersection_with_adaptive_approach()

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

    def _fulfill_intersection_with_adaptive_approach(self):
        up = [x / 2.0 for x in range(10, 31)]  # [5.0, 5.5, 6.0, ...]
        down = [x / 2.0 for x in reversed(range(1, 10))]  # [4.5, 4.0, ...]
        radius_candidates = up + down
        intersections = OrderedDict()

        for radius in radius_candidates:
            try:
                intersections = self._create_lane_intersections_mapping(radius)
            except IntersectionNotFound:
                pass
        if not intersections:
            raise JunctionNotSatisfied()

        waypoints = self._get_waypoints_for_intersections(intersections)
        exit_waypoints, entry_waypoints = self._split_exit_entry_waypoints(waypoints)

        lane_pairs = OrderedDict()

        for exit_waypoint in exit_waypoints:
            for entry_waypoint in entry_waypoints:
                if exit_waypoint.lane() is not entry_waypoint.lane():
                    if not exit_waypoint.lane() in lane_pairs:
                        lane_pairs[exit_waypoint.lane()] = OrderedDict()
                    lane_pairs[exit_waypoint.lane()][entry_waypoint.lane()] = None

        for radius in radius_candidates:
            self._fill_missing_connections(radius, lane_pairs, True)

        for radius in radius_candidates:
            self._fill_missing_connections(radius, lane_pairs, False)

        connections = []
        for exit_lane, record in lane_pairs.iteritems():
            for entry_lane, connection in record.iteritems():
                if not connection:
                    logger.warn("Connection not fulfilled {0} {1}".format(exit_lane, entry_lane))
                else:
                    connections.append(connection)

        return connections

    def _fill_missing_connections(self, radius, lane_pairs, strict):
        intersections = self._create_lane_intersections_mapping(radius, False)

        waypoints = self._get_waypoints_for_intersections(intersections)
        exit_waypoints, entry_waypoints = self._split_exit_entry_waypoints(waypoints)

        for index, exit_waypoint in enumerate(exit_waypoints):
            for exit_lane, record in lane_pairs.iteritems():
                for entry_lane, connection in record.iteritems():
                    if connection is not None:
                        if connection.start_waypoint() == exit_waypoint:
                            exit_waypoints[index] = connection.start_waypoint()

        for index, entry_waypoint in enumerate(entry_waypoints):
            for exit_lane, record in lane_pairs.iteritems():
                for entry_lane, connection in record.iteritems():
                    if connection is not None:
                        if connection.end_waypoint() == entry_waypoint:
                            entry_waypoints[index] = connection.end_waypoint()

        for exit_waypoint in exit_waypoints:
            for entry_waypoint in entry_waypoints:
                if exit_waypoint.lane() is not entry_waypoint.lane() and \
                   lane_pairs[exit_waypoint.lane()][entry_waypoint.lane()] is None:

                    if not exit_waypoint.center().almost_equal_to(entry_waypoint.center(), 5):
                        primitive = self._geometry_class.connect(exit_waypoint, entry_waypoint)

                        if primitive.is_valid_path_connection() or not strict:
                            connection = WaypointConnection(exit_waypoint, entry_waypoint, primitive)
                            lane_pairs[exit_waypoint.lane()][entry_waypoint.lane()] = connection

    def _fulfill_intersection_with_single_length(self):
        radius_candidates = [5.0, 5.5, 6.0, 4.5, 6.5]
        for radius in radius_candidates:
            try:
                return self._fulfill_intersection_with_circle_of_radius(radius)
            except JunctionNotSatisfied:
                pass
        raise JunctionNotSatisfied()

    def _fulfill_intersection_with_circle_of_radius(self, radius):
        try:
            intersections = self._create_lane_intersections_mapping(radius)
        except IntersectionNotFound:
            raise JunctionNotSatisfied()

        waypoints = self._get_waypoints_for_intersections(intersections)
        exit_waypoints, entry_waypoints = self._split_exit_entry_waypoints(waypoints)

        connections = []

        for exit_waypoint in exit_waypoints:
            for entry_waypoint in entry_waypoints:
                if exit_waypoint.lane() is not entry_waypoint.lane():

                    if exit_waypoint.center().almost_equal_to(entry_waypoint.center(), 5):
                        raise JunctionNotSatisfied()

                    primitive = self._geometry_class.connect(exit_waypoint, entry_waypoint)

                    if not primitive or not primitive.is_valid_path_connection():
                        raise JunctionNotSatisfied()

                    connections.append(WaypointConnection(exit_waypoint, entry_waypoint, primitive))

        return connections

    def _create_lane_intersections_mapping(self, radius, check_count=True):
        lane_intersections = OrderedDict()
        intersection_center = self.intersection_center()
        circle = Circle(intersection_center, radius)
        node = self._road_node
        for lane in self.lanes():
            path = lane.path_for(self._geometry_class)
            path_intersections = path.find_intersection(circle)

            if (path.starts_on(intersection_center) and path.ends_on(intersection_center)) or \
               (not path.starts_on(intersection_center) and not path.ends_on(intersection_center)):
                expected_intersections = 2
            else:
                expected_intersections = 1

            indexed_intersections = OrderedDict()
            for intersection in path_intersections:
                point = intersection.closest_point_to(intersection_center)
                rounded_point = point.rounded_to(7)
                indexed_intersections[rounded_point] = point
            path_intersections = indexed_intersections.values()
            if check_count and (len(path_intersections) is not expected_intersections):
                raise IntersectionNotFound("Intersections mismatch. Expecting {0} but found {1}".format(expected_intersections, path_intersections))
            lane_intersections[lane] = path_intersections
        return lane_intersections

    def _get_waypoints_for_intersections(self, intersection_points):
        new_waypoints = OrderedDict()
        waypoints = []
        for lane, points in intersection_points.iteritems():
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

    def _split_exit_entry_waypoints(self, waypoints):
        exit_waypoints = []
        entry_waypoints = []
        for waypoint in waypoints:
            heading_vector = waypoint.heading_vector()
            waypoint_to_intersection = self.intersection_center() - waypoint.center()
            angle = heading_vector.angle(waypoint_to_intersection)
            if abs(angle) < 90.0:
                exit_waypoints.append(waypoint)
            else:
                entry_waypoints.append(waypoint)
        return (exit_waypoints, entry_waypoints)
