from file_generator import FileGenerator
from rndf_id_mapper import RNDFIdMapper
from geometry.point import Point
import math


class RNDFGenerator(FileGenerator):

    def __init__(self, city, origin):
        super(RNDFGenerator, self).__init__(city)
        self.origin = origin
        self.id_mapper = RNDFIdMapper(city)

    def start_document(self):
        self.id_mapper.run()
        self.segment_id = 0

    def end_city(self, city):
        self._wrap_document_with_contents_for(city)

    def start_street(self, road):
        self.segment_id = self.segment_id + 1
        street_contents = self._contents_for(road, segment_id=self.segment_id)
        self._append_to_document(street_contents)

    def start_trunk(self, road):
        self.segment_id = self.segment_id + 1
        trunk_contents = self._contents_for(road, segment_id=self.segment_id)
        self._append_to_document(trunk_contents)

    # Transformation taken from
    # http://gis.stackexchange.com/questions/107992/
    # converting-from-an-x-y-coordinate-system-to-latitude-longitude
    def translate_point(self, point):
        meters_per_degree_lat = 111319.9
        meters_per_degree_lon = meters_per_degree_lat * math.cos(self.origin.x)
        lat = self.origin.y + (point.y / meters_per_degree_lat)
        lon = self.origin.x + (point.x / meters_per_degree_lon)
        return (lat, lon)

    def city_template(self):
        return """
        RNDF_name\t{{model.name}}
        num_segments\t{{model.roads_count()}}
        num_zones\t0
        format_version\t1.0
        {{inner_contents}}
        end_file"""

    def street_template(self):
        return """
        segment\t{{segment_id}}
        num_lanes\t1
        segment_name\t{{model.name}}
        lane\t{{segment_id}}.1
        num_waypoints\t{{model.points_count()}}
        lane_width\t{{model.width}}
        {% for point in model.points %}
        {% set latlon = generator.translate_point(point) %}
        {% set lat = latlon[0] %}
        {% set lon = latlon[1] %}
        {{segment_id}}.1.{{loop.index}}\t{{lat|round(6)}}\t{{lon|round(6)}}
        {% endfor %}
        end_lane
        end_segment"""

    def trunk_template(self):
        """Consider trunks as streets. We need to fix this"""
        return self.street_template()
