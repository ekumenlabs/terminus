from shapely.geometry import Point, Polygon

from models.city import City
from models.street import Street
from models.trunk import Trunk
from models.block import Block
from models.building import Building
from models.ground_plane import GroundPlane

from procedural_city.vertex import Vertex
from procedural_city.polygon2d import Polygon2D, Edge
from procedural_city.vertex_graph_to_roads_converter \
    import VertexGraphToRoadsConverter
from procedural_city.polygons_to_blocks_converter \
    import PolygonsToBlocksConverter

import pickle


class ProceduralCityBuilder(object):
    def __init__(self, verticesFilename, polygonsFilename):
        self.verticesFilename = verticesFilename
        self.polygonsFilename = polygonsFilename

    def get_city(self):
        city = City()
        ratio = 100

        vertices = self._parse_vertices_file()
        for road in self._build_roads(vertices, ratio):
            city.add_road(road)

        polygons = self._parse_polygons_file()
        for block in self._build_blocks(polygons, ratio):
            city.add_block(block)

        city.set_ground_plane(GroundPlane(100, Point(0, 0, 0)))
        return city

    def _build_roads(self, vertex_list, ratio):
        # Convert them to Gazebo coordinates. This is definitely ugly, as
        # we are changing the type in vertex.coords, we should revisit.
        for vertex in vertex_list:
            vertex.coords = Point(vertex.coords[0]*ratio,
                                  vertex.coords[1]*ratio,
                                  0)
        # 0.79 rad ~ 45 deg
        converter = VertexGraphToRoadsConverter(0.79, vertex_list)
        return converter.get_roads()

    def _build_blocks(self, polygon_list, ratio):
        lot_polygons = filter(lambda polygon: polygon.is_lot(), polygon_list)
        block_polygons = []
        # Make sure the polygons overlap, as sometimes merging two polygons
        # leave holes due to rounding. We should later change this to initially
        # make a small buffer (e.g. 0.1) for merging purposes and then do the
        # final buffering to tweak overlapping with the street before building
        # the block.
        buffer_size = ratio * 0.06

        for polygon in lot_polygons:
            points = polygon.get_vertices_as_points(ratio)
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
