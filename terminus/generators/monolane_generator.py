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

from collections import OrderedDict
import math

import yaml
from geometry.point import Point
from geometry.line_segment import LineSegment
from geometry.arc import Arc
from geometry.path import Path
from file_generator import FileGenerator
from monolane_id_mapper import MonolaneIdMapper
from models.lines_and_arcs_geometry import LinesAndArcsGeometry

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonolaneGenerator(FileGenerator):
    def __init__(self, city):
        super(MonolaneGenerator, self).__init__(city)

    def start_city(self, city):
        """Called when a visitation of a new city starts."""
        # First run the id mapper
        self.monolane_id_mapper = MonolaneIdMapper(city)
        self.monolane_id_mapper.run()
        # Map points and connections to avoid overlapping issues
        self.connected_points = {}
        self.monolane = {
            'maliput_monolane_builder': OrderedDict([
                ('id', city.name),
                ('lane_bounds', [-2, 2]),
                ('driveable_bounds', [-4, 4]),
                ('position_precision', 0.0005),
                ('orientation_precision', 0.5),
                ('points', OrderedDict()),
                ('connections', OrderedDict()),
                ('groups', OrderedDict()),
            ])
        }

    def start_lane(self, lane):
        self._build_lane_points(lane)
        self._build_lane_connections(lane)

    def _build_lane_points(self, lane):
        previous_waypoint = None
        previous_monolane_point = None
        last_line_heading = None
        for waypoint in lane.waypoints_for(LinesAndArcsGeometry):
            self._store_waypoint(waypoint)
        for connection in lane.out_connections_for(LinesAndArcsGeometry):
            for waypoint in connection.intermediate_waypoints():
                self._store_waypoint(waypoint)

    def _store_waypoint(self, waypoint):
        monolane_point = self._monolane_point_from_waypoint(waypoint)
        monolane_point_id = self.monolane_id_mapper.formatted_id_for(waypoint)
        self.monolane['maliput_monolane_builder']['points'][monolane_point_id] = monolane_point

    def _monolane_point_from_waypoint(self, waypoint):
        return self._create_monolane_point(waypoint.center(), waypoint.heading())

    def _create_monolane_point(self, center, heading):
        center = center.rounded_to(7)
        point = OrderedDict()
        point['xypoint'] = [float(center.x), float(center.y), float(heading)]
        point['zpoint'] = [float(center.z), 0, 0, 0]
        return point

    def _build_lane_connections(self, lane):
        waypoints = lane.waypoints_for(LinesAndArcsGeometry)
        connections = lane.inner_connections_for(LinesAndArcsGeometry)
        path = lane.path_for(LinesAndArcsGeometry)

        self._build_lane_inner_connections(lane, connections, path)
        self._build_lane_out_connections(waypoints, path)

    def _build_lane_inner_connections(self, lane, connections, path):

        # Remove extra segments if road starts with an intersection
        connections = self._trim_initial_connections(lane.road_nodes()[0], connections)

        # Remove extra segments if road ends in an intersection
        connections = self._trim_final_connections(lane.road_nodes()[-1], connections)

        for connection in connections:
            self._create_connection(path, connection)

    def _build_lane_out_connections(self, waypoints, path):

        for waypoint in waypoints:
            # If the waypoint is an exit, create the connection with all the
            # entry waypoints of the other lanes.
            for out_connection in waypoint.out_connections():
                self._create_out_connection(path, out_connection)

    def _trim_initial_connections(self, initial_node, connections):

        def getter(connection):
            return connection.start_waypoint()
        connections_clone = list(connections)
        cutting_connection = self._find_cutting_connection(initial_node, connections_clone, getter)
        if cutting_connection:
            while connections_clone[0] is not cutting_connection:
                connections_clone.pop(0)
        return connections_clone

    def _trim_final_connections(self, final_node, connections):

        def getter(connection):
            return connection.end_waypoint()
        connections_clone = list(connections)
        connections_clone.reverse()
        cutting_connection = self._find_cutting_connection(final_node, connections_clone, getter)
        if cutting_connection:
            while connections_clone[0] is not cutting_connection:
                connections_clone.pop(0)
        connections_clone.reverse()
        return connections_clone

    def _find_cutting_connection(self, target_node, connections, getter):
        '''
        If the target node (either a start or end of road) is an intersection,
        find which connection should be the new start of the connection, so
        that we can later drop unneeded segments.
        '''

        # We only care about intersections
        if not target_node.is_intersection():
            return None

        # Find the first connection that has an intersection waypoint
        iterator = (connection for connection in connections if getter(connection).is_intersection())
        cutting_connection = next(iterator, None)

        if not cutting_connection:
            return None

        # If an intersection waypoint form another node got in the way,
        # make sure we could actually perform the intersection for that node;
        # otherwise do not perform any cutting
        if getter(cutting_connection).road_node() is not target_node:
            should_cut = any(getter(connection).is_intersection() and
                             getter(connection).road_node() is target_node for connection in connections)
            if not should_cut:
                return None

        return cutting_connection

    def _create_out_connection(self, path, connection):
        primitive = connection.primitive()

        if isinstance(primitive, Path):
            if not primitive.is_valid_path_connection():
                logger.error("Path is not a valid connection - {0}".format(primitive))
            else:
                waypoints = connection.waypoints()
                for index, element in enumerate(primitive):
                    start = waypoints[index]
                    end = waypoints[index + 1]
                    monolane_connection = self._connect(element, start, end)
                    if monolane_connection is not None:
                        start_point = start.center().rounded_to(0)
                        end_point = end.center().rounded_to(0)
                        self.connected_points[start_point] = start
                        self.connected_points[end_point] = end
                        self._write_connection(monolane_connection, start, end)
        else:
            monolane_connection = self._connect(primitive, connection.start_waypoint(), connection.end_waypoint())

            if monolane_connection is not None:
                start = connection.start_waypoint()
                start_point = start.center().rounded_to(0)
                end = connection.end_waypoint()
                end_point = end.center().rounded_to(0)
                self.connected_points[start_point] = start
                self.connected_points[end_point] = end
                self._write_connection(monolane_connection, start, end)

    def _connect(self, primitive, start, end):
        if isinstance(primitive, Arc):
            return self._create_arc_connection(primitive, start, end)
        elif isinstance(primitive, LineSegment):
            return self._create_line_connection(primitive, start, end)
        else:
            raise ValueError("Connection geometry not supported by monolane generator")

    def _write_connection(self, monolane_connection, start, end):
        monolane_connection_id = "{0}-{1}".format(self.monolane_id_mapper.formatted_id_for(start),
                                                  self.monolane_id_mapper.formatted_id_for(end))
        self.monolane['maliput_monolane_builder']['connections'][monolane_connection_id] = monolane_connection

    def _create_connection(self, path, connection):
        monolane_connection = self._connect(connection.primitive(), connection.start_waypoint(), connection.end_waypoint())

        if monolane_connection is not None:
            start = connection.start_waypoint()
            start_point = start.center().rounded_to(0)
            end = connection.end_waypoint()
            end_point = end.center().rounded_to(0)

            if start_point in self.connected_points:
                existing_waypoint = self.connected_points[start_point]
                if existing_waypoint.lane() is not start.lane() and \
                   abs(existing_waypoint.heading() - start.heading()) > 1e-5:
                    old_start_point = start.center()
                    start.move_along(path, 0.02)
                    start_point = start.center().rounded_to(0)
                    self._store_waypoint(start)
                    if 'length' in monolane_connection:
                        monolane_connection['length'] -= 0.02
                    logger.warn("Moving overlapping waypoint from {0} to {1}".format(old_start_point, start.center()))

            if end_point in self.connected_points:
                existing_waypoint = self.connected_points[end_point]
                if existing_waypoint.lane() is not end.lane() and \
                   abs(existing_waypoint.heading() - end.heading()) > 1e-5:
                    old_end_point = end.center()
                    end.move_along(path, -0.02)
                    end_point = end.center().rounded_to(0)
                    self._store_waypoint(end)
                    if 'length' in monolane_connection:
                        monolane_connection['length'] -= 0.02
                    logger.warn("Moving overlapping waypoint from {0} to {1}".format(old_end_point, end.center()))

            self.connected_points[start_point] = start
            self.connected_points[end_point] = end

            self._write_connection(monolane_connection, start, end)

    def _create_line_connection(self, primitive, start, end):
        return OrderedDict([
            ('start', 'points.' + self.monolane_id_mapper.formatted_id_for(start)),
            ('length', primitive.length()),
            ('explicit_end', 'points.' + self.monolane_id_mapper.formatted_id_for(end))
        ])

    def _create_arc_connection(self, primitive, start, end):

        radius = primitive.radius()

        # If the turning radius is less than the driveable_bounds then
        # don't generate the connection
        if radius <= 4.0:
            logger.error("Radius is too small to create an arc connection - {0}".format(primitive))
            return None

        angle_in_degrees = round(primitive.angular_length(), 7)

        return OrderedDict([
            ('start', 'points.' + self.monolane_id_mapper.formatted_id_for(start)),
            ('arc', [radius, angle_in_degrees]),
            ('explicit_end', 'points.' + self.monolane_id_mapper.formatted_id_for(end))
        ])

    def end_document(self):
        """Called after the document is generated, but before it is written to a file."""
        self.document.write(self._contents_as_string())

    def _contents_as_string(self):
        """Convert the current monolane data into its yaml version.

        Preserves order of the keys inside of 'maliput_monolane_builder'.
        """
        header = "# -*- yaml -*-\n---\n# distances are meters; angles are degrees.\n"

        class OrderedDumper(yaml.Dumper):
            pass

        def _dict_representer(dumper, data):
            return dumper.represent_mapping(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                data.items())

        OrderedDumper.add_representer(OrderedDict, _dict_representer)
        return header + yaml.dump(self.monolane, None, OrderedDumper)
