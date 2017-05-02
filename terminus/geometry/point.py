"""
Copyright (C) 2017 Open Source Robotics Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import math
import shapely.geometry
from numbers import Number


class Point(object):
    def __init__(self, x, y, z=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

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

    def closest_point_to(self, other):
        return self

    def clone(self):
        return Point(self.x, self.y, self.z)

    def negated(self):
        return Point(-self.x, -self.y, -self.z)

    def orthogonal_vector(self):
        return Point(-self.y, self.x)

    def orthonormal_vector(self):
        return self.orthogonal_vector().normalized()

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

    def angle(self, other):
        """
        Returns the angle from self to other in degrees between -180 and 180
        """
        v1 = self.normalized()
        v2 = other.normalized()
        angle = math.degrees(math.atan2(v2.y, v2.x) - math.atan2(v1.y, v1.x))
        if angle <= -180:
            angle = angle + 360
        if angle > 180:
            angle = angle - 360
        return angle

    def is_collinear_with(self, other_point, tolerance=1e-5):
        """
        We assume that the receiver and the parameter represent vectors
        """
        return abs(self.angle(other_point)) <= tolerance

    def norm(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def norm_squared(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def normalized(self):
        length = self.norm()
        return Point(self.x / length, self.y / length, self.z / length)

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

    def rounded(self):
        return self.rounded_to(7)

    def mid_point(self, other):
        return (self + other) * (0.5)

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

    def __lt__(self, other):
        return self.x < other.x and self.y < other.y and self.z < other.z

    def __le__(self, other):
        return self.x <= other.x and self.y <= other.y and self.z <= other.z

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return other <= self
