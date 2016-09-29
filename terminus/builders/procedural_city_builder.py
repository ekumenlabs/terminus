from geometry.point import Point
from geometry.line_segment import LineSegment
from models.city import City
from models.road import Street, Trunk
from models.block import Block
from models.building import Building
from models.ground_plane import GroundPlane

from procedural_city.vertex import Vertex

import pickle


class ProceduralCityBuilder(object):
    def __init__(self, filename):
        self.filename = filename

    def get_city(self):
        city = City()
        ratio = 10
        vertex_list = self._parse_file()
        segments = self._build_unique_street_segments(vertex_list, ratio)
        for segment in segments:
            road = Street()
            road.add_segment(segment.start)
            road.add_segment(segment.end)
            city.add_road(road)
        city.set_ground_plane(GroundPlane(100, Point(0, 0)))
        return city

    def _build_unique_street_segments(self, vertex_list, ratio):
        """For each street segment there are two vertex in the list, with
           the coords and neighbour exchanged (like a two-way street). We
           don't support street directions so far, so we just get rid of
           the duplicate road segments"""
        segments = set()
        for vertex in vertex_list:
            for neighbour in vertex.neighbours:
                start = Point(vertex.coords[0]*ratio,
                              vertex.coords[1]*ratio)
                end = Point(neighbour.coords[0]*ratio,
                            neighbour.coords[1]*ratio)
                segments.add(LineSegment(start, end))
        return segments

    def _parse_file(self):
        with open(self.filename, 'rb') as f:
            # TODO: We should read/pre-process this lazily, no point in loading
            # the whole thing in memory.
            # Here we do the hacky conversion, from the Vertex class dumped in
            # procedural_city_generation package to our Vertex class use by
            # this builder.
            originalPackage = 'procedural_city_generation.roadmap.Vertex'
            builderPackage = 'builders.procedural_city.vertex'
            contents = f.read().replace(originalPackage, builderPackage)
            return pickle.loads(contents)
