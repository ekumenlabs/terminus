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

from geometry.line_segment import LineSegment

from path_geometry import PathGeometry


class PolylineBuilder(object):

    def __init__(self, control_points):
        if len(control_points) < 2:
            raise ValueError("Can't create a geometry from an empty path")
        self._control_points = control_points
        self._elements = self._build_geometry_from(self._control_points)

    def build_path_geometry(self):
        geometry = PathGeometry(self._elements)
        geometry.simplify()
        return geometry

    def index_nodes(self, nodes):
        node_mapping = dict((node.center.rounded(), node) for node in nodes)
        mapping = {}
        for element in self._elements:
            point = element.start_point().rounded()
            mapping[point] = node_mapping[point]
        missing_point = self._elements[-1].end_point().rounded()
        mapping[missing_point] = node_mapping[missing_point]
        return mapping

    def connect_waypoints(self, exit_waypoint, entry_waypoint):
        return LineSegment(exit_waypoint.center(), entry_waypoint.center())

    def _build_geometry_from(self, points):
        pairs = zip(points, points[1:])
        return map(lambda (p1, p2): LineSegment(p1, p2), pairs)
