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
from geometry.point import Point
from geometry.bounding_box import BoundingBox


# TODO: separate concepts of origin and translation vector for the pose.
class Building(CityModel):
    def __init__(self, origin, vertices, height=10, name=None):
        """
        Generates a building with a base shape given by the vertices list
        and extruded the given height, located at position 'origin'.
        """
        super(Building, self).__init__(name)
        self.origin = origin
        self.vertices = vertices
        self.height = height

    @staticmethod
    def square(origin, size, height):
        """
        Generate a square building of the given lateral size, height and
        centered in the given position.
        """
        w = size / 2.0
        vertices = [
            Point(w, w, 0),
            Point(-w, w, 0),
            Point(-w, -w, 0),
            Point(w, -w, 0)
        ]
        return Building(origin, vertices, height)

    def accept(self, generator):
        generator.start_building(self)
        generator.end_building(self)

    def bounding_box(self):
        box_list = map(lambda vertex: BoundingBox(vertex, vertex), self.vertices)
        base_box = BoundingBox.from_boxes(box_list).translate(self.origin)
        box_origin = base_box.origin
        box_corner = base_box.corner + Point(0, 0, self.height)
        return BoundingBox(box_origin, box_corner)
