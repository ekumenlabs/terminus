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

from geometry.arc import Arc
from geometry.point import Point
from geometry.line_segment import LineSegment
from geometry.path import Path

from waypoint import Waypoint
from lane_geometry import LaneGeometry


class LinesAndArcsGeometry(LaneGeometry):

    @classmethod
    def build_path_and_waypoints(cls, lane, mapped_centers):
        if lane.road_nodes_count() < 2:
            raise ValueError("At least two nodes are required to build a geometry")

        road_nodes = list(lane.road_nodes())
        is_circular = mapped_centers[road_nodes[0]].almost_equal_to(mapped_centers[road_nodes[-1]], 5)
        path = Path()
        waypoints = []

        previous_node = road_nodes.pop(0)
        previous_point = mapped_centers[previous_node]

        nodes_count = len(road_nodes)

        for index, node in enumerate(road_nodes):
            point = mapped_centers[node]
            is_last_node = index + 1 == nodes_count

            if is_last_node:
                if is_circular:
                    next_point = mapped_centers[road_nodes[0]]
                else:
                    next_point = None
            else:
                next_point = mapped_centers[road_nodes[index + 1]]

            if path.is_empty():
                previous_element_end_point = previous_point
            else:
                previous_element_end_point = path.element_at(-1).end_point()

            if next_point is None:
                element = LineSegment(previous_element_end_point, point)
                path.add_element(element)
                waypoints.append(cls._new_waypoint(lane, element, previous_node))
                waypoints.append(cls._new_waypoint(lane, element, road_nodes[-1], False))
            else:
                previous_vector = point - previous_point
                next_vector = next_point - point
                if previous_vector.is_collinear_with(next_vector):
                    element = LineSegment(previous_element_end_point, point)
                    path.add_element(element)
                    waypoints.append(cls._new_waypoint(lane, element, previous_node))
                    if is_last_node:
                        waypoints.append(cls._new_waypoint(lane, element, road_nodes[0], False))
                else:

                    inverted_previous_segment = LineSegment(point, previous_point)
                    real_inverted_previous_segment = LineSegment(point, previous_element_end_point)
                    next_segment = LineSegment(point, next_point)
                    if is_last_node:
                        real_next_segment = LineSegment(point, path.element_at(0).end_point())
                        delta = min(real_inverted_previous_segment.length(), real_next_segment.length(), 5)
                    else:
                        delta = min(real_inverted_previous_segment.length(), next_segment.length() / 2.0, 5)

                    previous_segment_new_end_point = real_inverted_previous_segment.point_at_offset(delta)
                    next_segment_new_start_point = next_segment.point_at_offset(delta)

                    previous_segment = LineSegment(previous_element_end_point, previous_segment_new_end_point)

                    # Try to avoid small segments
                    if previous_segment.length() < 0.25:
                        # `- 1e-10` to avoid length overflow due to floating point math
                        new_delta = delta + previous_segment.length() - 1e-10
                        if next_segment.length() > new_delta:
                            previous_segment_new_end_point = real_inverted_previous_segment.point_at_offset(new_delta)
                            next_segment_new_start_point = next_segment.point_at_offset(new_delta)
                            previous_segment = LineSegment(previous_element_end_point, previous_segment_new_end_point)

                    angle_between_vectors = previous_vector.angle(next_vector)
                    d2 = previous_segment_new_end_point.squared_distance_to(next_segment_new_start_point)
                    cos = math.cos(math.radians(angle_between_vectors))
                    radius = math.sqrt(d2 / (2.0 * (1.0 - cos)))

                    # If there should be no segment, just an arc. Use previous_element_end_point to
                    # avoid rounding errors and make a perfect overlap
                    if previous_segment.length() < 1e-8:
                        if path.not_empty():
                            heading = path.element_at(-1).end_heading()
                        else:
                            heading = inverted_previous_segment.inverted().start_heading()
                        connection_arc = Arc(previous_element_end_point, heading, radius, angle_between_vectors)
                        path.add_element(connection_arc)
                        waypoints.append(cls._new_waypoint(lane, connection_arc, node))

                        if not connection_arc.end_point().almost_equal_to(next_segment_new_start_point, 3):
                            raise RuntimeError("Expecting arc end {0} to match next segment entry point {1}".format(
                                               connection_arc.end_point(),
                                               next_segment_new_start_point))
                    else:
                        heading = inverted_previous_segment.inverted().start_heading()
                        connection_arc = Arc(previous_segment_new_end_point, heading, radius, angle_between_vectors)

                        path.add_element(previous_segment)
                        waypoints.append(cls._new_waypoint(lane, previous_segment, previous_node))

                        path.add_element(connection_arc)
                        waypoints.append(cls._new_waypoint(lane, connection_arc, node))

                        if not connection_arc.end_point().almost_equal_to(next_segment_new_start_point, 3):
                            raise RuntimeError("Expecting arc end {0} to match next segment entry point {1}".format(
                                               connection_arc.end_point(),
                                               next_segment_new_start_point))

                    if is_last_node:
                        if connection_arc.end_point().distance_to(path.element_at(1).start_point()) < 1e-8:
                            path.remove_first_element()
                            waypoints.pop(0)
                        else:
                            first_element = path.element_at(0)
                            new_first_element = LineSegment(connection_arc.end_point(), first_element.end_point())
                            path.replace_first_element(new_first_element)
                            waypoints[0] = cls._new_waypoint(lane, new_first_element, lane.road_nodes()[0])
                        waypoints.append(cls._new_waypoint(lane, connection_arc, road_nodes[0], False))

            previous_node = node
            previous_point = mapped_centers[previous_node]
        return (path, waypoints)

    @classmethod
    def connect(cls, exit_waypoint, entry_waypoint):
        if abs(exit_waypoint.heading() - entry_waypoint.heading()) < 1e-3:
            waypoints_angle = math.degrees(exit_waypoint.center().yaw(entry_waypoint.center()))
            if abs(exit_waypoint.heading() - waypoints_angle) < 1e-3:
                # Waypoints are in collinear lanes and can be connected by a line
                # segment with the same heading
                return LineSegment(exit_waypoint.center(), entry_waypoint.center())
            else:
                # Waypoints are in collinear lanes but have different offsets,
                # so they must be connected by an S-shaped path
                exit_line = exit_waypoint.defining_line()
                entry_line = entry_waypoint.defining_line()
                cutting_line = entry_line.perpendicular_line_at(entry_waypoint.center())

                delta_length = (exit_waypoint.center() - exit_line.intersection(cutting_line)).norm()
                segment_extension = delta_length / 5.0
                exit_extension = LineSegment.from_point_and_heading(exit_waypoint.center(),
                                                                    exit_waypoint.heading(),
                                                                    segment_extension)
                entry_extension = LineSegment.from_point_and_heading(entry_waypoint.center(),
                                                                     entry_waypoint.heading() + 180,
                                                                     segment_extension)
                connecting_segment = LineSegment(exit_extension.end_point(), entry_extension.end_point())
                connecting_segment = connecting_segment.extended_by(-segment_extension).inverted()
                connecting_segment = connecting_segment.extended_by(-segment_extension).inverted()

                start_arc = cls._build_arc(exit_waypoint.center(),
                                           exit_waypoint.heading(),
                                           connecting_segment.start_point(),
                                           connecting_segment.start_heading())
                end_arc = cls._build_arc(connecting_segment.end_point(),
                                         connecting_segment.end_heading(),
                                         entry_waypoint.center(),
                                         entry_waypoint.heading())
                path = Path()
                path.add_element(start_arc)
                path.add_element(connecting_segment)
                path.add_element(end_arc)
                return path

        else:
            exit_point = exit_waypoint.center()
            exit_line = exit_waypoint.defining_line()

            entry_point = entry_waypoint.center()
            entry_line = entry_waypoint.defining_line()

            intersection = exit_line.intersection(entry_line)

            exit_distance = exit_point.distance_to(intersection)
            entry_distance = entry_point.distance_to(intersection)

            path = None
            delta = abs(exit_distance - entry_distance)

            if delta > 1e-1:
                path = Path()
                if exit_distance > entry_distance:
                    end_point = exit_point + (exit_waypoint.heading_vector() * delta)
                    segment = LineSegment(exit_point, end_point)
                    arc = cls._build_arc(end_point, exit_waypoint.heading(), entry_point, entry_waypoint.heading())
                    path.add_element(segment)
                    path.add_element(arc)
                else:
                    start_point = entry_point - (entry_waypoint.heading_vector() * delta)
                    arc = cls._build_arc(exit_point, exit_waypoint.heading(), start_point, entry_waypoint.heading())
                    segment = LineSegment(arc.end_point(), entry_point)
                    path.add_element(arc)
                    path.add_element(segment)
                return path
            else:
                return cls._build_arc(exit_point, exit_waypoint.heading(), entry_point, entry_waypoint.heading())

    @classmethod
    def _build_arc(cls, start_point, start_heading, end_point, end_heading):

        angle_in_degrees = end_heading - start_heading
        d2 = end_point.squared_distance_to(start_point)
        cos = math.cos(math.radians(angle_in_degrees))
        radius = math.sqrt(d2 / (2 * (1 - cos)))

        # Keep the angle in the [-180, 180) range
        if angle_in_degrees >= 180:
            angle_in_degrees = angle_in_degrees - 360

        if angle_in_degrees < -180:
            angle_in_degrees = angle_in_degrees + 360

        return Arc(start_point, start_heading, radius, angle_in_degrees)
