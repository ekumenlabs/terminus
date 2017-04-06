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

import math

from geometry.point import Point
from geometry.latlon import LatLon
from models.polyline_builder import PolylineBuilder
from file_generator import FileGenerator
from rndf_id_mapper import RNDFIdMapper


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

    def waypoints_count_for(self, lane):
        return len(self.waypoints_for(lane))

    def waypoints_for(self, lane):
        return lane.waypoints_using(PolylineBuilder)

    def waypoint_connections_for(self, lane):
        exit_waypoints = filter(lambda waypoint: waypoint.is_exit(), self.waypoints_for(lane))
        waypoint_connections = []
        for exit_waypoint in exit_waypoints:
            for connection in exit_waypoint.out_connections():
                exit_id = self.id_for(connection.start_waypoint())
                entry_id = self.id_for(connection.end_waypoint())
                waypoint_connections.append((exit_id, entry_id))
        return waypoint_connections

    def translate_point(self, point):
        center = (point.y, point.x)
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
        num_waypoints\t{{generator.waypoints_count_for(model)}}
        lane_width\t{{generator.meters_to_feet(model.width())}}
        {% for waypoint_connection in generator.waypoint_connections_for(model) %}
        exit\t{{waypoint_connection[0]}}\t{{waypoint_connection[1]}}
        {% endfor %}
        {% for waypoint in generator.waypoints_for(model) %}
        {% set latlon = generator.translate_point(waypoint.center()) %}
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
