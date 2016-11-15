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
        self.object_to_id = {}
        self.id_to_object = {}
        super(RNDFIdMapper, self).run()

    def id_for(self, object):
        return self.object_to_id[object]

    def object_for(self, id):
        return self.id_to_object[id]

    def map_road(self, road):
        self.segment_id = self.segment_id + 1
        self.waypoint_id = 0
        # self.object_to_id[(road, id(road))] = self.segment_id
        # self.id_to_object[str(self.segment_id)] = road
        self.object_to_id[road] = self.segment_id
        for waypoint in road.get_waypoints():
            self.waypoint_id = self.waypoint_id + 1
            self.object_to_id[waypoint] = str(self.segment_id) + '.1.' + str(self.waypoint_id)
            self.id_to_object[str(self.segment_id) + '.1.' + str(self.waypoint_id)] = waypoint

    def start_street(self, street):
        self.map_road(street)

    def start_trunk(self, trunk):
        self.map_road(trunk)
