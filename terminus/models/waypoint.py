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

from geometry.point import Point
from geometry.line import Line


class Waypoint(object):

    def __init__(self, lane, center, heading, road_node):
        self._lane = lane
        self._center = center
        self._heading = heading
        self._road_node = road_node
        self._in_connections = []
        self._out_connections = []

    def is_proxy(self):
        return False

    def lane(self):
        return self._lane

    def road_node(self):
        return self._road_node

    def center(self):
        return self._center

    def heading(self):
        return self._heading

    def heading_vector(self):
        heading_in_radians = math.radians(self.heading())
        x = math.cos(heading_in_radians)
        y = math.sin(heading_in_radians)
        return Point(x, y)

    def defining_line(self):
        return Line.from_points(self.center(), self.center() + self.heading_vector())

    def is_exit(self):
        return len(self._out_connections) > 0

    def is_entry(self):
        return len(self._in_connections) > 0

    def is_intersection(self):
        return self.is_exit() or self.is_entry()

    def add_in_connection(self, connection):
        self._in_connections.append(connection)

    def add_out_connection(self, connection):
        self._out_connections.append(connection)

    def in_connections(self):
        return self._in_connections

    def out_connections(self):
        return self._out_connections

    def center(self):
        return self._center

    def move_along(self, path, delta):
        current_offset = path.offset_for_point(self.center())
        new_offset = current_offset + delta
        new_offset = min(max(new_offset, 0), path.length() - 1e-7)
        self._center = path.point_at_offset(new_offset)
        self._heading = path.heading_at_offset(new_offset)

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and \
               (round(self._heading, 7) == round(other._heading, 7)) and \
               (self._center.rounded_to(7) == other._center.rounded_to(7)) and \
               (self._lane == other._lane)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._lane, self._center.rounded_to(7), round(self._heading, 7)))

    def __repr__(self):
        result = ""
        if self.is_entry():
            result += "[ENTRY] "
        if self.is_exit():
            result += "[EXIT] "
        return result + "Waypoint at {0}".format(self.center())
