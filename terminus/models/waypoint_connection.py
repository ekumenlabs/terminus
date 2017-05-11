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

from geometry.path import Path
from waypoint import Waypoint


class WaypointConnection(object):

    def __init__(self, start_waypoint, end_waypoint, primitive):
        self._start_waypoint = start_waypoint
        self._end_waypoint = end_waypoint
        self._primitive = primitive
        self._waypoints = self._create_waypoints_collection()

    def start_waypoint(self):
        return self._start_waypoint

    def end_waypoint(self):
        return self._end_waypoint

    def waypoints(self):
        return self._waypoints

    def intermediate_waypoints(self):
        return self._waypoints[1:-1]

    def primitive(self):
        return self._primitive

    def connects_same_lanes(self, start_waypoint, end_waypoint):
        return self.start_waypoint().lane() is start_waypoint.lane() and \
            self.end_waypoint().lane() is end_waypoint.lane()

    def waypoint_for(self, lane):
        if self._start_waypoint.lane() is lane:
            return self._start_waypoint
        elif self._end_waypoint.lane() is lane:
            return self._end_waypoint
        else:
            raise RuntimeError("No lane matching")

    def _create_waypoints_collection(self):
        waypoints = [self.start_waypoint()]
        if isinstance(self.primitive(), Path):
            lane = self.start_waypoint().lane()
            road_node = self.start_waypoint().road_node()
            for element in self.primitive():
                new_waypoint = Waypoint(lane, element.end_point(), element.end_heading(), road_node)
                waypoints.append(new_waypoint)
            waypoints.pop(-1)
        waypoints.append(self.end_waypoint())
        return waypoints

    def __repr__(self):
        return "WaypointConnection({0}, {1}, {2})".format(self._start_waypoint, self._end_waypoint, self._primitive)
