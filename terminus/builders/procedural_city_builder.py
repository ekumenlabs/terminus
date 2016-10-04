from geometry.point import Point
from models.city import City
from models.road import Street, Trunk
from models.block import Block
from models.building import Building
from models.ground_plane import GroundPlane

from procedural_city.vertex import Vertex
from procedural_city.vertex_graph_to_roads_converter \
    import VertexGraphToRoadsConverter

import pickle


class ProceduralCityBuilder(object):
    def __init__(self, filename):
        self.filename = filename

    def get_city(self):
        city = City()
        ratio = 10
        vertex_list = self._parse_file()
        roads = self._build_roads(vertex_list, ratio)
        for road in roads:
            city.add_road(road)
        city.set_ground_plane(GroundPlane(100, Point(0, 0)))
        return city

    def _build_roads(self, vertex_list, ratio):
        # Convert them to Gazebo coordinates. This is definitely ugly, as
        # we are changing the type in vertex.coords, we should revisit.
        for vertex in vertex_list:
            vertex.coords = Point(vertex.coords[0]*ratio,
                                  vertex.coords[1]*ratio)
        # 0.79 rad ~ 45 deg
        converter = VertexGraphToRoadsConverter(0.79, vertex_list)
        return converter.get_roads()

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
