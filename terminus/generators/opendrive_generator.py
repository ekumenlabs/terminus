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

    def end_city(self, city):
        print "Finishing doc"
        self._wrap_document_with_contents_for(city)

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

    def city_template(self):
        return """
        <?xml version="1.0" standalone="yes"?>
          <OpenDRIVE xmlns="http://www.opendrive.org">
            <header revMajor="1" revMinor="1" name="" version="1.00" north="0.0000000000000000e+00" south="0.0000000000000000e+00" east="0.0000000000000000e+00" west="0.0000000000000000e+00" maxRoad="{{model.roads_count()}}" maxJunc="0" maxPrg="0">
            </header>
            {{inner_contents}}
        </OpenDRIVE>"""

    def street_template(self):
        return """
            {% set points = generator._get_waypoint_positions(model.get_waypoints()) %}
            {% set distances = generator._get_distances(points) %}
            {% set total_length = generator._road_length(distances) %}
            {% set angles = generator._yaws(points) %}
            <road name="{{model.name}}" length="{{total_length}}" id="{{segment_id}}">
              <type s="0.0000000000000000e+00" type="town"/>
              <planView>
              {% for i in range(generator._collection_size(points) - 1)    %}
                <geometry s="{{generator._road_length(distances[:i])}}" x="{{points[i].x}}" y="{{points[i].y}}" hdg="{{angles[i]}}" length="{{distances[i]}}">
                  <line/>
                </geometry>
              {% endfor %}
              </planView>
              <elevationProfile>
                  <elevation s="0.0000000000000000e+00" a="0.0000000000000000e+00" b="0.0000000000000000e+00" c="0.0000000000000000e+00" d="0.0000000000000000e+00"/>
              </elevationProfile>
              <lateralProfile>
              </lateralProfile>
              <lanes>
                  <laneSection s="0.0000000000000000e+00">
                      <center>
                          <lane id="0" type="driving" level= "0">
                              <link>
                              </link>
                              <roadMark sOffset="0.0000000000000000e+00" type="solid" weight="standard" color="standard" width="1.3000000000000000e-01"/>
                              <width sOffset="0.0000000000000000e+00" a="3.7500000000000000e+00" b="0.0000000000000000e+00" c="0.0000000000000000e+00" d="0.0000000000000000e+00"/>
                          </lane>
                      </center>
                  </laneSection>
              </lanes>
              <objects>
              </objects>
              <signals>
              </signals>
            </road>"""

    def trunk_template(self):
        return self.street_template()

    def _distance(self, pA, pB):
        return math.sqrt(math.pow(pA.x - pB.x, 2.0) + math.pow(pA.y - pB.y, 2.0))

    def _road_length(self, distances):
        return math.fsum(distances)

    def _get_distances(self, points):
        distances = []
        for i in range(len(points) - 1):
            distances.append(self._distance(points[i], points[i + 1]))
        return distances

    def _get_waypoint_positions(self, waypoints):
        points = []
        for waypoint in waypoints:
            points.append(waypoint.center)
        return points

    def _collection_size(self, collection):
        return len(collection)

    def _yaw(self, pA, pB):
        dX = pB.x - pA.x
        dY = pB.y - pA.y
        return math.atan2(dY, dX)

    def _yaws(self, points):
        yaws = []
        for i in range(len(points) - 1):
            yaws.append(self._yaw(points[i], points[i + 1]))
        yaws.append(yaws[-1])
        return yaws
