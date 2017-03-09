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

from city_model import CityModel
from geometry.bounding_box import BoundingBox
from geometry.point import Point


class GroundPlane(CityModel):
    def __init__(self, size, origin, name=None):
        super(GroundPlane, self).__init__(name)
        self.size = size
        self.origin = origin

    def bounding_box(self):
        box_origin = Point(-self.size / 2.0, -self.size / 2.0)
        box_corner = Point(self.size / 2.0, self.size / 2.0)
        box = BoundingBox(box_origin, box_corner)
        return box.translate(self.origin)

    def accept(self, generator):
        generator.start_ground_plane(self)
        generator.end_ground_plane(self)
