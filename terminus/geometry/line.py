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

from geometry.point import Point


class Line(object):

    def __init__(self, a, b, c):
        # The coefficients so that the line is a * x + b * y = c
        self.a = a
        self.b = b
        self.c = c

    @classmethod
    def from_points(cls, p1, p2):
        a = p1.y - p2.y
        b = p2.x - p1.x
        c = p1.x * p2.y - p2.x * p1.y
        return cls(a, b, -c)

    @classmethod
    def from_tuples(cls, t1, t2):
        return cls.from_points(Point.from_tuple(t1), Point.from_tuple(t2))

    def intersection(self, other):
        d = float(self.a * other.b - self.b * other.a)
        dx = self.c * other.b - self.b * other.c
        dy = self.a * other.c - self.c * other.a
        if d != 0:
            return Point(dx / d, dy / d)
        else:
            return None

    def __repr__(self):
        return "Line({0}, {1}, {2})".format(self.a, self.b, self.c)
