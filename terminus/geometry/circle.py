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

from point import Point


class Circle(object):

    def __init__(self, center, radius):
        self._center = center
        self._radius = float(radius)

    @classmethod
    def from_points_and_radius(cls, start_point, end_point, radius):
        # the path between start_point and end_point is walked in counter_clockwise direction
        # angular length between start_point and end_point is <= 180
        if start_point == end_point:
            raise ValueError("start_point and end_point must be different")
        d = start_point.distance_to(end_point)
        a = math.sqrt(radius ** 2 - (d / 2) ** 2)
        vector = end_point - start_point
        orthonormal_vector = vector.orthonormal_vector()
        mid_point = start_point.mid_point(end_point)
        center = mid_point + (orthonormal_vector * a)
        return cls(center, radius)

    def radius(self):
        return self._radius

    def center(self):
        return self._center

    def almost_equal_to(self, other, decimals=5):
        buffer = 1.0 / (decimals + 1)
        return self.center().almost_equal_to(other.center(), decimals) and \
            abs(self.radius() - other.radius()) < buffer

    def intersection(self, other, decimals=7):

        # Start by ruling out trivial cases
        if self.almost_equal_to(other, decimals):
            return [self]
        if self.center() == other.center() and self.radius() != other.radius():
            return []

        # To find the intersection, we solve the two equations system given by:
        #
        # (Point(x, y) - self.center).norm_squared()  == self.radius ** 2
        # (Point(x, y) - other.center).norm_squared() == other.radius ** 2
        #
        # Express that as M * x + N * y = R

        buffer = 1.0 / (decimals + 1)
        center_delta = other.center() - self.center()
        M = 2 * center_delta.x
        N = 2 * center_delta.y
        self_radius_squared = self.radius() ** 2
        other_radius_squared = other.radius() ** 2
        R = self_radius_squared - other_radius_squared + other.center().norm_squared() - self.center().norm_squared()

        if abs(N) < buffer:
            # If N = 0, then circles are horizontally aligned, hence we need to
            # solve M * x = R.
            x = R / M
            self_delta_x = abs(x - self.center().x)
            other_delta_x = abs(x - other.center().x)

            # Circles are too far away, no intersection
            if self_delta_x > self.radius() or other_delta_x > other.radius():
                return []

            # Single intersection point
            if self.radius() - self_delta_x < buffer and \
               self.radius() - self_delta_x < buffer:
                return [Point(x, self.center().y)]

            # Two intersection points
            delta_y = math.sqrt(self_radius_squared - self_delta_x ** 2)
            y_1 = self.center().y + delta_y
            y_2 = self.center().y - delta_y
            return [Point(x, y_1), Point(x, y_2)]

        # If N != 0, then we can compute y = (R - M * x) / N and replace y by that
        # expression in (Point(x, y) - self.center).norm_squared = self.radius ** 2.
        # We will arrive to a quadratic equation of the form
        # a * x ** 2 + b * x + c = 0,
        # which we will solve, if possible, using the formula
        # x = (-b +/- sqrt(b ** 2 - 4 * a * c)) / (2 * a).

        N_2 = N ** 2
        a = 1 + M ** 2 / N_2
        b = 2 * M * self.center().y / N - 2 * self.center().x - 2 * R * M / N_2
        c = self.center().norm_squared() + (R ** 2) / N_2 - 2 * R * self.center().y / N - self_radius_squared
        if a == 0:
            # If a = 0, then b * x + c = 0
            if b == 0 and abs(c) > buffer:
                return []
            x = -c / b
            y = (R - M * x) / N
            return [Point(x, y)]
        d = b ** 2 - 4 * a * c
        if d < 0:
            return []
        if d == 0:
            x = -b / (2 * a)
            y = (R - M * x) / N
            return [Point(x, y)]
        d_squared = math.sqrt(d)
        x_1 = (-b + d_squared) / (2 * a)
        x_2 = (-b - d_squared) / (2 * a)
        y_1 = (R - M * x_1) / N
        y_2 = (R - M * x_2) / N
        return [Point(x_1, y_1), Point(x_2, y_2)]

    def __eq__(self, other):
        return self.center() == other.center() and self.radius() == other.radius()

    def __hash__(self):
        return hash((self.center(), self.radius()))

    def __repr__(self):
        return "Circle({0}, {1})".format(self.center(), self.radius())
