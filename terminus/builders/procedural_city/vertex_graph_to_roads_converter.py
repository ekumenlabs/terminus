import numpy as np
from operator import itemgetter
from models.road import Street, Trunk

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
                street = Street()
                street.width = 5
                street.add_point(vertex.coords)
                self._build_road(street, None, vertex)
                roads.append(street)
        return roads

    def _build_road(self, street, previous_vertex, current_vertex):
        # If there is no previous vertex we don't care about the angle between
        # the current_vertex and the neighbour, as we are building the first
        # segment
        if previous_vertex is None:
            neighbour = current_vertex.neighbours.pop()
            if current_vertex in neighbour.neighbours:
                neighbour.neighbours.remove(current_vertex)
            street.add_point(neighbour.coords)
            self._build_road(street, current_vertex, neighbour)
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
            if edges and (edges[0][1] <= self.angle_threshold):
                selected_neighbour = edges[0][0]
                current_vertex.neighbours.remove(selected_neighbour)
                selected_neighbour.neighbours.remove(current_vertex)
                street.add_point(selected_neighbour.coords)
                self._build_road(street, current_vertex, selected_neighbour)

    def _angle_2d(self, point_from, point_to):
        alpha = np.arctan2(point_from.x - point_to.x, point_from.y - point_to.y)
        if alpha < 0:
            alpha += 2 * np.pi
        return alpha
