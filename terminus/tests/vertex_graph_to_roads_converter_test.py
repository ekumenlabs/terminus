import unittest
from builders.procedural_city.vertex_graph_to_roads_converter import VertexGraphToRoadsConverter
from builders.procedural_city.vertex import Vertex
from geometry.point import Point
from models.road import Street, Trunk

class VertexGraphToRoadsConverterTest(unittest.TestCase):

    def setUp(self):
        self.converter = VertexGraphToRoadsConverter([])

    def test_get_roads_one_aligned_segment(self):
        """
        (0,0)--(1,0)
        """
        v1 = Vertex(Point(0,0))
        v2 = Vertex(Point(1,0))
        v1.neighbours.append(v2)
        v2.neighbours.append(v1)
        self.converter = VertexGraphToRoadsConverter([v1, v2])
        roads = self.converter.get_roads()
        self.assertEqual(len(roads), 1)
        expected_road = Street()
        expected_road.add_point(Point(0,0))
        expected_road.add_point(Point(1,0))
        self.assertEqual(roads[0], expected_road)

    def test_get_roads_one_not_aligned_segment(self):
        """
        (0,0)--(1,1)
        Event though the angles don't match (45deg), the road is built as there
        is only a single possible path.
        """
        v1 = Vertex(Point(0,0))
        v2 = Vertex(Point(1,1))
        v1.neighbours.append(v2)
        v2.neighbours.append(v1)
        self.converter = VertexGraphToRoadsConverter([v1, v2])
        roads = self.converter.get_roads()
        self.assertEqual(len(roads), 1)
        expected_road = Street()
        expected_road.add_point(Point(0,0))
        expected_road.add_point(Point(1,1))
        self.assertEqual(roads[0], expected_road)


    def test_get_roads_multiple_aligned_segments(self):
        """
        (0,0)--(1,0)--(5,1)--(9,3)
        """
        v1 = Vertex(Point(0,0))
        v2 = Vertex(Point(1,0))
        v3 = Vertex(Point(5,1))
        v4 = Vertex(Point(9,3))
        v1.neighbours.append(v2)
        v2.neighbours.append(v1)
        v2.neighbours.append(v3)
        v3.neighbours.append(v2)
        v3.neighbours.append(v4)
        v4.neighbours.append(v3)
        self.converter = VertexGraphToRoadsConverter([v1, v2, v3, v4])
        roads = self.converter.get_roads()
        self.assertEqual(len(roads), 1)
        expected_road = Street()
        expected_road.add_point(Point(0,0))
        expected_road.add_point(Point(1,0))
        expected_road.add_point(Point(5,1))
        expected_road.add_point(Point(9,3))
        self.assertEqual(roads[0], expected_road)

    def test_get_roads_multiple_non_aligned_segments(self):
        """
        (0,0)--(1,0)--(5,1)--(6,2)
        Note that the last 2 segments have a 45deg angle
        """
        v1 = Vertex(Point(0,0))
        v2 = Vertex(Point(1,0))
        v3 = Vertex(Point(5,1))
        v4 = Vertex(Point(6,2))
        v1.neighbours.append(v2)
        v2.neighbours.append(v1)
        v2.neighbours.append(v3)
        v3.neighbours.append(v2)
        v3.neighbours.append(v4)
        v4.neighbours.append(v3)
        self.converter = VertexGraphToRoadsConverter([v1, v2, v3, v4])
        roads = self.converter.get_roads()
        self.assertEqual(len(roads), 2)
        expected_roads = [Street(), Street()]
        expected_roads[0].add_point(Point(0,0))
        expected_roads[0].add_point(Point(1,0))
        expected_roads[0].add_point(Point(5,1))
        expected_roads[1].add_point(Point(6,2))
        expected_roads[1].add_point(Point(5,1))
        self.assertEqual(roads, expected_roads)

    def test_get_roads_multiple_independent_segments(self):
        """
        (0,0)--(1,0)--(6,1)
        (2,5)--(3,4)
        """
        v1 = Vertex(Point(0,0))
        v2 = Vertex(Point(1,0))
        v3 = Vertex(Point(6,1))
        v4 = Vertex(Point(2,5))
        v5 = Vertex(Point(3,4))
        v1.neighbours.append(v2)
        v2.neighbours.append(v1)
        v2.neighbours.append(v3)
        v3.neighbours.append(v2)
        v4.neighbours.append(v5)
        v5.neighbours.append(v4)
        self.converter = VertexGraphToRoadsConverter([v1, v2, v3, v4, v5])
        roads = self.converter.get_roads()
        self.assertEqual(len(roads), 2)
        expected_roads = [Street(), Street()]
        expected_roads[0].add_point(Point(0,0))
        expected_roads[0].add_point(Point(1,0))
        expected_roads[0].add_point(Point(6,1))
        expected_roads[1].add_point(Point(2,5))
        expected_roads[1].add_point(Point(3,4))
        self.assertEqual(roads, expected_roads)


    def test_get_roads_V_type(self):
        """
        (0,0)--(3,1)
          |----(3,-1)
        """
        v1 = Vertex(Point(0,0))
        v2 = Vertex(Point(3,1))
        v3 = Vertex(Point(3,-1))
        v1.neighbours.append(v2)
        v1.neighbours.append(v3)
        v2.neighbours.append(v1)
        v3.neighbours.append(v1)
        self.converter = VertexGraphToRoadsConverter([v1, v2, v3])
        roads = self.converter.get_roads()
        self.assertEqual(len(roads), 2)
        expected_roads = [Street(), Street()]
        expected_roads[1].add_point(Point(3,-1))
        expected_roads[1].add_point(Point(0,0))
        expected_roads[0].add_point(Point(3,1))
        expected_roads[0].add_point(Point(0,0))
        self.assertEqual(roads, expected_roads)

    def test_get_roads_L_type(self):
        """
        (0,0)--(1,0)--(6,1)
                  |---(6,6)
        Note that (6,6) is discarded since the angle is greater than 15deg
        """
        v1 = Vertex(Point(0,0))
        v2 = Vertex(Point(1,0))
        v3 = Vertex(Point(6,1))
        v4 = Vertex(Point(6,6))
        v1.neighbours.append(v2)
        v2.neighbours.append(v1)
        v2.neighbours.append(v3)
        v2.neighbours.append(v4)
        v3.neighbours.append(v2)
        v4.neighbours.append(v2)
        self.converter = VertexGraphToRoadsConverter([v1, v2, v3, v4])
        roads = self.converter.get_roads()
        self.assertEqual(len(roads), 2)
        expected_roads = [Street(), Street()]
        expected_roads[0].add_point(Point(0,0))
        expected_roads[0].add_point(Point(1,0))
        expected_roads[0].add_point(Point(6,1))
        expected_roads[1].add_point(Point(6,6))
        expected_roads[1].add_point(Point(1,0))
        self.assertEqual(roads, expected_roads)

    def test_get_roads_Y_type(self):
        """
        (0,0)--(1,0)--(6,1)
                  |---(6,-0.8)
        Note that (6,1) is discarded only because (6,-0.8) is a better candidate,
        but both are eligible
        """
        v1 = Vertex(Point(0,0))
        v2 = Vertex(Point(1,0))
        v3 = Vertex(Point(6,1))
        v4 = Vertex(Point(6,-0.8))
        v1.neighbours.append(v2)
        v2.neighbours.append(v1)
        v2.neighbours.append(v3)
        v2.neighbours.append(v4)
        v3.neighbours.append(v2)
        v4.neighbours.append(v2)
        self.converter = VertexGraphToRoadsConverter([v1, v2, v3, v4])
        roads = self.converter.get_roads()
        self.assertEqual(len(roads), 2)
        expected_roads = [Street(), Street()]
        expected_roads[0].add_point(Point(0,0))
        expected_roads[0].add_point(Point(1,0))
        expected_roads[0].add_point(Point(6,-0.8))
        expected_roads[1].add_point(Point(6,1))
        expected_roads[1].add_point(Point(1,0))
        self.assertEqual(roads, expected_roads)

    def test_get_roads_matrix_distribution(self):
        """
        (0,2)--(1,2)--(2,2)
          |      |      |
        (0,1)--(1,1)--(2,1)
          |      |      |
        (0,0)--(1,0)--(2,0)
        """
        v1 = Vertex(Point(0,0))
        v2 = Vertex(Point(1,0))
        v3 = Vertex(Point(2,0))

        v4 = Vertex(Point(0,1))
        v5 = Vertex(Point(1,1))
        v6 = Vertex(Point(2,1))

        v7 = Vertex(Point(0,2))
        v8 = Vertex(Point(1,2))
        v9 = Vertex(Point(2,2))

        v1.neighbours.append(v2)
        v1.neighbours.append(v4)

        v2.neighbours.append(v1)
        v2.neighbours.append(v5)
        v2.neighbours.append(v3)

        v3.neighbours.append(v2)
        v3.neighbours.append(v6)

        v4.neighbours.append(v1)
        v4.neighbours.append(v5)
        v4.neighbours.append(v7)

        v5.neighbours.append(v2)
        v5.neighbours.append(v4)
        v5.neighbours.append(v6)
        v5.neighbours.append(v8)

        v6.neighbours.append(v3)
        v6.neighbours.append(v5)
        v6.neighbours.append(v9)

        v7.neighbours.append(v4)
        v7.neighbours.append(v8)

        v8.neighbours.append(v7)
        v8.neighbours.append(v5)
        v8.neighbours.append(v9)

        v9.neighbours.append(v6)
        v9.neighbours.append(v8)

        self.converter = VertexGraphToRoadsConverter([v1, v2, v3, v4, v5, v6, v7, v8, v9])
        roads = self.converter.get_roads()
        self.assertEqual(len(roads), 6)
        expected_roads = [Street(), Street(), Street(), Street(), Street(), Street()]
        expected_roads[0].add_point(Point(0,0))
        expected_roads[0].add_point(Point(0,1))
        expected_roads[0].add_point(Point(0,2))

        expected_roads[1].add_point(Point(0,0))
        expected_roads[1].add_point(Point(1,0))
        expected_roads[1].add_point(Point(2,0))

        expected_roads[2].add_point(Point(1,0))
        expected_roads[2].add_point(Point(1,1))
        expected_roads[2].add_point(Point(1,2))

        expected_roads[3].add_point(Point(2,0))
        expected_roads[3].add_point(Point(2,1))
        expected_roads[3].add_point(Point(2,2))

        expected_roads[4].add_point(Point(0,1))
        expected_roads[4].add_point(Point(1,1))
        expected_roads[4].add_point(Point(2,1))

        expected_roads[5].add_point(Point(0,2))
        expected_roads[5].add_point(Point(1,2))
        expected_roads[5].add_point(Point(2,2))

        self.assertEqual(roads, expected_roads)
