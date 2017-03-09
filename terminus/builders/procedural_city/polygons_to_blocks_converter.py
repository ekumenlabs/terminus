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

from shapely.geometry import Polygon
from geometry.point import Point
from models.block import Block


class PolygonsToBlocksConverter(object):

    def __init__(self, polygons):
        self.polygons = polygons

    def get_blocks(self):
        reduced_polygons = self._reduce_adjacent_polygons(self.polygons)
        reduced_polygons = self._reduce_all_polygons(reduced_polygons)
        return map(self._polygon_to_block, reduced_polygons)

    def _polygon_to_block(self, polygon):
        """Create a Block based on a Shapely polygon"""
        points = list(Point(c[0], c[1]) for c in polygon.exterior.coords)
        return Block(Point(0, 0, 0), points)

    def _reduce_adjacent_polygons(self, polygons):
        """Adjacent lots that belong to the same block are quite likely to be
        consecutive. Reduce the list by merging contiguous polygons that
        overlap into a single one"""

        optimized_polygons = []
        current_polygon = polygons[0]

        for polygon in polygons:
            if current_polygon.intersects(polygon):
                current_polygon = current_polygon.union(polygon)
            else:
                optimized_polygons.append(current_polygon)
                current_polygon = polygon
        optimized_polygons.append(current_polygon)
        return optimized_polygons

    def _reduce_all_polygons(self, polygons):
        """This is the ugly one, as we are doing all-against-all comparisons.
        If performance becomes an issue, this is the place to improve"""

        one_more_iteration = True
        current_list = list(polygons)
        while one_more_iteration:
            one_more_iteration = False
            new_list = []
            while len(current_list) > 0:
                current_polygon = current_list.pop()
                remainder = []
                for polygon in current_list:
                    if current_polygon.intersects(polygon):
                        current_polygon = current_polygon.union(polygon)
                    else:
                        remainder.append(polygon)
                one_more_iteration = one_more_iteration or \
                    (len(remainder) < len(current_list))
                new_list.append(current_polygon)
                current_list = remainder
            current_list = new_list
        return new_list
