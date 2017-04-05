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

from waypoint_connection import WaypointConnection


class Waypoint(object):

    def __init__(self, lane, geometry, center, heading, road_node):
        self._lane = lane
        self._geometry = geometry
        self._center = center
        self._heading = heading
        self._road_node = road_node
        self._in_connections = []
        self._out_connections = []

    def road_node(self):
        return self._road_node

    def center(self):
        return self._center

    def heading(self):
        return self._heading

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

    def road(self):
        return self._road

    def center(self):
        return self._center

    def add_connections_from(self, other_waypoint):
        for connection in other_waypoint.in_connections():
            self.add_in_connection(connection)

        for connection in other_waypoint.out_connections():
            self.add_out_connection(connection)

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and \
               (self._heading == other._heading) and \
               (self._center == other._center) and \
               (self._lane == other._lane) and \
               (self._geometry == other._geometry)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._lane, self._geometry, self._center, self._heading))

    def __repr__(self):
        return "Waypoint at {0}".format(self.center())
