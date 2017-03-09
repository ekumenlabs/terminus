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
        self.bounds['min_xy'] = min_xy
        self.bounds['max_xy'] = max_xy
        self.bounds['min_x_max_y'] = Point(min_xy.x, max_xy.y)
        self.bounds['max_x_min_y'] = Point(max_xy.x, min_xy.y)

        self.bounds['bottom'] = LineSegment(self.bounds['min_xy'],
                                            self.bounds['max_x_min_y'])

        self.bounds['top'] = LineSegment(self.bounds['min_x_max_y'],
                                         self.bounds['max_xy'])

        self.bounds['left'] = LineSegment(self.bounds['min_x_max_y'],
                                          self.bounds['min_xy'])

        self.bounds['right'] = LineSegment(self.bounds['max_xy'],
                                           self.bounds['max_x_min_y'])

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
        self._create_buildings(city)

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
                        self.nodes[ref] = {}

                    # Only include way if it doesn't exist
                    if osmid not in self.nodes[ref]:
                        self.nodes[ref][osmid] = None

    def _get_coords(self, coords):
        ''' OSM parser callback for the coords '''
        # osmid: OSM id for the node
        # lat, lon: latitude and longitude of the node
        for osmid, lon, lat in coords:
            self.osm_coords[osmid] = {'lat': lat, 'lon': lon}

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
                tmp_road = Street(name='OSM_' + str(osmid))
                coords_outside_box = []
                road_in_and_out = False
                coord_inside_bounds = False
                already_intersected = False
                prev_coord_outside = False
                prev_coord = None
                for ref in value['refs']:
                    # Check if coord is inside bounding box
                    ref_lat = self.osm_coords[ref]['lat']
                    ref_lon = self.osm_coords[ref]['lon']
                    ref_pair = LatLon(ref_lat, ref_lon)
                    coord = self._translate_coords(ref_pair)
                    self.osm_coords[ref]['point'] = coord

                    if self._is_coord_inside_bounds(ref_pair):
                        # If previous coord were outisde the bounding box,
                        # add the interscting point with it to the road
                        if prev_coord_outside:
                            for intersection in self._check_intersection_with_bounding_box(prev_coord, coord):
                                self._add_point_to_road(tmp_road, intersection)

                        # If list is empty, use the node
                        if not coords_outside_box:
                            self._add_point_to_road(tmp_road, coord)
                            prev_coord = coord
                            coord_inside_bounds = True
                            if self.nodes[ref][osmid] is None:
                                self.nodes[ref][osmid] = tmp_road
                        else:
                            # In this case, the road goes out of the bounding box
                            # and comes back again
                            road_in_and_out = True
                            coords_outside_box.append(coord)
                        prev_coord_outside = False
                    else:
                        # If there is already a node inside the bounding box,
                        # add the interscting point with it to the road
                        if tmp_road.node_count() >= 1 and not already_intersected:
                            for intersection in self._check_intersection_with_bounding_box(prev_coord, coord):
                                self._add_point_to_road(tmp_road, intersection)
                                prev_coord = intersection
                                already_intersected = True

                        if coord_inside_bounds:
                            coords_outside_box.append(coord)
                        else:
                            # We should remember the previous coordinates
                            prev_coord_outside = True
                            prev_coord = coord

                # Add nodes if way runs in and out the bounding box
                if road_in_and_out:
                    for coord in coords_outside_box:
                        self._add_point_to_road(tmp_road, Point(coord.x, coord.y, 0))
                    if self.nodes[ref][osmid] is None:
                        self.nodes[ref][osmid] = tmp_road

                # Check that road has at least two nodes
                if tmp_road.node_count() < 2:
                    continue

                # Check if street is one or two ways
                oneway = False
                if 'oneway' in value['tags']:
                    oneway = value['tags']['oneway'] in ['true', '1', 'yes', 'reverse', '-1']

                if oneway:
                    # Check if the street should be reversed
                    if value['tags']['oneway'] in ['-1', 'reverse']:
                        tmp_road.reverse()
                else:
                    # Make roads two ways
                    tmp_road.be_two_way()

                city.add_road(tmp_road)

        # Create intersections from simple nodes
        for key, node in self.nodes.iteritems():
            roads = node.values()
            for index in range(len(roads)):
                if roads[index] is not None and index < len(roads) - 1:
                    city.add_intersection_at(self.osm_coords[key]['point'])

    def _add_point_to_road(self, road, point):
        if not road.includes_point(point):
            road.add_point(point)

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

    def _is_coord_inside_bounds(self, latlon):
        return latlon.is_inside(self.bounds['origin'], self.bounds['corner'])

    def _check_road_type(self, road_type):
        pass

    def _translate_coords(self, latlon):
        (delta_lat, delta_lon) = self.map_origin.delta_in_meters(latlon)
        return Point(delta_lon, delta_lat, 0)

    def _check_intersection_with_bounding_box(self, prev_coord, coord):
        '''
        Checks if a road segment (provided 2 coordinates for the nodes)
        intersects the bounding box
        '''
        segment = LineSegment(prev_coord, coord)

        # Check if segment intersects with bounding box
        intersections = [
            segment.find_intersection(self.bounds['top']),
            segment.find_intersection(self.bounds['right']),
            segment.find_intersection(self.bounds['bottom']),
            segment.find_intersection(self.bounds['left'])
        ]
        return [intersection for intersection in intersections if intersection is not None]
