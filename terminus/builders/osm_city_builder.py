from geometry.point import Point

from imposm.parser import OSMParser
import math

from models.city import City
from models.street import Street
from models.trunk import Trunk
from models.block import Block
from models.building import Building
from models.ground_plane import GroundPlane
from models.road import *

import xml.etree.ElementTree as ET

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# For now exclude smaller roads, in the future we should draw each
# type of street with different width/texture
road_types = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary',
              'unclassified', 'residential']


class OsmCityBuilder(object):
    def __init__(self, osm_map):
        self.osm_map = osm_map
        self.osm_coords = {}
        self.osm_nodes = {}
        self.osm_ways = {}
        self.map_origin = None

    def get_city(self):
        city = City()

        # Ground plane
        city.set_ground_plane(GroundPlane(100, Point(0, 0, 0)))

        # Get origin of the map (we use the center)
        tree = ET.parse(self.osm_map)
        bounds = tree.find('bounds').attrib
        self.map_origin = ((float(bounds['minlat']) + float(bounds['maxlat'])) / 2,
                           (float(bounds['minlon']) + float(bounds['maxlon'])) / 2)

        logger.debug("Map Origin: {0}".format(self.map_origin))

        # Parse OSM map
        self.parser = OSMParser(coords_callback=self._get_coords,
                                ways_callback=self._get_ways)
        self.parser.parse(self.osm_map)

        logger.debug("Number of ways: {}".format(len(self.osm_ways)))
        logger.debug("Number of coords: {}".format(len(self.osm_coords)))

        self._create_roads(city)

        return city

    def _get_ways(self, ways):
        ''' OSM parser callback for the ways '''
        for osmid, tags, refs in ways:
            if 'highway' in tags:
                if tags['highway'] in road_types:
                    self.osm_ways[osmid] = {'tags': tags, 'refs': refs}

    def _get_coords(self, coords):
        ''' OSM parser callback for the coords '''
        for osmid, lat, lon in coords:
            self.osm_coords[osmid] = {'lat': lat, 'lon': lon}

    def _create_roads(self, city):
        for key, value in self.osm_ways.iteritems():
            tmp_road = Street()
            for ref in value['refs']:
                x, y = self._translate_coords(self.osm_coords[ref]['lat'],
                                              self.osm_coords[ref]['lon'])
                tmp_road.add_node(JunctionNode.on(x, y, 0))
            city.add_road(tmp_road)

    def _translate_coords(self, lat, lon):
        meters_per_degree_lat = 111319.9
        meters_per_degree_lon = meters_per_degree_lat * math.cos(self.map_origin[0])
        y = (lon - self.map_origin[0]) * meters_per_degree_lon
        x = (lat - self.map_origin[1]) * meters_per_degree_lat
        return (x, y)
