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
from geometry.bounding_box import BoundingBox


class RoadNode(object):
    def __init__(self, center, name=None):
        self.center = center
        self.name = name

    def bounding_box(self, width):
        if width < 0:
            raise ValueError('width should be a non negative number')
        box_origin = Point(self.center.x - width / 2, self.center.y - width / 2)
        box_corner = Point(self.center.x + width / 2, self.center.y + width / 2)
        return BoundingBox(box_origin, box_corner)

    @classmethod
    def on(cls, *args, **kwargs):
        return cls(Point(*args, **kwargs))

    def is_intersection(self):
        raise NotImplementedError()

    def added_to(self, road):
        raise NotImplementedError()

    def removed_from(self, road):
        raise NotImplementedError()

    def involved_roads(self):
        raise NotImplementedError()

    def involved_lanes(self):
        lanes = []
        for road in self.involved_roads():
            lanes.extend(road.lanes())
        return lanes

    def involved_roads_except(self, target_road):
        return filter(lambda road: road is not target_road, self.involved_roads())

    def involved_lanes_except_all_in(self, target_road):
        other_roads = self.involved_roads_except(target_road)
        other_lanes = []
        for other_road in other_roads:
            other_lanes.extend(other_road.lanes())
        return other_lanes

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.center == other.center

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.center))
