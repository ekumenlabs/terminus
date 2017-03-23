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
from lane_simple_node import LaneSimpleNode
from lane_intersection_node import LaneIntersectionNode
from waypoint import Waypoint
from waypoint_geometry import WaypointGeometry


class Lane(object):
    def __init__(self, road, width, offset):
        # Note: all these are private properties and should be kept that way
        self._road = road
        self._width = width
        self._offset = offset
        self._waypoint_geometry = None
        self._polyline_geometry = None
        self._lines_and_arcs_geometry = None

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

    def polyline_geometry(self):
        if not self._polyline_geometry:
            self._polyline_geometry = self._road.polyline_geometry()
        return self._polyline_geometry

    def lines_and_arcs_geometry(self):
        if not self._lines_and_arcs_geometry:
            self._lines_and_arcs_geometry = self._road.lines_and_arcs_geometry()
        return self._lines_and_arcs_geometry

    def waypoints_count(self):
        return len(self.waypoints())

    def waypoints(self):
        return self.waypoint_geometry().waypoints()

    def waypoint_geometry(self):
        if not self._waypoint_geometry:
            self._waypoint_geometry = WaypointGeometry(self, self.lines_and_arcs_geometry())
        return self._waypoint_geometry
