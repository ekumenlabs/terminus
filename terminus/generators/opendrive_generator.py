from file_generator import FileGenerator
from geometry.point import Point
from geometry.latlon import LatLon
from city_visitor import CityVisitor
from opendrive_id_mapper import OpenDriveIdMapper
from opendrive_id_mapper import Junction
from opendrive_id_mapper import Connection
import math


class OpenDriveGenerator(FileGenerator):

    def __init__(self, city, origin):
        super(OpenDriveGenerator, self).__init__(city)
        self.origin = origin
        self.id_mapper = OpenDriveIdMapper(city)

    def start_document(self):
        self.id_mapper.run()

    def end_city(self, city):
        self._wrap_document_with_contents_for(city)

    def start_street(self, street):
        self.start_road(street)

    def start_trunk(self, street):
        self.start_road(street)

    def start_road(self, road):
        pass

    def city_template(self):
        return """
        <?xml version="1.0" standalone="yes"?>
          <OpenDRIVE xmlns="http://www.opendrive.org">
            <header revMajor="1" revMinor="1" name="{{model.name}}" version="1.00" north="0.0" south="0.0" east="0.0" west="0.0" maxRoad="{{generator.get_last_road_id()}}" maxJunc="{{generator.get_last_junction_id()}}" maxPrg="0">
            </header>
            {% for road in generator.get_roads() %}
            {%     set points = road.get_waypoint_positions() %}
            {%     set distances = road.get_waypoint_distances() %}
            {%     set angles = road.get_waypoints_yaws() %}
            <road name="{{road.name}}" length="{{road.length()}}" id="{{road.id}}">
              <type s="0.0" type="town" junction="{{road.junction_id}}"/>
              <link>
            {%     if road.predecessor: %}
                <predecessor elementType="{{road.predecessor_type}}" elementId="{{road.predecessor}}" {% if road.predecessor_type != 'junction': %}contactPoint="start"{% endif %} />
            {%     endif %}
            {%     if road.successor: %}
                <successor elementType="{{road.successor_type}}" elementId="{{road.successor}}" contactPoint="end" />
            {%     endif %}
              </link>
              <planView>
              {% for i in range(road.waypoints_count() - 1)    %}
                <geometry s="{{road.length(0,i)}}" x="{{points[i].x}}" y="{{points[i].y}}" hdg="{{angles[i]}}" length="{{distances[i]}}">
                  <line/>
                </geometry>
              {% endfor %}
              </planView>
              <elevationProfile>
                  <elevation s="0.0e+00" a="0.0" b="0.0" c="0.0" d="0.0"/>
              </elevationProfile>
              <lateralProfile>
              </lateralProfile>
              <lanes>
                  <laneSection s="0.0">
                      <center>
                          <lane id="0" type="driving" level= "0">
                              <link>
                              </link>
                              <roadMark sOffset="0.0" type="none" weight="standard" color="standard" width="1.3e-01"/>
                          </lane>
                      </center>
                      <right>
                          <lane id="-1" type="driving" level= "0">
                              <link>
                              </link>
                              <roadMark sOffset="0.0" type="solid" weight="standard" color="standard" width="1.3e-01"/>
                              <width sOffset="0.0" a="{{road.width}}" b="0.0" c="0.0" d="0.0"/>
                          </lane>
                      </right>
                  </laneSection>
              </lanes>
              <objects>
              </objects>
              <signals>
              </signals>
            </road>
            {% endfor %}
            {% for junction in generator.get_junctions() %}
              <junction name="" id="{{junction.id}}">
            {%     for i in range(0, generator.get_junction_link_count(junction)) %}
                <connection id="{{i}}" incomingRoad="{{junction.links[i].incomming_road}}" connectingRoad="{{junction.links[i].connecting_road}}" contactPoint="start">
                  <laneLink from="1" to="1"/>
                </connection>
            {%     endfor %}
              </junction>
            {% endfor %}
        </OpenDRIVE>"""

    # We don't have support for multilane roads, so we should
    # correct the lane creation for roads. We are creating only one lane to the
    # right of the base line and no offset is set.
    def road_template(self):
        return """"""

    def street_template(self):
        return self.road_template()

    def trunk_template(self):
        return self.road_template()

    def get_last_road_id(self):
        return self.id_mapper.road_id_max

    def get_last_junction_id(self):
        return self.id_mapper.junction_id_max

    def get_roads(self):
        return self.id_mapper.get_od_roads_as_list()

    def get_junctions(self):
        return self.id_mapper.junctions

    def get_junction_link_count(self, junction):
        return len(junction.links)
