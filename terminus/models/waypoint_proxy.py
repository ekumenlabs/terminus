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


class WaypointProxy(object):

    def __init__(self, lane, geometry_builder, center, road_node):
        self._lane = lane
        self._geometry_builder = geometry_builder
        self._center = center
        self._road_node = road_node

    def is_proxy(self):
        return True

    def center(self):
        return self._center

    def road_node(self):
        return self._road_node

    def resolve(self):
        waypoints = self._lane.waypoints_using(self._geometry_builder)
        for waypoint in waypoints:
            if waypoint.center().rounded_to(7) == self.center().rounded_to(7) and \
               waypoint.road_node() == self.road_node():
                return waypoint
        raise RuntimeError("Could not resolve waypoint")

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and \
               (self._center.rounded_to(7) == other._center.rounded_to(7)) and \
               (self._lane == other._lane) and \
               (self._geometry_builder == other._geometry_builder)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._lane, self._geometry_builder, self._center.rounded_to(7)))

    def __repr__(self):
        return "WaypointProxy at {0}".format(self.center())
