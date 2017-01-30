from geometry.point import Point
from road_node import RoadNode
from shapely.geometry import LineString
from waypoint import Waypoint


class RoadIntersectionNode(RoadNode):

    def __init__(self, center, name=None):
        super(RoadIntersectionNode, self).__init__(center, name)
        self.roads = []

    def is_intersection(self):
        return True

    def added_to(self, road):
        self._add_road(road)

    def removed_from(self, road):
        self.roads.remove(road)

    def involved_roads(self):
        return self.roads

    def _add_road(self, road):
        self.roads.append(road)

    def __repr__(self):
        return "RoadIntersectionNode @ " + str(self.center)
