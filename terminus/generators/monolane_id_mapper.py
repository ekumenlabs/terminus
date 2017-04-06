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

from city_visitor import CityVisitor
from models.lines_and_arcs_builder import LinesAndArcsBuilder


class MonolaneIdMapper(CityVisitor):
    # TODO: Code is almost the same as the RNDF id mapper. Refactor.

    def run(self):
        self.lane_id = 0
        self.waypoint_id = 0
        self.object_to_id_level_1 = {}
        self.object_to_id_level_2 = {}
        self.id_to_object = {}
        super(MonolaneIdMapper, self).run()

    def id_for(self, object):
        try:
            return self.object_to_id_level_1[id(object)]
        except KeyError:
            return self.object_to_id_level_2[object]

    def formatted_id_for(self, object):
        id = self.id_for(object)
        return "{0}_{1}_{2}".format(id[0], id[1], id[2])

    def object_for(self, id):
        return self.id_to_object[id]

    def map_road(self, road):
        self.road_id = road.name
        self.lane_id = 0

    def start_street(self, street):
        self.map_road(street)

    def start_trunk(self, trunk):
        self.map_road(trunk)

    def start_lane(self, lane):
        self.lane_id = self.lane_id + 1
        self.waypoint_id = 0
        for waypoint in lane.waypoints_using(LinesAndArcsBuilder):
            self.waypoint_id = self.waypoint_id + 1
            waypoint_uid = (self.road_id, self.lane_id, self.waypoint_id)
            self._register(waypoint_uid, waypoint)

    def _register(self, object_id, object):
        """We do some caching by id, to avoid computing hashes if they are
        expensive, but keep the hash-based dict as a fallback"""
        self.object_to_id_level_1[id(object)] = object_id
        self.object_to_id_level_2[object] = object_id
        self.id_to_object[object_id] = object
