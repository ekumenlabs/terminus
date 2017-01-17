from city_visitor import CityVisitor


class OpenDriveIdMapper(CityVisitor):

    def run(self):
        self.segment_id = 0
        self.waypoint_id = 0
        self.object_to_id_level_1 = {}
        self.object_to_id_level_2 = {}
        self.id_to_object = {}

    def id_for(self, object):
        self.segment_id = self.segment_id + 1
        return self.segment_id
        # try:
        #     return self.object_to_id_level_1[id(object)]
        # except KeyError:
        #     return self.object_to_id_level_2[object]

    def object_for(self, id):
        return self.id_to_object[id]

    def map_road(self, road):
        self.segment_id = self.segment_id + 1
        self.waypoint_id = 0
        self._register(str(self.segment_id), road)
        for waypoint in road.get_waypoints():
            self.waypoint_id = self.waypoint_id + 1
            rndf_id = str(self.segment_id) + '.1.' + str(self.waypoint_id)
            self._register(rndf_id, waypoint)

    def start_street(self, street):
        self.map_road(street)

    def start_trunk(self, trunk):
        self.map_road(trunk)

    def _register(self, rndf_id, object):
        """We do some caching by id, to avoid computing hashes if they are
        expensive, but keep the hash-based dict as a fallback"""
        self.object_to_id_level_1[id(object)] = rndf_id
        self.object_to_id_level_2[object] = rndf_id
        self.id_to_object[rndf_id] = object
