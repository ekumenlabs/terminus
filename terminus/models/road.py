from city_model import CityModel


class Road(CityModel):
    def __init__(self, width, name=None):
        super(Road, self).__init__(name)
        self.width = width
        self.points = []

    @classmethod
    def from_points(cls, array_of_points):
        road = cls()
        for point in array_of_points:
            road.add_point(point)
        return road

    def add_point(self, point):
        self.points.append(point)

    def points_count(self):
        return len(self.points)

    def get_width(self):
        return width

    def set_width(self, width):
        self.width = width

    # This implementation is temporal and we will soon replace it
    # with the return of proper street waypoints.
    def get_waypoints(self):
        return self.points

    def waypoints_count(self):
        return len(self.get_waypoints())

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and \
               (self.width == other.width) and \
               (self.points == other.points)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.width, tuple(self.points)))

    def __repr__(self):
        return "%s: " % self.__class__ + reduce(lambda acc, point: acc +
                                                "%s," % str(point),
                                                self.points, '')
