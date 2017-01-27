import unittest
import mock
import numpy as np
from builders.procedural_city_builder import ProceduralCityBuilder
from builders.procedural_city.vertex import *
from builders.procedural_city.polygon2d import Polygon2D, Edge
from geometry.point import Point

class PcgRunnerTest(unittest.TestCase):

    def test_run(self):
        pcg_runner = mock.Mock()
        builder = ProceduralCityBuilder(pcg_runner=pcg_runner)
        edges = np.array([[0, 0], [1, 1], [2, 2]])
        polygon = Polygon2D(edges)
        builder._parse_polygons_file = mock.Mock(return_value=[polygon, polygon])
        vertex = Vertex([0, 0])
        builder._parse_vertices_file = mock.Mock(return_value=[vertex, vertex])
        builder.get_city()
