from city_visitor import CityVisitor


class OpenDriveIdMapper(CityVisitor):

    def run(self):
        self.segment_id = 0

    def id_for(self, object):
        self.segment_id = self.segment_id + 1
        return self.segment_id
