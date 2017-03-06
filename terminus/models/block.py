"""
/*
 * Copyright (C) 2017 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
"""
from city_model import CityModel
from geometry.point import Point
from geometry.bounding_box import BoundingBox


class Block(CityModel):
    def __init__(self, origin, vertices, height=0.15, name=None):
        """
        Generates one block of a city with a shape defined by an array of
        vertices and the specified height.
        """
        super(Block, self).__init__(name)
        self.origin = origin
        self.height = height
        self.vertices = vertices

    @staticmethod
    def square(origin, size):
        """
        Generate a square block of the given size and in the given position.
        """
        w = size / 2.0
        vertices = [
            Point(w, w, 0),
            Point(-w, w, 0),
            Point(-w, -w, 0),
            Point(w, -w, 0)
        ]
        return Block(origin, vertices)

    def accept(self, generator):
        generator.start_block(self)
        generator.end_block(self)

    def bounding_box(self):
        box_list = map(lambda vertex: BoundingBox(vertex, vertex), self.vertices)
        box_base = BoundingBox.from_boxes(box_list).translate(self.origin)
        box_origin = box_base.origin
        box_corner = box_base.corner + Point(0, 0, self.height)
        return BoundingBox(box_origin, box_corner)
