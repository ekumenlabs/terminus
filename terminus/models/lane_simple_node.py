from lane_node import LaneNode
from waypoint import Waypoint


class LaneSimpleNode(LaneNode):

    def __init__(self, center, main_lane, road_node):
        self.lane = None
        super(LaneSimpleNode, self).__init__(center, main_lane, road_node)

    def added_to(self, lane):
        self.lane = lane

    def involved_lane(self):
        return [self.lane]

    def get_waypoints_for(self, lane):
        if (self.lane is not lane):
            return None
        return [Waypoint(lane, self, self.center)]

    def connected_waypoints_for(self, waypoint):
        return []

    def __repr__(self):
        return "LaneSimpleNode @ " + str(self.center)


    # def removed_from(self, road):
    #     self.road = None





