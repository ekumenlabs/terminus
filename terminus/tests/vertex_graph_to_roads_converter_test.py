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
import unittest
from geometry.point import Point

from builders.procedural_city.vertex_graph_to_roads_converter \
    import VertexGraphToRoadsConverter
from builders.procedural_city.vertex import *
from models.road_simple_node import RoadSimpleNode
from models.road_intersection_node import RoadIntersectionNode
from models.street import Street
from models.trunk import Trunk
from models.city import City


class VertexGraphToRoadsConverterTest(unittest.TestCase):

    def setUp(self):
        self.city = City()

    def test_get_roads_one_aligned_segment(self):
        """
        (0,0)--(1,0)
        """
        n1 = GraphNode(Point(0, 0))
        n2 = GraphNode(Point(1, 0))

        self._connect(n1, n2)

        VertexGraphToRoadsConverter(self.city, 0.25, [n1, n2]).run()

        expected_roads = [
            Street.from_nodes([RoadSimpleNode.on(0, 0), RoadSimpleNode.on(1, 0)])
        ]
        self.assertItemsEqual(self.city.roads, expected_roads)

    def test_get_roads_one_not_aligned_segment(self):
        """
        (0,0)--(1,1)
        Event though the angles don't match (45deg), the road is built as there
        is only a single possible path.
        """
        n1 = GraphNode(Point(0, 0))
        n2 = GraphNode(Point(1, 1))

        self._connect(n1, n2)

        VertexGraphToRoadsConverter(self.city, 0.25, [n1, n2]).run()

        expected_roads = [
            Street.from_nodes([RoadSimpleNode.on(0, 0), RoadSimpleNode.on(1, 1)])
        ]
        self.assertItemsEqual(self.city.roads, expected_roads)

    def test_get_roads_multiple_aligned_segments(self):
        """
        (0,0)--(1,0)--(5,1)--(9,3)
        """
        n1 = GraphNode(Point(0, 0))
        n2 = GraphNode(Point(1, 0))
        n3 = GraphNode(Point(5, 1))
        n4 = GraphNode(Point(9, 3))

        self._connect(n1, n2)
        self._connect(n2, n3)
        self._connect(n3, n4)

        VertexGraphToRoadsConverter(self.city, 0.25, [n1, n2, n3, n4]).run()

        expected_roads = [
            Street.from_nodes([
                RoadSimpleNode.on(0, 0),
                RoadSimpleNode.on(1, 0),
                RoadSimpleNode.on(5, 1),
                RoadSimpleNode.on(9, 3)
            ])
        ]
        self.assertItemsEqual(self.city.roads, expected_roads)

    def test_get_roads_multiple_non_aligned_segments(self):
        """
        (0,0)--(1,0)--(5,1)--(6,2)
        Note that the last 2 segments have a 45deg angle
        """
        n1 = GraphNode(Point(0, 0))
        n2 = GraphNode(Point(1, 0))
        n3 = GraphNode(Point(5, 1))
        n4 = GraphNode(Point(6, 2))

        self._connect(n1, n2)
        self._connect(n2, n3)
        self._connect(n3, n4)

        VertexGraphToRoadsConverter(self.city, 0.25, [n1, n2, n3, n4]).run()

        intersection = RoadIntersectionNode.on(5, 1)
        expected_roads = [
            Street.from_nodes([RoadSimpleNode.on(0, 0), RoadSimpleNode.on(1, 0), intersection]),
            Street.from_nodes([RoadSimpleNode.on(6, 2), intersection])
        ]
        self.assertItemsEqual(self.city.roads, expected_roads)

    def test_get_roads_multiple_independent_segments(self):
        """
        (0,0)--(1,0)--(6,1)
        (2,5)--(3,4)
        """
        n1 = GraphNode(Point(0, 0))
        n2 = GraphNode(Point(1, 0))
        n3 = GraphNode(Point(6, 1))
        n4 = GraphNode(Point(2, 5))
        n5 = GraphNode(Point(3, 4))

        self._connect(n1, n2)
        self._connect(n2, n3)
        self._connect(n4, n5)

        VertexGraphToRoadsConverter(self.city, 0.25, [n1, n2, n3, n4, n5]).run()

        expected_roads = [
            Street.from_nodes([RoadSimpleNode.on(0, 0), RoadSimpleNode.on(1, 0), RoadSimpleNode.on(6, 1)]),
            Street.from_nodes([RoadSimpleNode.on(2, 5), RoadSimpleNode.on(3, 4)])
        ]
        self.assertItemsEqual(self.city.roads, expected_roads)

    def test_get_roads_V_type(self):
        """
        (0,0)--(3,1)
          |----(3,-1)
        """
        n1 = GraphNode(Point(0, 0))
        n2 = GraphNode(Point(3, 1))
        n3 = GraphNode(Point(3, -1))

        self._connect(n1, n2)
        self._connect(n1, n3)

        VertexGraphToRoadsConverter(self.city, 0.25, [n1, n2, n3]).run()
        intersection = RoadIntersectionNode.on(0, 0)
        expected_roads = [
            Street.from_nodes([RoadSimpleNode.on(3, 1), intersection]),
            Street.from_nodes([RoadSimpleNode.on(3, -1), intersection])
        ]
        self.assertItemsEqual(self.city.roads, expected_roads)

    def test_get_roads_L_type(self):
        """
        (0,0)--(1,0)--(6,1)
                  |---(6,6)
        Note that (6,6) is discarded since the angle is greater than 15deg
        """
        n1 = GraphNode(Point(0, 0))
        n2 = GraphNode(Point(1, 0))
        n3 = GraphNode(Point(6, 1))
        n4 = GraphNode(Point(6, 6))

        self._connect(n1, n2)
        self._connect(n2, n3)
        self._connect(n2, n4)

        VertexGraphToRoadsConverter(self.city, 0.25, [n1, n2, n3, n4]).run()
        intersection = RoadIntersectionNode.on(1, 0)
        expected_roads = [
            Street.from_nodes([RoadSimpleNode.on(0, 0), intersection, RoadSimpleNode.on(6, 1)]),
            Street.from_nodes([RoadSimpleNode.on(6, 6), intersection])
        ]
        self.assertItemsEqual(self.city.roads, expected_roads)

    def test_get_roads_Y_type(self):
        """
        (0,0)--(1,0)--(6,1)
                  |---(6,-0.8)
        Note that (6,1) is discarded only because (6,-0.8) is a better
        candidate, but both are eligible
        """
        n1 = GraphNode(Point(0, 0))
        n2 = GraphNode(Point(1, 0))
        n3 = GraphNode(Point(6, 1))
        n4 = GraphNode(Point(6, -0.8))

        self._connect(n1, n2)
        self._connect(n2, n3)
        self._connect(n2, n4)

        VertexGraphToRoadsConverter(self.city, 0.25, [n1, n2, n3, n4]).run()
        intersection = RoadIntersectionNode.on(1, 0)
        expected_roads = [
            Street.from_nodes([RoadSimpleNode.on(0, 0), intersection, RoadSimpleNode.on(6, -0.8)]),
            Street.from_nodes([RoadSimpleNode.on(6, 1), intersection])
        ]
        self.assertItemsEqual(self.city.roads, expected_roads)

    def test_get_roads_matrix_distribution(self):
        """
        (0,2)--(1,2)--(2,2)
          |      |      |
        (0,1)--(1,1)--(2,1)
          |      |      |
        (0,0)--(1,0)--(2,0)
        """
        n1 = GraphNode(Point(0, 0))
        n2 = GraphNode(Point(1, 0))
        n3 = GraphNode(Point(2, 0))

        n4 = GraphNode(Point(0, 1))
        n5 = GraphNode(Point(1, 1))
        n6 = GraphNode(Point(2, 1))

        n7 = GraphNode(Point(0, 2))
        n8 = GraphNode(Point(1, 2))
        n9 = GraphNode(Point(2, 2))

        self._connect(n1, n2)
        self._connect(n1, n4)
        self._connect(n2, n5)
        self._connect(n2, n3)
        self._connect(n3, n6)
        self._connect(n4, n5)
        self._connect(n4, n7)
        self._connect(n5, n6)
        self._connect(n5, n8)
        self._connect(n6, n9)
        self._connect(n7, n8)
        self._connect(n8, n9)

        VertexGraphToRoadsConverter(self.city, 0.25, [n1, n2, n3, n4, n5, n6, n7, n8, n9]).run()
        j1 = RoadIntersectionNode.on(0, 0)
        j2 = RoadIntersectionNode.on(1, 0)
        j3 = RoadIntersectionNode.on(2, 0)
        j4 = RoadIntersectionNode.on(0, 1)
        j5 = RoadIntersectionNode.on(1, 1)
        j6 = RoadIntersectionNode.on(2, 1)
        j7 = RoadIntersectionNode.on(0, 2)
        j8 = RoadIntersectionNode.on(1, 2)
        j9 = RoadIntersectionNode.on(2, 2)
        expected_roads = [
            Street.from_nodes([j1, j4, j7]),
            Street.from_nodes([j2, j5, j8]),
            Street.from_nodes([j3, j6, j9]),
            Street.from_nodes([j1, j2, j3]),
            Street.from_nodes([j4, j5, j6]),
            Street.from_nodes([j7, j8, j9])
        ]
        self.assertItemsEqual(self.city.roads, expected_roads)

    def test_get_roads_Y_street_best_neighbour_trunk(self):
        """
        (0,0)--(1,0)--(6,1)
                  |---(6,-0.8)(trunk)
        Expected: main street:[(0,0),(1,0),(6,1)]
                  access street:[(1,0), (6,-0.8)]
        """
        n1 = GraphNode(Point(0, 0))
        n2 = GraphNode(Point(1, 0))
        v3 = GraphNode(Point(6, 1))
        n4 = GraphNode(Point(6, -0.8))
        n4.is_minor_road = False  # make trunk

        self._connect(n1, n2)
        self._connect(n2, v3)
        self._connect(n2, n4)

        VertexGraphToRoadsConverter(self.city, 0.25, [n1, n2, v3, n4]).run()
        intersection = RoadIntersectionNode.on(1, 0)
        expected_roads = [
            Street.from_nodes([RoadSimpleNode.on(0, 0), intersection, RoadSimpleNode.on(6, 1)]),
            Street.from_nodes([intersection, RoadSimpleNode.on(6, -0.8)])
        ]
        self.assertItemsEqual(self.city.roads, expected_roads)

    def test_get_roads_Y_street_best_neighbour_street(self):
        """
        (0,0)--(1,0)--(6,1)(trunk)
                  |---(6,-0.8)
        Expected: main street:[(0,0),(1,0),(6,-0.8)]
                  access street:[(1,0), (6,1)]
        """
        n1 = GraphNode(Point(0, 0))
        n2 = GraphNode(Point(1, 0))
        n3 = GraphNode(Point(6, 1))
        n3.is_minor_road = False  # make trunk
        n4 = GraphNode(Point(6, -0.8))

        self._connect(n1, n2)
        self._connect(n2, n3)
        self._connect(n2, n4)

        VertexGraphToRoadsConverter(self.city, 0.25, [n1, n2, n3, n4]).run()
        intersection = RoadIntersectionNode.on(1, 0)
        expected_roads = [
            Street.from_nodes([RoadSimpleNode.on(0, 0), intersection, RoadSimpleNode.on(6, -0.8)]),
            Street.from_nodes([intersection, RoadSimpleNode.on(6, 1)])
        ]
        self.assertItemsEqual(self.city.roads, expected_roads)

    def test_get_roads_pipe_street_into_trunk(self):
        """
        (0,0)--(1,0)--(6,0)(trunk)
        Expected: main street:[(0,0),(1,0),(6,0)]
        """
        n1 = GraphNode(Point(0, 0))
        n2 = GraphNode(Point(1, 0))
        n3 = GraphNode(Point(6, 0))
        n3.is_minor_road = False  # make trunk

        self._connect(n1, n2)
        self._connect(n2, n3)

        VertexGraphToRoadsConverter(self.city, 0.25, [n1, n2, n3]).run()
        expected_roads = [
            Street.from_nodes([RoadSimpleNode.on(0, 0), RoadSimpleNode.on(1, 0), RoadSimpleNode.on(6, 0)])
        ]
        self.assertItemsEqual(self.city.roads, expected_roads)

    def test_get_roads_pipe_trunk_into_street(self):
        """
        (0,0)(trunk)--(1,0)(trunk)--(6,0)
        Expected: trunk:[(0,0),(1,0)]
                  access street:[(6,0),(1,0)]
        """
        n1 = GraphNode(Point(0, 0))
        n1.is_minor_road = False  # make trunk
        n2 = GraphNode(Point(1, 0))
        n2.is_minor_road = False  # make trunk
        n3 = GraphNode(Point(6, 0))

        self._connect(n1, n2)
        self._connect(n2, n3)

        VertexGraphToRoadsConverter(self.city, 0.25, [n1, n2, n3]).run()

        intersection = RoadIntersectionNode.on(1, 0)
        expected_roads = [
            Street.from_nodes([RoadSimpleNode.on(6, 0), intersection]),
            Trunk.from_nodes([RoadSimpleNode.on(0, 0), intersection])
        ]
        self.assertItemsEqual(self.city.roads, expected_roads)

    def _connect(self, n1, n2):
        """Make a bidirectional connection between two nodes"""
        n1.add_neighbour(n2)
        n2.add_neighbour(n1)
