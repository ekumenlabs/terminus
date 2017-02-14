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

    @classmethod
    def from_tuple(cls, tuple):
        if len(tuple) == 3:
            return cls(tuple[0], tuple[1], tuple[2])
        else:
            return cls(tuple[0], tuple[1])

    def min(self, other):
        min_x = min(self.x, other.x)
        min_y = min(self.y, other.y)
        min_z = min(self.z, other.z)
        return Point(min_x, min_y, min_z)

    def max(self, other):
        max_x = max(self.x, other.x)
        max_y = max(self.y, other.y)
        max_z = max(self.z, other.z)
        return Point(max_x, max_y, max_z)

    def to_shapely_point(self):
        return shapely.geometry.Point(self.x, self.y, self.z)

    def to_tuple(self):
        return (self.x, self.y, self.z)

    def cross_product(self, other):
        return Point(self.y * other.z - self.z * other.y,
                     self.z * other.x - self.x * other.z,
                     self.x * other.y - self.y * other.x)

    def dot_product(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def norm(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def squared_distance_to(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2

    def distance_to(self, other):
        return math.sqrt(self.squared_distance_to(other))

    def yaw(self, other):
        diff = other - self
        return math.atan2(diff.y, diff.x)

    def almost_equal_to(self, other, decimals):
        return self.rounded_to(decimals) == other.rounded_to(decimals)

    def rounded_to(self, decimals):
        return Point(round(self.x, decimals),
                     round(self.y, decimals),
                     round(self.z, decimals))

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

    def __abs__(self):
        return Point(abs(self.x), abs(self.y))
