import math
import shapely.geometry
from numbers import Number


class Point(object):
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def from_shapely(cls, shapely_point):
        if shapely_point._ndim == 3:
            return cls(shapely_point.x, shapely_point.y, shapely_point.z)
        else:
            return cls(shapely_point.x, shapely_point.y)

    def to_shapely_point(self):
        return shapely.geometry.Point(self.x, self.y, self.z)

    def to_tuple(self):
        return (self.x, self.y, self.z)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((hash(self.x) << 4) + hash(self.y) + (hash(self.z) ^ 0xFFFFFF))

    def __repr__(self):
        return "Point({0}, {1}, {2})".format(self.x, self.y, self.z)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if isinstance(other, Number):
            return Point(self.x * other, self.y * other, self.z * other)
        else:
            return Point(self.x * other.x, self.y * other.y, self.z * other.z)

    def __div__(self, other):
        if isinstance(other, Number):
            return Point(self.x / other, self.y / other, self.z / other)
        else:
            return Point(self.x / other.x, self.y / other.y, self.z / other.z)

    def distance_to(self, other):
        return math.sqrt(math.pow(self.x - other.x, 2.0) + math.pow(self.y - other.y, 2.0) + math.pow(self.z - other.z, 2.0))

    def yaw(self, other):
        diff = other - self
        return math.atan2(diff.y, diff.x)
