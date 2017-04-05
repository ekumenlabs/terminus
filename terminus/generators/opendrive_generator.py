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

from file_generator import FileGenerator
from geometry.point import Point
from geometry.latlon import LatLon
from city_visitor import CityVisitor
from opendrive_id_mapper import OpenDriveIdMapper
import math


class OpenDriveGenerator(FileGenerator):

    def __init__(self, city):
        super(OpenDriveGenerator, self).__init__(city)
        self.id_mapper = OpenDriveIdMapper(city)

    def start_document(self):
        self.id_mapper.run()

    def end_city(self, city):
        self._wrap_document_with_contents_for(city)

    def start_street(self, street):
        '''
        For the time being we will assume that a Street can only contain a
        single lane, at the center. Otherwise we fail loudly.
        We will generalize this in the future.
        '''
        if street.lane_count() != 1 or street.lane_at(0).offset() != 0:
            raise RuntimeError("Only streets with a single lane at the center are currently supported")
        street_id = self.id_for(street)
        street_content = self._contents_for(street, segment_id=street_id)
        self._append_to_document(street_content)

    def start_trunk(self, trunk):
        trunk_id = self.id_for(trunk)
        trunk_content = self._contents_for(trunk, segment_id=trunk_id)
        self._append_to_document(trunk_content)

    def id_for(self, object):
        return self.id_mapper.id_for(object)

    def sorted_right_lanes(self, road):
        right_lanes = filter(lambda lane: lane.offset() > 0, road.lanes())
        right_lanes.sort(key=lambda lane: lane.offset())
        lane_id = 0
        tuples = []
        for lane in right_lanes:
            lane_id = lane_id - 1
            tuples.append((lane_id, lane))
        return tuples

    def has_right_lanes(self, road):
        return len(self.sorted_right_lanes(road)) != 0

    def sorted_left_lanes(self, road):
        left_lanes = filter(lambda lane: lane.offset() < 0, road.lanes())
        left_lanes.sort(key=lambda lane: lane.offset())
        lane_id = len(left_lanes) + 1
        tuples = []
        for lane in left_lanes:
            lane_id = lane_id - 1
            tuples.append((lane_id, lane))
        tuples.reverse()
        return tuples

    def has_left_lanes(self, road):
        return len(self.sorted_left_lanes(road)) != 0

    def reset_accumulated_width(self):
        self.accumulated_width = 0

    def accumulate_width_for(self, lane):
        self.accumulated_width = abs(lane.external_offset())

    def width_for(self, lane):
        return abs(lane.external_offset()) - self.accumulated_width

    def city_template(self):
        return """
        <?xml version="1.0" standalone="yes"?>
        <OpenDRIVE>
          <header revMajor="1" revMinor="1" name="{{model.name}}" version="1.00" north="0.0" south="0.0" east="0.0" west="0.0">
          </header>
          {{inner_contents}}
        </OpenDRIVE>"""

    def street_template(self):
        return """
            {% set points = model.get_waypoint_positions() %}
            {% set distances = model.get_waypoint_distances() %}
            {% set angles = model.get_waypoints_yaws() %}
            <road name="{{model.name}}" length="{{model.length()}}" id="{{segment_id}}">
              <type s="0.0" type="town"/>
              <planView>
              {% for i in range(model.waypoints_count() - 1)    %}
                <geometry s="{{model.length(0,i)}}" x="{{points[i].x}}" y="{{points[i].y}}" hdg="{{angles[i]}}" length="{{distances[i]}}">
                  <line/>
                </geometry>
              {% endfor %}
              </planView>
              <elevationProfile>
                  <elevation s="0.0" a="0.0" b="0.0" c="0.0" d="0.0"/>
              </elevationProfile>
              <lateralProfile>
              </lateralProfile>
              <lanes>
                  <laneOffset s="0.0" a="{{model.width() / 2.0}}" b="0.0" c="0.0" d="0.0"/>
                  <laneSection s="0.0">
                      <center>
                          <lane id="0" type="driving" level="false">
                              <link>
                              </link>
                              <roadMark sOffset="0.0" type="solid" weight="standard" color="standard" width="1.3e-01">
                              </roadMark>
                          </lane>
                      </center>
                      <right>
                          <lane id="-1" type="driving" level="false">
                              <link>
                              </link>
                              <width sOffset="0.0" a="{{model.width()}}" b="0.0" c="0.0" d="0.0"/>
                              <roadMark sOffset="0.0" type="solid" weight="standard" color="standard" width="1.3e-01">
                              </roadMark>
                          </lane>
                      </right>
                  </laneSection>
              </lanes>
              <objects>
              </objects>
              <signals>
              </signals>
            </road>"""

    def trunk_template(self):
        return """
            {% set points = model.get_waypoint_positions() %}
            {% set distances = model.get_waypoint_distances() %}
            {% set angles = model.get_waypoints_yaws() %}
            <road name="{{model.name}}" length="{{model.length()}}" id="{{segment_id}}">
              <type s="0.0" type="town"/>
              <planView>
              {% for i in range(model.waypoints_count() - 1)    %}
                <geometry s="{{model.length(0,i)}}" x="{{points[i].x}}" y="{{points[i].y}}" hdg="{{angles[i]}}" length="{{distances[i]}}">
                  <line/>
                </geometry>
              {% endfor %}
              </planView>
              <elevationProfile>
                  <elevation s="0.0" a="0.0" b="0.0" c="0.0" d="0.0"/>
              </elevationProfile>
              <lateralProfile>
              </lateralProfile>
              <lanes>
                  <laneSection s="0.0">
                      {% if generator.has_left_lanes(model) %}
                      {% do generator.reset_accumulated_width() %}
                      <left>
                        {% for (id, lane) in generator.sorted_left_lanes(model) %}
                          <lane id="{{id}}" type="driving" level="false">
                              <link>
                              </link>
                              <width sOffset="0.0" a="{{generator.width_for(lane)}}" b="0.0" c="0.0" d="0.0"/>
                              {% if loop.last %}
                                <roadMark sOffset="0.0" type="solid" weight="standard" color="standard" width="1.3e-01">
                                </roadMark>
                              {% else %}
                                <roadMark sOffset="0.0" type="broken" weight="standard" color="standard" width="1.3e-01">
                                </roadMark>
                              {% endif %}
                          {% do generator.accumulate_width_for(lane) %}
                          </lane>
                        {% endfor %}
                      </left>
                      {% endif -%}
                      <center>
                          <lane id="0" type="driving" level="false">
                              <link>
                              </link>
                              <roadMark sOffset="0.0" type="broken" weight="standard" color="standard" width="1.3e-01">
                              </roadMark>
                          </lane>
                      </center>
                      {% if generator.has_right_lanes(model) %}
                      {% do generator.reset_accumulated_width() %}
                      <right>
                        {% for (id, lane) in generator.sorted_right_lanes(model) %}
                          <lane id="{{id}}" type="driving" level="false">
                              <link>
                              </link>
                              <width sOffset="0.0" a="{{generator.width_for(lane)}}" b="0.0" c="0.0" d="0.0"/>
                              {% if loop.last %}
                                <roadMark sOffset="0.0" type="solid" weight="standard" color="standard" width="1.3e-01">
                                </roadMark>
                              {% else %}
                                <roadMark sOffset="0.0" type="broken" weight="standard" color="standard" width="1.3e-01">
                                </roadMark>
                              {% endif %}
                          {% do generator.accumulate_width_for(lane) %}
                          </lane>
                        {% endfor %}
                      </right>
                      {% endif -%}
                  </laneSection>
              </lanes>
              <objects>
              </objects>
              <signals>
              </signals>
            </road>"""
