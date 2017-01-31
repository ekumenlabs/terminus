from road_node import RoadNode
from waypoint import Waypoint


class RoadSimpleNode(RoadNode):

    def __init__(self, center, name=None):
        super(RoadSimpleNode, self).__init__(center, name)
        self.road = None

    def is_intersection(self):
        return False

    def added_to(self, road):
        self.road = road

    def removed_from(self, road):
        self.road = None

    def involved_roads(self):
        return [self.road]

    def __repr__(self):
        return "RoadSimpleNode @ " + str(self.center)
