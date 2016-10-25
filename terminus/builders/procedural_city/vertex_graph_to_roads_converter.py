import numpy as np
from operator import itemgetter
from models.street import Street
from models.trunk import Trunk


class VertexGraphToRoadsConverter(object):

    def __init__(self, angle_threshold, vertex_list):
        self.angle_threshold = angle_threshold
        self.vertex_list = vertex_list

    def get_roads(self):
        roads = []
        to_traverse = self.vertex_list
        while to_traverse:
            # Not particularly performant, needs review
            to_traverse = sorted(to_traverse,
                                 key=lambda vertex: len(vertex.neighbours))
            vertex = to_traverse.pop(0)
            while vertex.neighbours:
                if vertex.minor_road:
                    road = Street(width=4)
                else:
                    road = Trunk(width=22)
                road.add_point(vertex.coords)
                self._build_road(road, None, vertex)
                if len(road.points) > 1:
                    roads.append(road)
        return roads

    def _build_road(self, road, previous_vertex, current_vertex):
        # If there is no previous vertex we don't care about the angle between
        # the current_vertex and the neighbour, as we are building the first
        # segment
        if previous_vertex is None:
            neighbour = current_vertex.neighbours.pop()
            # If first vertex is a trunk and the second is a street, then stop
            if not current_vertex.minor_road and neighbour.minor_road:
                return
            if current_vertex in neighbour.neighbours:
                neighbour.neighbours.remove(current_vertex)
            road.add_point(neighbour.coords)
            self._build_road(road, current_vertex, neighbour)
        else:
            # Since there is a previous vertex, we must compute the angle
            # between the previous_vertex and the current_vertex and try to
            # find the neighbour that is better aligned with that segment.
            current_angle = self._angle_2d(previous_vertex.coords,
                                           current_vertex.coords)
            edges = []
            for neighbour in current_vertex.neighbours:
                neighbours_angle = self._angle_2d(current_vertex.coords,
                                                  neighbour.coords)
                edges.append([neighbour,
                             abs(current_angle - neighbours_angle)])
            edges.sort(key=itemgetter(1))
            # Pick the edge with the lowest angle and check if it's below the
            # threshold.
            first_option = second_option = None
            for edge in edges:
                if edge[1] <= self.angle_threshold:
                    selected_neighbour = edge[0]
                    # Prefer building the same type of road in first place
                    if current_vertex.minor_road == \
                            selected_neighbour.minor_road:
                        first_option = selected_neighbour
                        break
                    # Prefer connecting a street to a trunk in second place
                    if current_vertex.minor_road and \
                            not selected_neighbour.minor_road and \
                            second_option is None:
                        second_option = selected_neighbour
            # If we've got some options, use the best one
            best_neighbour = None
            if first_option is not None:
                best_neighbour = first_option
            else:
                if second_option is not None:
                    best_neighbour = second_option
            if best_neighbour is not None:
                current_vertex.neighbours.remove(best_neighbour)
                if current_vertex in best_neighbour.neighbours:
                    best_neighbour.neighbours.remove(current_vertex)
                road.add_point(best_neighbour.coords)
                self._build_road(road, current_vertex, best_neighbour)

    def _angle_2d(self, point_from, point_to):
        alpha = np.arctan2(point_from.x - point_to.x,
                           point_from.y - point_to.y)
        if alpha < 0:
            alpha += 2 * np.pi
        return alpha
