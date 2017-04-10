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

from geometry.line_segment import LineSegment
from geometry.arc import Arc
from path_geometry_builder import PathGeometryBuilder


class LinesAndArcsBuilder(PathGeometryBuilder):

    def connect_waypoints(self, exit_waypoint, entry_waypoint):
        if exit_waypoint.heading() == entry_waypoint.heading():
            return LineSegment(exit_waypoint.center(), entry_waypoint.center())
        else:
            angle_in_degrees = entry_waypoint.heading() - exit_waypoint.heading()
            d2 = entry_waypoint.center().squared_distance_to(exit_waypoint.center())
            cos = math.cos(math.radians(angle_in_degrees))
            radius = math.sqrt(d2 / (2 * (1 - cos)))

            # Keep the angle in the [-180, 180) range
            if angle_in_degrees >= 180:
                angle_in_degrees = angle_in_degrees - 360

            if angle_in_degrees < -180:
                angle_in_degrees = angle_in_degrees + 360

            return Arc(exit_waypoint.center(), exit_waypoint.heading(), radius, angle_in_degrees)

    def index_nodes(self, nodes):
        mapping = {}
        nodes = list(nodes)
        previous_node = nodes.pop(0)
        nodes_count = len(nodes)
        elements = []

        for index, node in enumerate(nodes):
            if index + 1 == nodes_count:
                next_node = None
            else:
                next_node = nodes[index + 1]

            if elements:
                previous_element_point = elements[-1].end_point()
            else:
                previous_element_point = previous_node.center

            if next_node is None:
                mapping[previous_node.center.rounded()] = previous_node
                mapping[node.center.rounded()] = node
            else:
                point = node.center
                previous_point = previous_node.center
                next_point = next_node.center
                previous_vector = point - previous_point
                next_vector = next_point - point
                # If they are collinear (given some tolerance)
                angle_between_vectors = previous_vector.angle(next_vector)
                if abs(angle_between_vectors) < 1e-5:
                    elements.append(LineSegment(previous_point, point))
                    mapping[previous_point.rounded()] = previous_node
                    mapping[point.rounded()] = node
                else:
                    inverted_previous_segment = LineSegment(point, previous_point)
                    next_segment = LineSegment(point, next_point)
                    delta = min(inverted_previous_segment.length() / 2.0, next_segment.length() / 2.0, 5)

                    previous_segment_new_end_point = inverted_previous_segment.point_at_offset(delta)
                    next_segment_new_start_point = next_segment.point_at_offset(delta)

                    previous_segment = LineSegment(previous_element_point, previous_segment_new_end_point)

                    d2 = previous_segment_new_end_point.squared_distance_to(next_segment_new_start_point)
                    cos = math.cos(math.radians(angle_between_vectors))
                    radius = math.sqrt(d2 / (2 * (1 - cos)))

                    # If there should be no segment, just an arc. Use previous_element_point to
                    # avoid rounding errors and make a perfect overlap
                    if previous_segment.length() < 1e-5:
                        connection_arc = Arc(previous_element_point, elements[-1].end_heading(), radius, angle_between_vectors)
                        elements.append(connection_arc)
                        mapping[connection_arc.start_point().rounded()] = node
                        mapping[connection_arc.end_point().rounded()] = node
                    else:
                        connection_arc = Arc(previous_segment_new_end_point, previous_segment.end_heading(), radius, angle_between_vectors)

                        elements.append(previous_segment)
                        mapping[previous_segment.start_point().rounded()] = previous_node

                        elements.append(connection_arc)
                        mapping[connection_arc.start_point().rounded()] = node
                        mapping[connection_arc.end_point().rounded()] = node

            previous_node = node
        return mapping

    def _build_geometry_from(self, points):
        points = list(points)
        elements = []
        previous_point = points.pop(0)
        points_count = len(points)

        for index, point in enumerate(points):
            if index + 1 == points_count:
                next_point = None
            else:
                next_point = points[index + 1]

            if elements:
                previous_element_point = elements[-1].end_point()
            else:
                previous_element_point = previous_point

            if next_point is None:
                elements.append(LineSegment(previous_element_point, point))
            else:
                previous_vector = point - previous_point
                next_vector = next_point - point
                # If they are collinear (given some tolerance)
                angle_between_vectors = previous_vector.angle(next_vector)
                if abs(angle_between_vectors) < 1e-5:
                    elements.append(LineSegment(previous_point, point))
                else:
                    inverted_previous_segment = LineSegment(point, previous_point)
                    next_segment = LineSegment(point, next_point)
                    delta = min(inverted_previous_segment.length() / 2.0, next_segment.length() / 2.0, 5)

                    previous_segment_new_end_point = inverted_previous_segment.point_at_offset(delta)
                    next_segment_new_start_point = next_segment.point_at_offset(delta)

                    previous_segment = LineSegment(previous_element_point, previous_segment_new_end_point)

                    d2 = previous_segment_new_end_point.squared_distance_to(next_segment_new_start_point)
                    cos = math.cos(math.radians(angle_between_vectors))
                    radius = math.sqrt(d2 / (2 * (1 - cos)))

                    # If there should be no segment, just an arc. Use previous_element_point to
                    # avoid rounding errors and make a perfect overlap
                    if previous_segment.length() < 1e-5:
                        connection_arc = Arc(previous_element_point, elements[-1].end_heading(), radius, angle_between_vectors)
                        elements.append(connection_arc)
                    else:
                        connection_arc = Arc(previous_segment_new_end_point, previous_segment.end_heading(), radius, angle_between_vectors)
                        elements.append(previous_segment)
                        elements.append(connection_arc)

            previous_point = point
        return elements
