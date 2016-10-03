import numpy as np
from operator import itemgetter
from models.road import Street, Trunk
from geometry.point import Point

class VertexGraphToRoadsConverter(object):
    def __init__(self, vertex_list):
        self.vertex_list = vertex_list

    def get_roads(self):
        roads = []
        to_traverse = self.vertex_list
        while to_traverse:
          # Not particularly performant, needs review
          to_traverse = sorted(to_traverse, key=lambda vertex: len(vertex.neighbours))
          vertex = to_traverse.pop(0);
          while vertex.neighbours:
              street = Street()
              street.add_point(vertex.coords)
              self._build_road(street, None, vertex)
              roads.append(street)
        return roads

    def _build_road(self, street, previous_vertex, current_vertex):
        if previous_vertex is None:
            neighbour = current_vertex.neighbours.pop()
            if current_vertex in neighbour.neighbours:
                neighbour.neighbours.remove(current_vertex)
            street.add_point(neighbour.coords)
            self._build_road(street, current_vertex, neighbour)
        else:
            current_angle = previous_vertex.coords.angle_2d_to(current_vertex.coords)
            edges = []
            for neighbour in current_vertex.neighbours:
                neighbours_angle = current_vertex.coords.angle_2d_to(neighbour.coords)
                edges.append([neighbour, abs(current_angle - neighbours_angle)])
            edges.sort(key=itemgetter(1))
            # 0.25 rad = 15deg
            if edges and (edges[0][1] < 0.5):
                selected_neighbour = edges[0][0]
                current_vertex.neighbours.remove(selected_neighbour)
                selected_neighbour.neighbours.remove(current_vertex)
                street.add_point(selected_neighbour.coords)
                self._build_road(street, current_vertex, selected_neighbour )
