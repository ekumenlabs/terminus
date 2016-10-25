from file_generator import FileGenerator
from shapely.geometry import Point
try:
    from cStringIO import StringIO
except:
    from io import StringIO

class RNDFGenerator(FileGenerator):

    def __init__(self, city, origin):
        super(RNDFGenerator, self).__init__(city)
        self.origin = origin

    def generate(self):
        self.segment_id = 0
        self.document = StringIO()
        self.city.accept(self)
        return self.document.getvalue()

    def start_city(self, city):
        self.document.write(self._contents_for(city))

    def start_street(self, road):
        self.segment_id = self.segment_id + 1
        self.document.write(self._contents_for(road, segment_id=self.segment_id))

    def translate_point(self, point):
        meters_per_degree = 111319.9
        x = point.x / meters_per_degree + self.origin.x
        y = point.y / meters_per_degree + self.origin.y
        return Point(x,y)

    def city_template(self):
        return """
        RNDF_name\t{{model.name}}
        num_segments\t{{model.roads_count()}}
        num_zones\t0
        format_version\t1.0"""

    def street_template(self):
        return """
        segment\t{{segment_id}}
        num_lanes\t1
        segment_name\t{{model.name}}
        lane\t{{segment_id}}.1
        num_waypoints\t0
        lane_width\t{{model.width}}
        {% for point in model.points %}
        {% set latlon = generator.translate_point(point) %}
        {{segment_id}}.1.{{loop.index}}\t{{latlon.x|round(6)}}\t{{latlon.y|round(6)}}
        {% endfor %}
        end_lane"""

    def trunk_template(self):
        """Consider trunks as streets. We need to fix this"""
        return self.street_template()
