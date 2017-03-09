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

from models.city import City
from models.street import Street
from models.trunk import Trunk
from models.block import Block
from models.building import Building
from models.ground_plane import GroundPlane

from builders.abstract_city_builder import AbstractCityBuilder

from procedural_city.vertex import *
from procedural_city.polygon2d import Polygon2D, Edge
from procedural_city.vertex_graph_to_roads_converter \
    import VertexGraphToRoadsConverter
from procedural_city.polygons_to_blocks_converter \
    import PolygonsToBlocksConverter
from procedural_city.pcg_runner import PcgRunner


import pickle


class ProceduralCityBuilder(AbstractCityBuilder):
    def __init__(self, verticesFilename=None, polygonsFilename=None, size=1500, pcg_runner=None):
        if pcg_runner is None:
            # Default runner
            self.pcg_runner = PcgRunner()
        else:
            self.pcg_runner = pcg_runner
        self.verticesFilename = verticesFilename
        self.polygonsFilename = polygonsFilename
        self.ratio = 100  # ratio between pcg and gazebo (1unit = 100m)
        self.pcg_runner.set_size(size / self.ratio)

    def get_city(self):
        city = City()

        # If no verticesFilename or polygonsFilename is specified,
        # generate new ones using procedural_city_generation
        if self.verticesFilename is None or self.polygonsFilename is None:
            self.pcg_runner.run()
            self.verticesFilename = self.pcg_runner.get_vertices_filename()
            self.polygonsFilename = self.pcg_runner.get_polygons_filename()

        vertices = self._parse_vertices_file()
        self._build_roads(city, vertices)

        polygons = self._parse_polygons_file()
        for block in self._build_blocks(polygons):
            city.add_block(block)

        city.set_ground_plane(GroundPlane(100, Point(0, 0, 0)))
        return city

    def _build_roads(self, city, vertex_list):
        vertex_mapping = {}
        for vertex in vertex_list:
            vertex_mapping[vertex] = GraphNode.from_vertex(vertex, self.ratio)
        for vertex, node in vertex_mapping.iteritems():
            node_neighbours = map(lambda vertex_neighbour: vertex_mapping[vertex_neighbour],
                                  vertex.neighbours)
            node.set_neighbours(node_neighbours)

        # 0.79 rad ~ 45 deg
        converter = VertexGraphToRoadsConverter(city, 0.79, vertex_mapping.values())
        converter.run()

    def _build_blocks(self, polygon_list):
        lot_polygons = filter(lambda polygon: polygon.is_lot(), polygon_list)
        block_polygons = []
        # Make sure the polygons overlap, as sometimes merging two polygons
        # leave holes due to rounding. We should later change this to initially
        # make a small buffer (e.g. 0.1) for merging purposes and then do the
        # final buffering to tweak overlapping with the street before building
        # the block.
        buffer_size = self.ratio * 0.06

        for polygon in lot_polygons:
            points = polygon.get_vertices_as_points(self.ratio)
            poly = Polygon(points).buffer(buffer_size, 16, 1, 1, 2)
            block_polygons.append(poly)

        converter = PolygonsToBlocksConverter(block_polygons)
        return converter.get_blocks()

    def _parse_vertices_file(self):
        original = 'procedural_city_generation.roadmap.Vertex'
        replace = 'builders.procedural_city.vertex'
        return self._parse_replacing(self.verticesFilename, original, replace)

    def _parse_polygons_file(self):
        original = 'procedural_city_generation.polygons.Polygon2D'
        replace = 'builders.procedural_city.polygon2d'
        return self._parse_replacing(self.polygonsFilename, original, replace)

    def _parse_replacing(self, filename, original_name, replace_name):
        with open(filename, 'rb') as f:
            # TODO: We should read/pre-process this lazily, no point in loading
            # the whole thing in memory.
            # Here we do the hacky conversion, from the Vertex class dumped in
            # procedural_city_generation package to our Vertex class use by
            # this builder.
            contents = f.read().replace(original_name, replace_name)
            return pickle.loads(contents)
