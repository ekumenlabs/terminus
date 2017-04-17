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


class BoundingBox(object):

    def __init__(self, origin, corner):
        self.origin = origin
        self.corner = corner
        self._normalize()

    @classmethod
    def from_boxes(cls, box_list):
        if not box_list:
            raise ValueError("box_list can't be empty")
        whole_merge = box_list[0]
        for i in range(1, len(box_list)):
            whole_merge = whole_merge.merge(box_list[i])
        return whole_merge

    def __hash__(self):
        return hash(hash(origin), hash(corner))

    def __eq__(self, other):
        return self.origin == other.origin and self.corner == other.corner

    def includes_point(self, point):
        return (self.origin <= point) and (point <= self.corner)

    def merge(self, other):
        merge_origin = self.origin.min(other.origin)
        merge_corner = self.corner.max(other.corner)
        return BoundingBox(merge_origin, merge_corner)

    def translate(self, point):
        new_origin = self.origin + point
        new_corner = self.corner + point
        return BoundingBox(new_origin, new_corner)

    def width(self):
        return self.corner.x - self.origin.x

    def height(self):
        return self.corner.y - self.origin.y

    def _normalize(self):
        new_origin = self.origin.min(self.corner)
        new_corner = self.origin.max(self.corner)
        self.origin = new_origin
        self.corner = new_corner
