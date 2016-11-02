import unittest
from builders.procedural_city.vertex_graph_to_roads_converter \
    import VertexGraphToRoadsConverter
from builders.procedural_city.vertex import Vertex
from shapely.geometry import Point
from models.street import Street
from models.trunk import Trunk


class VertexGraphToRoadsConverterTest(unittest.TestCase):

    def test_get_roads_one_aligned_segment(self):
        """
        (0,0)--(1,0)
        """
        v1 = Vertex(Point(0, 0))
        v2 = Vertex(Point(1, 0))

        self._connect(v1, v2)

        self.converter = VertexGraphToRoadsConverter(0.25, [v1, v2])
        roads = self.converter.get_roads()
        expected_roads = [
            Street.from_points([Point(0, 0), Point(1, 0)])
        ]
        self.assertItemsEqual(roads, [])

    def test_get_roads_one_not_aligned_segment(self):
        """
        (0,0)--(1,1)
        Event though the angles don't match (45deg), the road is built as there
        is only a single possible path.
        """
        v1 = Vertex(Point(0, 0))
        v2 = Vertex(Point(1, 1))

        self._connect(v1, v2)

        self.converter = VertexGraphToRoadsConverter(0.25, [v1, v2])
        roads = self.converter.get_roads()
        expected_roads = [
            Street.from_points([Point(0, 0), Point(1, 1)])
        ]
        self.assertItemsEqual(roads, expected_roads)

    def test_get_roads_multiple_aligned_segments(self):
        """
        (0,0)--(1,0)--(5,1)--(9,3)
        """
        v1 = Vertex(Point(0, 0))
        v2 = Vertex(Point(1, 0))
        v3 = Vertex(Point(5, 1))
        v4 = Vertex(Point(9, 3))

        self._connect(v1, v2)
        self._connect(v2, v3)
        self._connect(v3, v4)

        self.converter = VertexGraphToRoadsConverter(0.25, [v1, v2, v3, v4])
        roads = self.converter.get_roads()
        expected_roads = [
            Street.from_points(
                [Point(0, 0), Point(1, 0), Point(5, 1), Point(9, 3)])
        ]
        self.assertItemsEqual(roads, expected_roads)

    def test_get_roads_multiple_non_aligned_segments(self):
        """
        (0,0)--(1,0)--(5,1)--(6,2)
        Note that the last 2 segments have a 45deg angle
        """
        v1 = Vertex(Point(0, 0))
        v2 = Vertex(Point(1, 0))
        v3 = Vertex(Point(5, 1))
        v4 = Vertex(Point(6, 2))

        self._connect(v1, v2)
        self._connect(v2, v3)
        self._connect(v3, v4)

        self.converter = VertexGraphToRoadsConverter(0.25, [v1, v2, v3, v4])
        roads = self.converter.get_roads()
        expected_roads = [
            Street.from_points([Point(0, 0), Point(1, 0), Point(5, 1)]),
            Street.from_points([Point(6, 2), Point(5, 1)])
        ]
        self.assertItemsEqual(roads, expected_roads)

    def test_get_roads_multiple_independent_segments(self):
        """
        (0,0)--(1,0)--(6,1)
        (2,5)--(3,4)
        """
        v1 = Vertex(Point(0, 0))
        v2 = Vertex(Point(1, 0))
        v3 = Vertex(Point(6, 1))
        v4 = Vertex(Point(2, 5))
        v5 = Vertex(Point(3, 4))

        self._connect(v1, v2)
        self._connect(v2, v3)
        self._connect(v4, v5)

        self.converter = VertexGraphToRoadsConverter(
            0.25, [v1, v2, v3, v4, v5])
        roads = self.converter.get_roads()
        expected_roads = [
            Street.from_points([Point(0, 0), Point(1, 0), Point(6, 1)]),
            Street.from_points([Point(2, 5), Point(3, 4)])
        ]
        self.assertItemsEqual(roads, expected_roads)

    def test_get_roads_V_type(self):
        """
        (0,0)--(3,1)
          |----(3,-1)
        """
        v1 = Vertex(Point(0, 0))
        v2 = Vertex(Point(3, 1))
        v3 = Vertex(Point(3, -1))

        self._connect(v1, v2)
        self._connect(v1, v3)

        self.converter = VertexGraphToRoadsConverter(0.25, [v1, v2, v3])
        roads = self.converter.get_roads()
        expected_roads = [
            Street.from_points([Point(3, -1), Point(0, 0)]),
            Street.from_points([Point(3, 1), Point(0, 0)])
        ]
        self.assertItemsEqual(roads, expected_roads)

    def test_get_roads_L_type(self):
        """
        (0,0)--(1,0)--(6,1)
                  |---(6,6)
        Note that (6,6) is discarded since the angle is greater than 15deg
        """
        v1 = Vertex(Point(0, 0))
        v2 = Vertex(Point(1, 0))
        v3 = Vertex(Point(6, 1))
        v4 = Vertex(Point(6, 6))

        self._connect(v1, v2)
        self._connect(v2, v3)
        self._connect(v2, v4)

        self.converter = VertexGraphToRoadsConverter(0.25, [v1, v2, v3, v4])
        roads = self.converter.get_roads()
        expected_roads = [
            Street.from_points([Point(0, 0), Point(1, 0), Point(6, 1)]),
            Street.from_points([Point(6, 6), Point(1, 0)])
        ]
        self.assertItemsEqual(roads, expected_roads)

    def test_get_roads_Y_type(self):
        """
        (0,0)--(1,0)--(6,1)
                  |---(6,-0.8)
        Note that (6,1) is discarded only because (6,-0.8) is a better
        candidate, but both are eligible
        """
        v1 = Vertex(Point(0, 0))
        v2 = Vertex(Point(1, 0))
        v3 = Vertex(Point(6, 1))
        v4 = Vertex(Point(6, -0.8))

        self._connect(v1, v2)
        self._connect(v2, v3)
        self._connect(v2, v4)

        self.converter = VertexGraphToRoadsConverter(0.25, [v1, v2, v3, v4])
        roads = self.converter.get_roads()
        expected_roads = [
            Street.from_points([Point(0, 0), Point(1, 0), Point(6, -0.8)]),
            Street.from_points([Point(6, 1), Point(1, 0)])
        ]
        self.assertItemsEqual(roads, expected_roads)

    def test_get_roads_matrix_distribution(self):
        """
        (0,2)--(1,2)--(2,2)
          |      |      |
        (0,1)--(1,1)--(2,1)
          |      |      |
        (0,0)--(1,0)--(2,0)
        """
        v1 = Vertex(Point(0, 0))
        v2 = Vertex(Point(1, 0))
        v3 = Vertex(Point(2, 0))

        v4 = Vertex(Point(0, 1))
        v5 = Vertex(Point(1, 1))
        v6 = Vertex(Point(2, 1))

        v7 = Vertex(Point(0, 2))
        v8 = Vertex(Point(1, 2))
        v9 = Vertex(Point(2, 2))

        self._connect(v1, v2)
        self._connect(v1, v4)
        self._connect(v2, v5)
        self._connect(v2, v3)
        self._connect(v3, v6)
        self._connect(v4, v5)
        self._connect(v4, v7)
        self._connect(v5, v6)
        self._connect(v5, v8)
        self._connect(v6, v9)
        self._connect(v7, v8)
        self._connect(v8, v9)

        self.converter = VertexGraphToRoadsConverter(
            0.25, [v1, v2, v3, v4, v5, v6, v7, v8, v9])
        roads = self.converter.get_roads()
        expected_roads = [
            Street.from_points([Point(0, 0), Point(0, 1), Point(0, 2)]),
            Street.from_points([Point(1, 0), Point(1, 1), Point(1, 2)]),
            Street.from_points([Point(2, 0), Point(2, 1), Point(2, 2)]),
            Street.from_points([Point(0, 0), Point(1, 0), Point(2, 0)]),
            Street.from_points([Point(0, 1), Point(1, 1), Point(2, 1)]),
            Street.from_points([Point(0, 2), Point(1, 2), Point(2, 2)])
        ]
        self.assertItemsEqual(roads, expected_roads)

    def _connect(self, v1, v2):
        """Make a bidirectional connection between two vertices"""
        v1.neighbours.append(v2)
        v2.neighbours.append(v1)
