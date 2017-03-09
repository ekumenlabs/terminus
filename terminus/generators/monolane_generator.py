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
from file_generator import FileGenerator
from monolane_id_mapper import MonolaneIdMapper

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

    def _build_lane_connections(self, lane):
        all_waypoints = lane.get_waypoints()
        previous_waypoint = None
        for waypoint in all_waypoints:
            if previous_waypoint is not None:
                # If the waypoint is an exit, create the connection with all the
                # entry waypoints of the other lanes.
                if waypoint.is_exit():
                    for entry_waypoint in waypoint.connected_waypoints():
                        monolane_connection = self._create_arc_connection(waypoint, entry_waypoint)
                        if monolane_connection is not None:
                            monolane_connection_id = "{0}-{1}".format(self.monolane_id_mapper.formatted_id_for(waypoint), self.monolane_id_mapper.formatted_id_for(entry_waypoint))
                            self.monolane['maliput_monolane_builder']['connections'][monolane_connection_id] = monolane_connection

                # Do the previous and current waypoint belong to the same intersection?
                are_same_intersection = previous_waypoint.source_node == waypoint.source_node

                # In some cases we don't want to generate the connection between
                # the previous and following node.
                # If the lane starts with an intersection, start on the entry waypoint
                if are_same_intersection and previous_waypoint == all_waypoints[0] and waypoint.is_entry():
                    pass
                # If the lane ends with an intersection, end it on the exit waypoint
                elif are_same_intersection and waypoint == all_waypoints[-1] and previous_waypoint.is_exit():
                    pass
                elif previous_waypoint.center == waypoint.center:
                    pass
                elif previous_waypoint.is_arc_start_connection() and waypoint.is_arc_end_connection():
                    monolane_connection = self._create_arc_connection(previous_waypoint, waypoint)
                    if monolane_connection is not None:
                        monolane_connection_id = "{0}-{1}".format(self.monolane_id_mapper.formatted_id_for(previous_waypoint), self.monolane_id_mapper.formatted_id_for(waypoint))
                        self.monolane['maliput_monolane_builder']['connections'][monolane_connection_id] = monolane_connection
                else:
                    monolane_connection = self._create_line_connection(previous_waypoint, waypoint)
                    monolane_connection_id = "{0}-{1}".format(self.monolane_id_mapper.formatted_id_for(previous_waypoint), self.monolane_id_mapper.formatted_id_for(waypoint))
                    self.monolane['maliput_monolane_builder']['connections'][monolane_connection_id] = monolane_connection
            previous_waypoint = waypoint

    def _create_line_connection(self, start_waypoint, end_waypoint):
        return OrderedDict([
            ('start', 'points.' + self.monolane_id_mapper.formatted_id_for(start_waypoint)),
            ('length', start_waypoint.center.distance_to(end_waypoint.center)),
            ('explicit_end', 'points.' + self.monolane_id_mapper.formatted_id_for(end_waypoint))
        ])

    def _create_arc_connection(self, start_waypoint, end_waypoint):
        try:
            previous_waypoint = self._previous_waypoint(start_waypoint)
            start_vector = start_waypoint.center - previous_waypoint.center

            following_waypoint = self._following_waypoint(end_waypoint)
            end_vector = following_waypoint.center - end_waypoint.center
        except:
            logger.debug("Can't create arc connection between {0} and {1}".format(start_waypoint, end_waypoint))
            return None

        angle = start_vector.angle(end_vector)
        d2 = start_waypoint.center.squared_distance_to(end_waypoint.center)
        cos = math.cos(angle)
        if cos == 1:
            return None
        radius = math.sqrt(d2 / (2 * (1 - cos)))

        # If the turning radius is less than the driveable_bounds then
        # don't generate the connection
        if radius <= 4:
            return None

        angle_in_degrees = math.degrees(angle)

        # Keep the angle in the [-180, 180) range
        if angle_in_degrees >= 180:
            angle_in_degrees = angle_in_degrees - 360

        if angle_in_degrees < -180:
            angle_in_degrees = angle_in_degrees + 360

        return OrderedDict([
            ('start', 'points.' + self.monolane_id_mapper.formatted_id_for(start_waypoint)),
            ('arc', [radius, angle_in_degrees]),
            ('explicit_end', 'points.' + self.monolane_id_mapper.formatted_id_for(end_waypoint))
        ])

    def _previous_waypoint(self, waypoint):
        (road_id, lane_id, waypoint_id) = self.monolane_id_mapper.id_for(waypoint)
        return self.monolane_id_mapper.object_for((road_id, lane_id, waypoint_id - 1))

    def _following_waypoint(self, waypoint):
        (road_id, lane_id, waypoint_id) = self.monolane_id_mapper.id_for(waypoint)
        return self.monolane_id_mapper.object_for((road_id, lane_id, waypoint_id + 1))

    def end_document(self):
        """Called after the document is generated, but before it is written to a file."""
        self.document.write(self.to_string())

    def _build_lane_points(self, lane):
        previous_waypoint = None
        previous_monolane_point = None
        last_line_heading = None
        for waypoint in lane.get_waypoints():
            monolane_point = self._monolane_point_from_waypoint(waypoint)
            monolane_point_id = self.monolane_id_mapper.formatted_id_for(waypoint)
            self.monolane['maliput_monolane_builder']['points'][monolane_point_id] = monolane_point
            if previous_waypoint is not None:
                if previous_waypoint.is_arc_start_connection() and waypoint.is_arc_end_connection():
                    if last_line_heading is not None:
                        previous_monolane_point['xypoint'][2] = last_line_heading
                else:
                    previous_heading = math.degrees(previous_waypoint.center.yaw(waypoint.center))
                    last_line_heading = previous_heading
                    previous_monolane_point['xypoint'][2] = previous_heading
            previous_waypoint = waypoint
            previous_monolane_point = monolane_point

    def _monolane_point_from_waypoint(self, waypoint):
        point = OrderedDict()
        point['xypoint'] = [float(waypoint.center.x), float(waypoint.center.y), 0]
        point['zpoint'] = [float(waypoint.center.z), 0, 0, 0]
        return point

    def to_string(self, Dumper=yaml.Dumper, **kwds):
        """Convert the current monolane data into its yaml version.

        Preserves order of the keys inside of 'maliput_monolane_builder'.
        """
        header = """# -*- yaml -*-
---
# distances are meters; angles are degrees.
"""

        class OrderedDumper(yaml.Dumper):
            pass

        def _dict_representer(dumper, data):
            return dumper.represent_mapping(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                data.items())

        OrderedDumper.add_representer(OrderedDict, _dict_representer)
        return header + yaml.dump(self.monolane, None, OrderedDumper, **kwds)
