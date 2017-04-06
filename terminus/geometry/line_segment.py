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

from geometry.point import Point

# Avoid module circular dependencies
import geometry.arc


class LineSegment(object):

    def __init__(self, point_a, point_b):
        self.a = point_a
        self.b = point_b

    @classmethod
    def from_tuples(cls, t1, t2):
        return cls(Point.from_tuple(t1), Point.from_tuple(t2))

    def includes_point(self, point, buffer=0.001):
        # First check if the a->b and a->point are collinear. If they are,
        # the cross product should be zero (with some buffer for errors)
        cross_product = (self.b - self.a).cross_product(point - self.a)
        if cross_product.norm() > buffer:
            return False

        # If the dot product between a->b and a->point is negative then
        # point lays outside the a---b boundaries
        dot_product = (self.b - self.a).dot_product(point - self.a)
        if dot_product < 0:
            return False

        # Finally if it is greater than the a->b squared distance it also lays
        # out of bounds
        distance = self.a.squared_distance_to(self.b)
        if dot_product > distance:
            return False

        return True

    def start_point(self):
        return self.a

    def end_point(self):
        return self.b

    def direction_vector(self):
        return self.b - self.a

    def length(self):
        return self.direction_vector().norm()

    def translate_by(self, point):
        return LineSegment(self.start_point() + point, self.end_point() + point)

    def is_orthogonal_to(self, line_segment, buffer=0.001):
        return abs((self.b - self.a).dot_product(line_segment.b - line_segment.a)) < buffer

    def _find_line_segment_intersection(self, segment):
        v1 = self.direction_vector()
        p1 = self.start_point()

        v2 = segment.direction_vector()
        p2 = segment.start_point()

        v3 = p2 - p1
        v4 = p1 - p2

        v1_cross_v2 = v1.cross_product(v2)
        v2_cross_v1 = v2.cross_product(v1)

        if v1_cross_v2.norm() == 0.0:
            return None

        k1 = v3.cross_product(v2).norm() / v1_cross_v2.norm()

        k2 = v4.cross_product(v1).norm() / v2_cross_v1.norm()

        if (k1 < 0) or (k1 > 1) or (k2 < 0) or (k2 > 1):
            return None

        candidate = p1 + v1 * k1

        if self.includes_point(candidate) and segment.includes_point(candidate):
            return candidate
        else:
            return None

    def _find_arc_intersection(self, arc):
        local_segment = self.translate_by(arc.center_point().negated())
        local_segment_vector = local_segment.direction_vector()

        a = local_segment_vector.norm_squared()
        b = 2 * ((local_segment_vector.x * local_segment.start_point().x) + (local_segment_vector.y * local_segment.start_point().y))
        c = local_segment.start_point().norm_squared() - (arc.radius() ** 2)

        delta = (b ** 2) - (4 * a * c)

        if delta < 0:
            # No intersection
            return None
        elif delta == 0.0:
            # Exactly one intersection (tangent)
            # Note that we no longer use the local coordinates
            u = -b / (2 * a)
            candidate = self.start_point() + (local_segment_vector * u)
            if self.includes_point(candidate) and arc.includes_point(candidate):
                return candidate
            else:
                return None
        else:
            delta = math.sqrt(delta)
            u1 = (-b + delta) / (2 * a)
            u2 = (-b - delta) / (2 * a)
            candidates = [self.start_point() + (local_segment_vector * u1),
                          self.start_point() + (local_segment_vector * u2)]
            points = filter(lambda point: self.includes_point(point) and arc.includes_point(point), candidates)
            if not points:
                return None
            elif len(points) == 1:
                return points[0]
            else:
                return points

    def find_intersection(self, other):
        # TODO: Remove this switch statement and make a proper polymorphic delegation
        if isinstance(other, LineSegment):
            return self._find_line_segment_intersection(other)
        elif isinstance(other, geometry.arc.Arc):
            return self._find_arc_intersection(other)
        else:
            raise ValueError("Intersection between {0} and {1} not supported".format(self, other))

    def extend(self, distance):
        """
        Returns a new line segment that has been extended by distance. The extension
        is performed assuming the direction defined as if the line segment was a
        vector going from point a to point b
        """
        dx = self.b.x - self.a.x
        dy = self.b.y - self.a.y
        linelen = math.hypot(dx, dy)

        new_end = Point(self.b.x + dx / linelen * distance,
                        self.b.y + dy / linelen * distance)
        return LineSegment(self.a, new_end)

    def point_at_offset(self, offset):
        """
        Returns a point in the segment considered as an offset from the start of
        the segment. The offset is considered assuming the direction defined as
        if the line segment was a vector going from point a to point b
        """
        if offset > self.length():
            raise ValueError("Offset ({0})is greater than segment length ({1})".format(offset, self.length()))
        dx = self.b.x - self.a.x
        dy = self.b.y - self.a.y
        linelen = math.hypot(dx, dy)

        return Point(self.a.x + dx / linelen * offset,
                     self.a.y + dy / linelen * offset)

    def offset_for_point(self, point):
        if not self.includes_point(point):
            raise ValueError("Point {0} is not included in line segment".format(point))
        return (self.a - point).norm()

    def line_string_points(self):
        return [self.a.clone(), self.b.clone()]

    def start_heading(self):
        return math.degrees(self.a.yaw(self.b))

    def end_heading(self):
        # Heading doesn't change in a line segment
        return self.start_heading()

    def heading_at_offset(self, offset):
        if offset > self.length():
            raise ValueError("Offset ({0}) is greater than segment length ({1})".format(offset, self.length()))
        # Heading doesn't change in a line segment
        return self.start_heading()

    def split_into(self, pairs):
        return map(lambda pair: LineSegment(pair[0], pair[1]), pairs)

    def can_be_merged_with(self, other):
        if self.__class__ is not other.__class__:
            return False
        tentative_merge = LineSegment(self.start_point(), other.end_point())
        return tentative_merge.includes_point(self.end_point())

    def merge(self, other):
        return LineSegment(self.start_point(), other.end_point())

    def is_valid_path_connection(self):
        return self.length() >= 5

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((hash(self.a), hash(self.b)))

    def __repr__(self):
        return "LineSegment({0}, {1})".format(self.a, self.b)
