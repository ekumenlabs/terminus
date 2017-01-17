from file_generator import FileGenerator
from geometry.point import Point
from geometry.latlon import LatLon
from city_visitor import CityVisitor
from opendrive_id_mapper import OpenDriveIdMapper
import math


class OpenDriveGenerator(FileGenerator):

    def __init__(self, city, origin):
        super(OpenDriveGenerator, self).__init__(city)
        self.origin = origin
        self.id_mapper = OpenDriveIdMapper(city)

    # # Start/End document handling
    def start_document(self):
        self.id_mapper.run()

    def end_document(self):
        print "Finishing doc"
        self._wrap_document_with_template('document')

    def start_street(self, street):
        self.start_road(street)

    def start_trunk(self, street):
        self.start_road(street)

    def start_road(self, road):
        road_id = self.id_for(road)
        road_content = self._contents_for(road, segment_id=road_id)
        self._append_to_document(road_content)

    def id_for(self, object):
        return self.id_mapper.id_for(object)

    def document_template(self):
        return """
          <?xml version="1.0" standalone="yes"?>
          <OpenDRIVE xmlns="http://www.opendrive.org">
          <header revMajor="1" revMinor="1" name="" version="1.00" north="0.0000000000000000e+00" south="0.0000000000000000e+00" east="0.0000000000000000e+00" west="0.0000000000000000e+00">
          </header>
          {{inner_contents}}
          </OpenDRIVE>"""

    def road_template(self):
        return """
        <road id={{road_id}} length="">
            <type s="0.0000000000000000e+00" type="town"/>
            <planView>
            </planView>
            <elevationProfile>
                <elevation s="0.0000000000000000e+00" a="0.0000000000000000e+00" b="0.0000000000000000e+00" c="0.0000000000000000e+00" d="0.0000000000000000e+00"/>
            </elevationProfile>
            <lateralProfile>
            </lateralProfile>
            <objects>
            </objects>
            <signals>
            </signals>
        </road>
        """

    def trunk_template(self):
        return self.road_template()
