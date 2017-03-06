"""
/*
 * Copyright (C) 2017 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
"""
from file_generator import FileGenerator
from rndf_id_mapper import RNDFIdMapper
from geometry.point import Point
from geometry.latlon import LatLon
import math


# TODO: In the near future we should do some benchmarking, as
# road generation now is taking too long (after adding the new exit waypoint
# computation)
class RNDFGenerator(FileGenerator):

    def __init__(self, city, origin):
        super(RNDFGenerator, self).__init__(city)
        self.origin = origin
        self.id_mapper = RNDFIdMapper(city)

    def start_document(self):
        self.id_mapper.run()

    def end_city(self, city):
        self._wrap_document_with_contents_for(city)

    def start_lane(self, lane):
        lane_id = self.id_for(lane)
        lane_contents = self._contents_for(lane, lane_id=lane_id)
        self._append_to_document(lane_contents)

    def start_road(self, road):
        segment_id = self.id_for(road)
        street_contents = self._contents_for(road, segment_id=segment_id)
        self._append_to_document(street_contents)

    def start_street(self, street):
        self.start_road(street)

    def start_trunk(self, street):
        self.start_road(street)

    def end_road(self, road):
        self._append_to_document("""
        end_segment""")

    def end_street(self, street):
        self.end_road(street)

    def end_trunk(self, street):
        self.end_road(street)

    def id_for(self, object):
        return self.id_mapper.id_for(object)

    def meters_to_feet(self, meters):
        return int(meters * 3.28084)

    def waypoint_connections_for(self, road):
        exit_waypoints = filter(lambda waypoint: waypoint.is_exit(), road.get_waypoints())
        waypoint_connections = []
        for exit_waypoint in exit_waypoints:
            for entry_waypoint in exit_waypoint.connected_waypoints():
                connection = WaypointConnection(self, exit_waypoint, entry_waypoint)
                # TODO: Don't know why we sometimes get repeated entry-exit
                # connections. Need to understand and fix this.
                if connection not in waypoint_connections:
                    waypoint_connections.append(connection)
        return waypoint_connections

    def translate_waypoint(self, waypoint):
        center = (waypoint.center.y, waypoint.center.x)
        return self.origin.translate(center)

    # TODO: Put {{inner_contents}} on a different line while keeping RNDF
    # proper format.
    def city_template(self):
        return """
        RNDF_name\t{{model.name}}
        num_segments\t{{model.roads_count()}}
        num_zones\t0
        format_version\t1.0{{inner_contents}}
        end_file"""

    def lane_template(self):
        return """
        lane\t{{lane_id}}
        num_waypoints\t{{model.waypoints_count()}}
        lane_width\t{{generator.meters_to_feet(model.width())}}
        {% for waypoint_connection in generator.waypoint_connections_for(model) %}
        exit\t{{waypoint_connection.exit_id()}}\t{{waypoint_connection.entry_id()}}
        {% endfor %}
        {% for waypoint in model.get_waypoints() %}
        {% set latlon = generator.translate_waypoint(waypoint) %}
        {% set lat = latlon.lat %}
        {% set lon = latlon.lon %}
        {{generator.id_for(waypoint)}}\t{{'{0:0.6f}'.format(lat)}}\t{{'{0:0.6f}'.format(lon)}}
        {% endfor %}
        end_lane"""

    def road_template(self):
        return """
        segment\t{{segment_id}}
        num_lanes\t{{model.lane_count()}}
        segment_name\t{{model.name}}"""

    def street_template(self):
        return self.road_template()

    def trunk_template(self):
        return self.road_template()


class WaypointConnection(object):
    def __init__(self, generator, exit_waypoint, entry_waypoint):
        self.generator = generator
        self.exit_waypoint = exit_waypoint
        self.entry_waypoint = entry_waypoint

    def exit_id(self):
        return self.generator.id_for(self.exit_waypoint)

    def entry_id(self):
        return self.generator.id_for(self.entry_waypoint)

    def __eq__(self, other):
        return (self.exit_waypoint == other.exit_waypoint) and \
               (self.entry_waypoint == other.entry_waypoint)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.exit_waypoint, self.entry_waypoint))
