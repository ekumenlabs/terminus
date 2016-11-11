from file_generator import FileGenerator
from rndf_id_mapper import RNDFIdMapper
from geometry.point import Point
import math
#import pprint

#pp = pprint.PrettyPrinter(indent=4)

class RNDFGenerator(FileGenerator):

    def __init__(self, city, origin):
        super(RNDFGenerator, self).__init__(city)
        self.origin = origin
        self.id_mapper = RNDFIdMapper(city)

    def start_document(self):
        self.id_mapper.run()
#        pp.pprint(self.id_mapper.id_to_object)

    def end_city(self, city):
        self._wrap_document_with_contents_for(city)

    def start_road(self, road):
        segment_id = self.id_for(road)
        street_contents = self._contents_for(road, segment_id=segment_id)
        self._append_to_document(street_contents)

    def start_street(self, street):
        self.start_road(street)

    def start_trunk(self, street):
        self.start_road(street)

    def id_for(self, object):
        return self.id_mapper.id_for(object)

    def waypoint_connections_for(self, road):
        exit_waypoints = filter(lambda waypoint: waypoint.is_exit(), road.get_waypoints())
        waypoint_connections = []
        for exit_waypoint in exit_waypoints:
            for entry_waypoint in exit_waypoint.connected_waypoints():
                waypoint_connections.append(WaypointConnection(self,
                                                                exit_waypoint,
                                                                entry_waypoint))
        return waypoint_connections

    # Transformation taken from
    # http://gis.stackexchange.com/questions/107992/
    # converting-from-an-x-y-coordinate-system-to-latitude-longitude
    def translate_waypoint(self, waypoint):
        center = waypoint.center
        meters_per_degree_lat = 111319.9
        meters_per_degree_lon = meters_per_degree_lat * math.cos(self.origin.x)
        lat = self.origin.y + (center.y / meters_per_degree_lat)
        lon = self.origin.x + (center.x / meters_per_degree_lon)
        return (lat, lon)

    # TODO: Put {{inner_contents}} on a different line while keeping RNDF
    # proper format.
    def city_template(self):
        return """
        RNDF_name\t{{model.name}}
        num_segments\t{{model.roads_count()}}
        num_zones\t0
        format_version\t1.0{{inner_contents}}
        end_file"""

    def street_template(self):
        return """
        segment\t{{segment_id}}
        num_lanes\t1
        segment_name\t{{model.name}}
        lane\t{{segment_id}}.1
        num_waypoints\t{{model.waypoints_count()}}
        lane_width\t{{model.width}}
        {% for waypoint_connection in generator.waypoint_connections_for(model) %}
        exit\t{{waypoint_connection.exit_id()}}\t{{waypoint_connection.entry_id()}}
        {% endfor %}
        {% for waypoint in model.get_waypoints() %}
        {% set latlon = generator.translate_waypoint(waypoint) %}
        {% set lat = latlon[0] %}
        {% set lon = latlon[1] %}
        {{generator.id_for(waypoint)}}\t{{lat|round(6)}}\t{{lon|round(6)}}
        {% endfor %}
        end_lane
        end_segment"""

    def trunk_template(self):
        """Consider trunks as streets. We need to fix this"""
        return self.street_template()

class WaypointConnection(object):
    def __init__(self, generator, exit_waypoint, entry_waypoint):
        self.generator = generator
        self.exit_waypoint = exit_waypoint
        self.entry_waypoint = entry_waypoint

    def exit_id(self):
        return self.generator.id_for(self.exit_waypoint)

    def entry_id(self):
        return self.generator.id_for(self.entry_waypoint)
