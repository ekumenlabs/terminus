from road_node import RoadNode
from waypoint import Waypoint


class SimpleNode(RoadNode):

    def added_to(self, road):
        self.road = road

    def removed_from(self, road):
        self.road = None

    def get_waypoints_for(self, road):
        if (self.road is not road):
            return None
        return [Waypoint(road, self, self.center)]

    def connected_waypoints_for(self, waypoint):
        return []

    def involved_roads(self):
        return [self.road]

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.center == other.center

    def __hash__(self):
        return hash((self.__class__, self.center))

    def __repr__(self):
        return "SimpleNode @ " + str(self.center)
