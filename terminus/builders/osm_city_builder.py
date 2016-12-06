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


class OsmCityBuilder(object):
    def __init__(self, osm_map):
        self.osm_map = osm_map
        self.osm_coords = {}
        self.osm_nodes = {}
        self.osm_ways = {}
        self.bounds = {}
        self.map_origin = None

    def get_city(self):
        city = City()

        # Get origin of the map (we use the center)
        tree = ET.parse(self.osm_map)
        bounds = tree.find('bounds').attrib
        self.bounds = {'minlat': float(bounds['minlat']),
                       'maxlat': float(bounds['maxlat']),
                       'minlon': float(bounds['minlon']),
                       'maxlon': float(bounds['maxlon'])}

        self.map_origin = Point((self.bounds['minlat'] + self.bounds['maxlat']) / 2,
                                (self.bounds['minlon'] + self.bounds['maxlon']) / 2,
                                0)

        logger.debug("Map Origin: {0}".format(self.map_origin))

        # Calculate bounding box based on lat/lon
        min_xy = self._translate_coords(self.bounds['minlat'],
                                        self.bounds['minlon'])
        max_xy = self._translate_coords(self.bounds['maxlat'],
                                        self.bounds['maxlon'])
        self.bounds['min_xy'] = min_xy
        self.bounds['max_xy'] = max_xy

        self.bounds['size'] = Point(abs(min_xy.x) + abs(max_xy.x),
                                    abs(min_xy.y) + abs(max_xy.y),
                                    0)

        logger.debug("Bound box size {0}".format(self.bounds['size']))
        logger.debug(
            "Bound box 'minlat': {0}, 'maxlat': {1}\n\t\t\t\t\t  "
            "'minlon': {2}, 'maxlon': {3}".format(self.bounds['minlat'],
                                                  self.bounds['maxlat'],
                                                  self.bounds['minlon'],
                                                  self.bounds['maxlon'])
        )

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

        return city

    def _get_ways(self, ways):
        ''' OSM parser callback for the ways '''
        # For now exclude smaller roads, in the future we should draw each
        # type of street with different width/texture
        road_types = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary',
                      'unclassified', 'residential']

        for osmid, tags, refs in ways:
            if 'highway' in tags:
                if tags['highway'] in road_types:
                    self.osm_ways[osmid] = {'tags': tags, 'refs': refs}

    def _get_coords(self, coords):
        ''' OSM parser callback for the coords '''
        for osmid, lon, lat in coords:
            self.osm_coords[osmid] = {'lat': lat, 'lon': lon}

    def _create_roads(self, city):
        for key, value in self.osm_ways.iteritems():
            tmp_road = Street()
            coords_outside_box = []
            road_in_and_out = False
            coord_inside_bounds = False
            for ref in value['refs']:
                # Check if coord is inside bounding box
                ref_lat = self.osm_coords[ref]['lat']
                ref_lon = self.osm_coords[ref]['lon']
                coord = self._translate_coords(ref_lat, ref_lon)

                if self._is_coord_inside_bounds(ref_lat, ref_lon):
                    # If list is empty, use the node
                    if not coords_outside_box:
                        tmp_road.add_node(SimpleNode.on(coord.x, coord.y, 0))
                        coord_inside_bounds = True
                    else:
                        # In this case, the road goes out of the bounding box
                        # and comes basck again
                        road_in_and_out = True
                        coords_outside_box.append(coord)
                else:
                    if coord_inside_bounds:
                        coords_outside_box.append(coord)

            # Add nodes if way runs in and out the bounding box
            if road_in_and_out:
                for coord in coords_outside_box:
                    tmp_road.add_node(SimpleNode.on(coord.x, coord.y, 0))

            # Checck that road has at least two nodes
            if tmp_road.node_count() < 2:
                continue

            city.add_road(tmp_road)

    def _is_coord_inside_bounds(self, lat, lon):
        if self.bounds['minlat'] < lat < self.bounds['maxlat'] and \
           self.bounds['minlon'] < lon < self.bounds['maxlon']:
            return True

    def _check_road_type(self, road_type):
        pass

    def _translate_coords(self, lat, lon):
        meters_per_degree_lat = 111319.9
        meters_per_degree_lon = meters_per_degree_lat * math.cos(self.map_origin.x)
        x = (lon - self.map_origin.y) * meters_per_degree_lon
        y = (lat - self.map_origin.x) * meters_per_degree_lat
        return Point(x, y, 0)
