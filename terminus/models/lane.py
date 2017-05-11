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

from math import hypot, copysign
from geometry.point import Point
from geometry.line_segment import LineSegment
from geometry.line import Line
from shapely.geometry import LineString, LinearRing, Polygon
from shapely.geometry.collection import GeometryCollection
from shapely.geometry import Point as ShapelyPoint, MultiPoint
from city_model import CityModel
from waypoint import Waypoint
from waypoint_geometry import WaypointGeometry


class Lane(object):
    def __init__(self, road, width, offset):
        self._road = road
        self._width = width
        self._offset = offset
        self._cached_geometries = {}

    def offset(self):
        return self._offset

    def width(self):
        return self._width

    def external_offset(self):
        return copysign(abs(self.offset()) + (self.width() / 2.0), self.offset())

    def accept(self, generator):
        generator.start_lane(self)
        generator.end_lane(self)

    def road(self):
        return self._road

    def road_nodes(self):
        return self.road().nodes()

    def road_nodes_count(self):
        return self.road().node_count()

    def waypoints_for(self, geometry_class):
        return self._lane_geometry(geometry_class).waypoints()

    def path_for(self, geometry_class):
        return self._lane_geometry(geometry_class).path()

    def inner_connections_for(self, geometry_class):
        '''
        Returns a list of connections that connect the lane waypoints
        '''
        return self._lane_geometry(geometry_class).inner_connections()

    def out_connections_for(self, geometry_class):
        '''
        Returns a list of connections that are used to connect the lane
        waypoints with other lanes
        '''
        out_connections = []
        for waypoint in self.waypoints_for(geometry_class):
            out_connections.extend(waypoint.out_connections())
        return out_connections

    def starts_on(self, road_node):
        return self.road_nodes()[0] == road_node

    def ends_on(self, road_node):
        return self.road_nodes()[-1] == road_node

    def _lane_geometry(self, geometry_class):
        if geometry_class not in self._cached_geometries:
            geometry = geometry_class(self)
            self._cached_geometries[geometry_class] = geometry
        return self._cached_geometries[geometry_class]
