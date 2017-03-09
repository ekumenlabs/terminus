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


class RNDFIdMapper(CityVisitor):
    """Simple city visitor that generates the RNDF ids for segments,
    lanes and waypoints. Ids and objects are stored in two dictionaries,
    so we can later perform lookups in either way"""

    # Note: For the time being we treat streets and trunks in the same way,
    # hence generating a single lane for any of them. This will change in the
    # future, when we properly support multi-lanes trunks.

    def run(self):
        self.segment_id = 0
        self.waypoint_id = 0
        self.lane_id = 0
        self.object_to_id_level_1 = {}
        self.object_to_id_level_2 = {}
        self.id_to_object = {}
        super(RNDFIdMapper, self).run()

    def id_for(self, object):
        try:
            return self.object_to_id_level_1[id(object)]
        except KeyError:
            return self.object_to_id_level_2[object]

    def object_for(self, id):
        return self.id_to_object[id]

    def map_road(self, road):
        self.segment_id = self.segment_id + 1
        self.lane_id = 0
        self._register(str(self.segment_id), road)

    def start_street(self, street):
        self.map_road(street)

    def start_trunk(self, trunk):
        self.map_road(trunk)

    def start_lane(self, lane):
        self.lane_id = self.lane_id + 1
        rndf_lane_id = str(self.segment_id) + '.' + str(self.lane_id)
        self._register(rndf_lane_id, lane)
        self.waypoint_id = 0
        for waypoint in lane.get_waypoints():
            self.waypoint_id = self.waypoint_id + 1
            rndf_waypoint_id = rndf_lane_id + '.' + str(self.waypoint_id)
            self._register(rndf_waypoint_id, waypoint)

    def _register(self, rndf_id, object):
        """We do some caching by id, to avoid computing hashes if they are
        expensive, but keep the hash-based dict as a fallback"""
        self.object_to_id_level_1[id(object)] = rndf_id
        self.object_to_id_level_2[object] = rndf_id
        self.id_to_object[rndf_id] = object
