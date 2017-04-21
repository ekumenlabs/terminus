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

from path_geometry import PathGeometry

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PathGeometryBuilder(object):

    def __init__(self, control_points):
        if len(control_points) < 2:
            raise ValueError("Can't create a geometry from an empty path")
        self._control_points = control_points
        self._elements = self._build_geometry_from(self._control_points)

    def build_path_geometry(self, lane):
        geometry = PathGeometry(self._elements)
        geometry.simplify()
        self._extend_geometry_if_necessary(geometry, lane)
        return geometry

    def build_raw_geometry(self):
        geometry = PathGeometry(self._elements)
        geometry.simplify()
        return geometry

    def connect_waypoints(self, exit_waypoint, entry_waypoint):
        raise NotImplementedError()

    def index_nodes(self, nodes):
        raise NotImplementedError()

    def _build_geometry_from(self, points):
        raise NotImplementedError()

    def _extend_geometry_if_necessary(self, geometry, lane):
        road = lane.road()
        road_nodes = road.nodes()
        intersection_nodes = filter(lambda node: node.is_intersection(), road_nodes)
        for node in intersection_nodes:
            other_roads = node.involved_roads_except(road)
            other_lanes = []
            for other_road in other_roads:
                other_lanes.extend(other_road.lanes())
            for other_lane in other_lanes:
                intersections = set()
                intersection_control_point = node.center
                target_geometry = other_lane.raw_geometry_using(self.__class__)

                for source_element in geometry.elements():
                    for target_element in target_geometry.elements():
                        intersections.update(source_element.find_intersection(target_element))

                if not intersections:
                    if geometry.start_point().almost_equal_to(intersection_control_point, 5):
                        self._extend_geometry_start(node, geometry, target_geometry)
                    elif geometry.end_point().almost_equal_to(intersection_control_point, 5):
                        self._extend_geometry_end(node, geometry, target_geometry)
                    elif target_geometry.start_point().almost_equal_to(intersection_control_point, 5):
                        self._extend_geometry_start(node, target_geometry, geometry)
                    elif target_geometry.end_point().almost_equal_to(intersection_control_point, 5):
                        self._extend_geometry_end(node, target_geometry, geometry)

    def _extend_geometry_end(self, node, source_geometry, target_geometry):
        element = source_geometry.last_element()
        new_end = self._extend_geometry_element(node, element, source_geometry, target_geometry)
        source_geometry.replace_element_at(-1, new_end)

    def _extend_geometry_start(self, node, source_geometry, target_geometry):
        element = source_geometry.first_element().inverted()
        new_start = self._extend_geometry_element(node, element, source_geometry, target_geometry).inverted()
        source_geometry.replace_element_at(0, new_start)

    def _extend_geometry_element(self, node, element, source_geometry, target_geometry):
        intersections = set()
        new_element = element.extended_by(10)
        for target_element in target_geometry.elements():
            intersections.update(target_element.find_intersection(new_element))
        intersection = self._pick_intersection_from_list(intersections, node, source_geometry, target_geometry)
        return element.extended_to(intersection)

    def _pick_intersection_from_list(self, intersections, road_node, source_geometry, target_geometry):

        intersection_control_point = road_node.center
        intersections = list(intersections)

        if not intersections:
            logger.error("Couldn't find intersection between geometries")
            logger.error("ROAD NODE: {0}".format(road_node))
            logger.error("SOURCE: {0}".format(source_geometry))
            logger.error("TARGET: {0}".format(target_geometry))
            # TODO: Replace with assertion
            raise ValueError("Intersection list is empty, can't pick a value")

        if len(intersections) > 1:
            logger.debug("Multiple intersections found between geometries. Picking the closest one.")
            logger.debug("ROAD NODE: {0}".format(road_node))
            logger.debug("SOURCE: {0}".format(source_geometry))
            logger.debug("TARGET: {0}".format(target_geometry))
            logger.debug("INTERSECTIONS: {0}".format(intersections))
            intersections = sorted(intersections,
                                   key=lambda point: point.squared_distance_to(intersection_control_point))

        return intersections[0]
