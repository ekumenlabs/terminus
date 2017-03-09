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
from road_node import RoadNode
from shapely.geometry import LineString
from waypoint import Waypoint


class RoadIntersectionNode(RoadNode):

    def __init__(self, center, name=None):
        super(RoadIntersectionNode, self).__init__(center, name)
        self.roads = []

    def is_intersection(self):
        return True

    def added_to(self, road):
        self._add_road(road)

    def removed_from(self, road):
        self.roads.remove(road)

    def involved_roads(self):
        return self.roads

    def _add_road(self, road):
        self.roads.append(road)

    def __repr__(self):
        return "RoadIntersectionNode @ " + str(self.center)
