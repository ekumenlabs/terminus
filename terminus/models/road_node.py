from geometry.point import Point


class RoadNode(object):
    def __init__(self, center, name=None):
        self.center = center
        self.name = name

    @classmethod
    def on(cls, *args, **kwargs):
        return cls(Point(*args, **kwargs))

    def get_waypoints_for(self, road):
        raise NotImplementedError()

    def added_to(self, road):
        raise NotImplementedError()

    def removed_from(self, road):
        raise NotImplementedError()

    def connected_waypoints_for(self, waypoint):
        raise NotImplementedError()

    def involved_roads(self):
        raise NotImplementedError()

    def involved_roads_except(self, target_road):
        return filter(lambda road: road is not target_road, self.involved_roads())

    def __ne__(self, other):
        return not self.__eq__(other)
