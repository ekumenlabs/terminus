from shapely.geometry import Polygon
from geometry.point import Point

from models.city import City
from models.street import Street
from models.trunk import Trunk
from models.block import Block
from models.building import Building
from models.ground_plane import GroundPlane

from procedural_city.vertex import *
from procedural_city.polygon2d import Polygon2D, Edge
from procedural_city.vertex_graph_to_roads_converter \
    import VertexGraphToRoadsConverter
from procedural_city.polygons_to_blocks_converter \
    import PolygonsToBlocksConverter

import pickle

import os
import sys
import subprocess

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProceduralCityBuilder(object):
    def __init__(self, verticesFilename=None, polygonsFilename=None, size=1500):
        self.verticesFilename = verticesFilename
        self.polygonsFilename = polygonsFilename
        self.ratio = 100  # ratio between pcg and gazebo (1unit = 100m)
        self.size = size

    def get_city(self):
        city = City()

        # If no verticesFilename or polygonsFilename is specified,
        # generate new ones using procedural_city_generation
        if self.verticesFilename is None or self.polygonsFilename is None:
            self._generate_procedural_city()

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

    def _generate_procedural_city(self):
        ''' Generate city using the procedural_city_generation library '''
        this_path = os.path.realpath(__file__)
        pcg_path = os.path.join(os.path.dirname(os.path.dirname(this_path)),
                                'procedural_city_generation')

        pcg_run = 'python {0}/UI.py'.format(pcg_path)

        # Configure roadmap parameters
        command_string = '{0} roadmap --configure plot False '\
            'border_x {1} border_y {1}'
        command = command_string.format(pcg_run, int(self.size / self.ratio))

        self._pcg_run_command(command)

        # Generate roadmap
        command = '{0} roadmap run'.format(pcg_run)
        self._pcg_run_command(command)

        # Configure polygons parameters
        command = '{0} polygons --configure plotbool False'.format(pcg_run)
        self._pcg_run_command(command)

        # Generate polygons
        command = '{0} polygons run'.format(pcg_run)
        self._pcg_run_command(command)

        self.temp_path = os.path.join(pcg_path,
                                      'procedural_city_generation/temp/')

        self.verticesFilename = os.path.join(self.temp_path, 'mycity')
        self.polygonsFilename = os.path.join(self.temp_path,
                                             'mycity_polygons.txt')

    def _pcg_run_command(self, command):

        with open(os.devnull, "w") as f:
            result = subprocess.call(command.split(),
                                     stdout=f,
                                     stderr=subprocess.STDOUT)

        if result == 0:
            logger.debug("Command '{0}' executed succesfully".format(command))
        else:
            logger.fatal("Command '{0}' failed to execute".format(command))
            sys.exit(1)
