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
import copy
import numpy as np
from operator import itemgetter
from models.road import *
from models.street import Street
from models.trunk import Trunk


class VertexGraphToRoadsConverter(object):

    def __init__(self, city, angle_threshold, graph_node_list):
        self.city = city
        self.angle_threshold = angle_threshold
        self.graph_node_list = graph_node_list

    def run(self):
        to_traverse = self.graph_node_list
        for node in to_traverse:
            node.prepare_traversal()
        while to_traverse:
            # Not particularly performant, needs review
            to_traverse = sorted(to_traverse,
                                 key=lambda node: node.neighbours_to_traverse_count())
            node = to_traverse.pop(0)
            while node.get_neighbours_to_traverse():
                if node.is_minor_road:
                    road = Street()
                else:
                    road = Trunk()
                if node.neighbours_count() > 1:
                    self.city.add_intersection_at(node.location)

                road.add_point(node.location)

                self._build_road(road, None, node)

                if road.node_count() > 1:
                    self.city.add_road(road)

    def _build_road(self, road, previous_node, current_node):
        # If there is no previous vertex we don't care about the angle between
        # the current_node and the neighbour, as we are building the first
        # segment
        if previous_node is None:
            neighbour = current_node.pop_neighbours_to_traverse()
            # If first vertex is a trunk and the second is a street, then stop
            if not current_node.is_minor_road and neighbour.is_minor_road:
                return
            if current_node in neighbour.get_neighbours_to_traverse():
                neighbour.remove_neighbour_to_traverse(current_node)
            if neighbour.neighbours_count() > 2:
                self.city.add_intersection_at(neighbour.location)
            road.add_point(neighbour.location)
            self._build_road(road, current_node, neighbour)
        else:
            # Since there is a previous vertex, we must select the
            # best of the neighbours.
            best_neighbour = self._pick_best_neighbour(previous_node,
                                                       current_node)
            if best_neighbour is not None:
                current_node.remove_neighbour_to_traverse(best_neighbour)
                if current_node in best_neighbour.get_neighbours_to_traverse():
                    best_neighbour.remove_neighbour_to_traverse(current_node)
                if best_neighbour.neighbours_count() > 2:
                    self.city.add_intersection_at(best_neighbour.location)
                road.add_point(best_neighbour.location)
                self._build_road(road, current_node, best_neighbour)
            else:
                # Go to the last point and fix if it was originally a simple
                # node but had 2 neighbours, since it should be flagged as
                # an intersection.
                if current_node.neighbours_count() == 2:
                    last_node = road.get_nodes()[-1]
                    self.city.add_intersection_at(last_node.center)

    def _angle_2d(self, point_from, point_to):
        alpha = np.arctan2(point_from.x - point_to.x,
                           point_from.y - point_to.y)
        if alpha < 0:
            alpha += 2 * np.pi
        return alpha

    def _pick_best_neighbour(self, previous_node, current_node):
        """
        Choose the best neighbour for the current vertex.
        We order the edges according to their angle with the current edge and
        we select the vertex with the lowest angle and check if it's below the
        threshold. Also we prefer continuing the same type of road.
        Trunks can only start and end on trunk vertices (`minor_road` == false).
        Streets can eventually end on a trunk vertex.
        """
        current_angle = self._angle_2d(previous_node.location,
                                       current_node.location)
        edges = []
        for neighbour in current_node.get_neighbours_to_traverse():
            neighbours_angle = self._angle_2d(current_node.location,
                                              neighbour.location)
            edges.append([neighbour,
                         abs(current_angle - neighbours_angle)])
        edges.sort(key=itemgetter(1))
        first_option = second_option = None
        for edge in edges:
            if edge[1] <= self.angle_threshold:
                selected_neighbour = edge[0]
                # Prefer building the same type of road in first place
                if current_node.is_minor_road == \
                        selected_neighbour.is_minor_road:
                    first_option = selected_neighbour
                    break
                # Prefer connecting a street to a trunk in second place
                if current_node.is_minor_road and \
                        not selected_neighbour.is_minor_road and \
                        second_option is None:
                    second_option = selected_neighbour
        # If we've got some options, use the best one
        best_neighbour = None
        if first_option is not None:
            best_neighbour = first_option
        else:
            if second_option is not None:
                best_neighbour = second_option
        return best_neighbour
