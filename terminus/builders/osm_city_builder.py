"""
Copyright (C) 2017 Open Source Robotics Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from geometry.point import Point
from geometry.latlon import LatLon
from geometry.line_segment import LineSegment
from geometry.path import Path

from imposm.parser import OSMParser

from models.city import City
from models.street import Street
from models.trunk import Trunk
from models.block import Block
from models.building import Building
from models.ground_plane import GroundPlane
from models.road import *

from builders.abstract_city_builder import AbstractCityBuilder

import xml.etree.ElementTree as ET

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OsmCityBuilder(AbstractCityBuilder):
    def __init__(self, osm_map):
        self.osm_map = osm_map
        self.osm_coords = {}
        self.osm_nodes = {}
        self.osm_ways = {}
        self.bounds = {}
        self.map_origin = None
        self.nodes = {}
        self.road_types = ['motorway', 'trunk', 'primary', 'secondary',
                           'tertiary', 'unclassified', 'residential',
                           'living_street']

    def get_city(self):
        city = City()

        # Get origin of the map (we use the center)
        tree = ET.parse(self.osm_map)
        bounds = tree.find('bounds').attrib
        self.bounds = {'origin': LatLon(float(bounds['minlat']),
                                        float(bounds['minlon'])),
                       'corner': LatLon(float(bounds['maxlat']),
                                        float(bounds['maxlon']))}

        self.map_origin = self.bounds['origin'].midpoint(self.bounds['corner'])

        logger.debug("Map Origin: {0}".format(self.map_origin))

        # Calculate bounding box based on lat/lon
        min_xy = self._translate_coords(self.bounds['origin'])
        max_xy = self._translate_coords(self.bounds['corner'])
        self.bounding_box = BoundingBox(min_xy, max_xy)

        self.bounds['size'] = abs(min_xy) * 2

        logger.debug("Bound box size {0}".format(self.bounds['size']))
        logger.debug("Bounding box from {0} to {1}".format(self.bounds['origin'],
                                                           self.bounds['corner']))

        # Parse OSM map
        self.parser = OSMParser(coords_callback=self._get_coords,
                                ways_callback=self._get_ways)
        self.parser.parse(self.osm_map)

        logger.debug("Number of ways: {}".format(len(self.osm_ways)))
        logger.debug("Number of coords: {}".format(len(self.osm_coords)))

        # Ground plane
        city.set_ground_plane(GroundPlane(max(self.bounds['size'].x,
                                              self.bounds['size'].y),
                                          Point(0, 0, 0)))

        self._create_roads(city)
        self._create_intersections(city)
        # self._create_buildings(city)

        city.trim_roads()

        return city

    def _get_ways(self, ways):
        ''' OSM parser callback for the ways '''
        # osmid: OSM id for the way/street
        # tags: tag dictionary with various information about the way (name, type, etc)
        # refs: nodes that are part of the way/street
        for osmid, tags, refs in ways:
            self.osm_ways[osmid] = {'tags': tags, 'refs': refs}
            if 'highway' in tags and tags['highway'] in self.road_types:
                for ref in refs:
                    if ref not in self.nodes:
                        self.nodes[ref] = set()
                    self.nodes[ref].add(osmid)

    def _get_coords(self, coords):
        ''' OSM parser callback for the coords '''
        # osmid: OSM id for the node
        # lat, lon: latitude and longitude of the node
        for osmid, lon, lat in coords:
            lat_lon = LatLon(lat, lon)
            self.osm_coords[osmid] = {
                'lat_lon': lat_lon,
                'point': self._translate_coords(lat_lon)
            }

    def _create_road_geometry(self, id, record):
        points = []
        for ref in record['refs']:
            points.append(self.osm_coords[ref]['point'])

        geometry = Path.polyline_from_points(points)

        return geometry.trim_to_fit(self.bounding_box)

    def _create_road(self, city, osm_id, geometry, is_one_way, is_reversed):
        if is_one_way:
            road = Street(name='OSM_' + osm_id)
        else:
            road = Street(name='OSM_' + osm_id)
            # tmp_road = Trunk(name='OSM_' + str(osm_id))

        if is_reversed:
            geometry = geometry.reversed()

        road.add_control_points(geometry.vertices())

        city.add_road(road)

    def _create_roads(self, city):
        '''
        Iterate the ways data to find the highway objects and create roads
        with them.
        '''
        # For now exclude smaller roads, in the future we should draw each
        # type of street with different width/texture
        for osmid, value in self.osm_ways.iteritems():
            tags = value['tags']
            # Filter highways
            if 'highway' in tags and tags['highway'] in self.road_types:

                geometry = self._create_road_geometry(osmid, value)

                # Check if street is one or two ways
                is_one_way = False
                if 'oneway' in value['tags']:
                    is_one_way = value['tags']['oneway'] in ['true', '1', 'yes', 'reverse', '-1']

                # Check if the points were given in reversed order
                is_reversed = is_one_way and (value['tags']['oneway'] in ['-1', 'reverse'])

                # The road went outside the bounding box and back in. For that
                # case we will generate a new road for each piece.
                if len(geometry) > 1:
                    index = "A"
                    for road_geometry in geometry:
                        self._create_road(city, str(osmid) + "_" + index, road_geometry, is_one_way, is_reversed)
                        index = chr(ord(index) + 1)
                else:
                    road_geometry = geometry[0]
                    self._create_road(city, str(osmid), road_geometry, is_one_way, is_reversed)

    def _create_intersections(self, city):
        for node_id, nodes in self.nodes.iteritems():
            if len(nodes) > 1:
                city.add_intersection_at(self.osm_coords[node_id]['point'])

    def _add_point_to_road(self, road, point):
        if not road.includes_control_point(point):
            road.add_control_point(point)

    def _create_buildings(self, city):
        '''
        Iterate the ways to find the buildings data and create model buildings
        with it.
        '''
        for key, value in self.osm_ways.iteritems():
            tags = value['tags']
            if 'building' in tags:
                vertices = []
                for ref in value['refs']:
                    ref_lat = self.osm_coords[ref]['lat']
                    ref_lon = self.osm_coords[ref]['lon']
                    ref_pair = LatLon(ref_lat, ref_lon)
                    vertex = self._translate_coords(ref_pair)
                    vertices.append(vertex)
                if 'height' in value:
                    height = value['height']
                else:
                    height = 20
                building = Building(Point(0, 0, 0), vertices, height=height)
                city.add_building(building)

    def _translate_coords(self, latlon):
        (delta_lat, delta_lon) = self.map_origin.delta_in_meters(latlon)
        return Point(delta_lon, delta_lat, 0)
