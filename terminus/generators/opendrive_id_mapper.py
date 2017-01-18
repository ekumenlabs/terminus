from city_visitor import CityVisitor


# This class is inteded to handle ids of junctions and roads.
# All the ids should be unique, so this class will handle that, and the
# reference to the objects it gives the new id. This class will have
# development further.
class OpenDriveIdMapper(CityVisitor):

    def run(self):
        self.segment_id = 0

    def id_for(self, object):
        self.segment_id = self.segment_id + 1
        return self.segment_id
