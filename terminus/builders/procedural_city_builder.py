from models.city import City
from models.road import Street, Trunk
from models.point import Point
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
        print("Parsing file...")
        vertex_list = self._parse_file()
        print("Building streets...")
        for vertex in vertex_list:
            for neighbour in vertex.neighbours:
                road = Street()
                road.add_segment(Point(vertex.coords[0]*ratio, vertex.coords[1]*ratio, 0))
                road.add_segment(Point(neighbour.coords[0]*ratio, neighbour.coords[1]*ratio, 0))
                city.add_road(road)
        city.set_ground_plane(GroundPlane(100, Point(0,0,0)))
        return city

    def _parse_file(self):
        with open(self.filename, 'rb') as f:
            # TODO: We should read/pre-process this lazily, no point in loading
            # the whole thing in memory.
            # Here we do the hacky conversion, from the Vertex class dumped in
            # procedural_city_generation package to our Vertex class use by this
            # builder.
            originalPackage = 'procedural_city_generation.roadmap.Vertex'
            builderPackage = 'builders.procedural_city.vertex'
            contents = f.read().replace(originalPackage, builderPackage)
            return pickle.loads(contents)
