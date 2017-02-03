import unittest
import mock
import numpy as np
from builders.procedural_city_builder import ProceduralCityBuilder
from builders.procedural_city.vertex import *
from builders.procedural_city.polygon2d import Polygon2D, Edge


class PcgRunnerTest(unittest.TestCase):

    def test_run(self):
        pcg_runner_mock = mock.Mock()
        builder = ProceduralCityBuilder(pcg_runner=pcg_runner_mock)
        edges = np.array([[0, 0], [1, 1], [2, 2]])
        polygon = Polygon2D(edges, "lot")
        builder._parse_polygons_file = mock.Mock(return_value=[polygon])
        vertex1 = Vertex([0, 0])
        vertex2 = Vertex([1, 1])
        builder._parse_vertices_file = mock.Mock(return_value=[vertex1, vertex2])
        builder.get_city()
        pcg_runner_mock.set_size.assert_called()
        pcg_runner_mock.run.assert_called()
        pcg_runner_mock.get_vertices_filename.assert_called()
        pcg_runner_mock.get_polygons_filename.assert_called()
