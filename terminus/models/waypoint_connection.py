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


class WaypointConnection(object):

    def __init__(self, start_waypoint, end_waypoint, primitive):
        self._start_waypoint = start_waypoint
        self._end_waypoint = end_waypoint
        self._primitive = primitive

    def start_waypoint(self):
        return self._start_waypoint

    def end_waypoint(self):
        return self._end_waypoint

    def primitive(self):
        return self._primitive
