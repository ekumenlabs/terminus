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
from file_generator import FileGenerator
from monolane_id_mapper import MonolaneIdMapper
from models.lines_and_arcs_builder import LinesAndArcsBuilder

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
        # Reset all of the class variables used until stop_city is called.
        self.monolane = {
            'maliput_monolane_builder': OrderedDict([
                ('id', city.name),
                ('lane_bounds', [-2, 2]),
                ('driveable_bounds', [-4, 4]),
                ('position_precision', 0.01),
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
        for waypoint in lane.waypoints_using(LinesAndArcsBuilder):
            monolane_point = self._monolane_point_from_waypoint(waypoint)
            monolane_point_id = self.monolane_id_mapper.formatted_id_for(waypoint)
            self.monolane['maliput_monolane_builder']['points'][monolane_point_id] = monolane_point

    def _build_lane_connections(self, lane):
        connections = lane.waypoint_geometry_using(LinesAndArcsBuilder).connections()
        for connection in connections:
            monolane_connection = None

            # If the waypoint is an exit, create the connection with all the
            # entry waypoints of the other lanes.
            if connection.start_waypoint().is_exit():
                exit_waypoint = connection.start_waypoint()
                for out_connection in exit_waypoint.out_connections():
                    self._create_connection(out_connection)

            # In some cases we don't want to generate the connection between
            # the previous and following node.
            # If the lane starts with an intersection, start on the entry waypoint
            belong_to_same_node = connection.start_waypoint().road_node() is connection.end_waypoint().road_node()
            if belong_to_same_node and (connection is connections[0]) and connection.end_waypoint().is_entry():
                pass
            # If the lane ends with an intersection, end it on the exit waypoint
            elif belong_to_same_node and (connection is connections[-1]) and connection.start_waypoint().is_exit():
                pass
            else:
                self._create_connection(connection)

    def _create_connection(self, connection):
        connection_primitive = connection.primitive()
        if isinstance(connection_primitive, Arc):
            monolane_connection = self._create_arc_connection(connection)
        elif isinstance(connection_primitive, LineSegment):
            monolane_connection = self._create_line_connection(connection)
        else:
            raise ValueError("Connection geometry not supported by monolane generator")

        if monolane_connection is not None:
            start = connection.start_waypoint()
            end = connection.end_waypoint()
            monolane_connection_id = "{0}-{1}".format(self.monolane_id_mapper.formatted_id_for(start), self.monolane_id_mapper.formatted_id_for(end))
            self.monolane['maliput_monolane_builder']['connections'][monolane_connection_id] = monolane_connection

    def _create_line_connection(self, connection):
        return OrderedDict([
            ('start', 'points.' + self.monolane_id_mapper.formatted_id_for(connection.start_waypoint())),
            ('length', connection.primitive().length()),
            ('explicit_end', 'points.' + self.monolane_id_mapper.formatted_id_for(connection.end_waypoint()))
        ])

    def _create_arc_connection(self, connection):

        primitive = connection.primitive()

        radius = primitive.radius()

        # If the turning radius is less than the driveable_bounds then
        # don't generate the connection
        if radius <= 4:
            logger.error("Radius is too small to create an arc connection - {0}".format(primitive))
            return None

        angle_in_degrees = primitive.angular_length()

        return OrderedDict([
            ('start', 'points.' + self.monolane_id_mapper.formatted_id_for(connection.start_waypoint())),
            ('arc', [radius, angle_in_degrees]),
            ('explicit_end', 'points.' + self.monolane_id_mapper.formatted_id_for(connection.end_waypoint()))
        ])

    def _monolane_point_from_waypoint(self, waypoint):
        point = OrderedDict()
        point['xypoint'] = [float(waypoint.center().x), float(waypoint.center().y), float(waypoint.heading())]
        point['zpoint'] = [float(waypoint.center().z), 0, 0, 0]
        return point

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
