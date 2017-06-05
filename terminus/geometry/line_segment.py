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
import geometry.circle


class LineSegment(object):

    def __init__(self, point_a, point_b):
        self.a = point_a
        self.b = point_b

    @classmethod
    def from_tuples(cls, t1, t2):
        return cls(Point.from_tuple(t1), Point.from_tuple(t2))

    @classmethod
    def from_point_and_heading(cls, point, heading, length=1):
        heading_in_radians = math.radians(heading)
        dx = math.cos(heading_in_radians) * length
        dy = math.sin(heading_in_radians) * length
        return cls(point, point + Point(dx, dy))

    def includes_point(self, point, buffer=1e-7):
        # First check if the a->b and a->point are collinear. If they are,
        # the cross product should be zero (with some buffer for errors)
        cross_product = (self.b - self.a).cross_product(point - self.a)
        if cross_product.norm() > buffer:
            return False

        # If the dot product between a->b and a->point is negative then
        # point lays outside the a---b boundaries
        dot_product = (self.b - self.a).dot_product(point - self.a)
        if dot_product + buffer < 0.0:
            return False

        # Finally if it is greater than the a->b squared distance it also lays
        # out of bounds
        distance = self.a.squared_distance_to(self.b)
        if dot_product - distance > buffer:
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

    def inverted(self):
        return LineSegment(self.b, self.a)

    def is_orthogonal_to(self, line_segment, buffer=0.001):
        return abs((self.b - self.a).dot_product(line_segment.b - line_segment.a)) < buffer

    def includes_line_segment(self, other_segment):
        return self.includes_point(other_segment.start_point()) and \
            self.includes_point(other_segment.end_point())

    def _find_line_segment_intersection(self, segment):
        v1 = self.direction_vector()
        p1 = self.start_point()

        v2 = segment.direction_vector()
        p2 = segment.start_point()

        v3 = p2 - p1
        v4 = p1 - p2

        v1_cross_v2 = v1.cross_product(v2)
        v2_cross_v1 = v2.cross_product(v1)

        if abs(v1_cross_v2.norm()) < 1e-7:
            overlap = self._collinear_overlap_with(segment)
            if overlap:
                return [overlap]
            else:
                return []

        k1 = v3.cross_product(v2).norm() / v1_cross_v2.norm()

        k2 = v4.cross_product(v1).norm() / v2_cross_v1.norm()

        rounded_k1 = round(k1, 7)
        rounded_k2 = round(k2, 7)

        if (rounded_k1 < 0.0) or (rounded_k1 > 1.0) or (rounded_k2 < 0.0) or (rounded_k2 > 1.0):
            return []

        candidate = p1 + v1 * k1

        if self.includes_point(candidate) and segment.includes_point(candidate):
            return [candidate]
        else:
            return []

    def _find_bounding_box_intersection(self, bounding_box):
        intersections = []
        for segment in bounding_box.perimeter():
            intersections.extend(self.find_intersection(segment))
        return intersections

    def _find_arc_intersection(self, arc):
        local_segment = self.translate_by(arc.center_point().negated())
        local_segment_vector = local_segment.direction_vector()

        a = local_segment_vector.norm_squared()
        b = 2 * ((local_segment_vector.x * local_segment.start_point().x) + (local_segment_vector.y * local_segment.start_point().y))
        c = local_segment.start_point().norm_squared() - (arc.radius() ** 2)

        delta = (b ** 2) - (4 * a * c)

        if delta < 0:
            # No intersection
            return []
        elif delta == 0.0:
            # Exactly one intersection (tangent)
            # Note that we no longer use the local coordinates
            u = -b / (2 * a)
            candidate = self.start_point() + (local_segment_vector * u)
            if self.includes_point(candidate) and arc.includes_point(candidate):
                return [candidate]
            else:
                return []
        else:
            delta = math.sqrt(delta)
            u1 = (-b + delta) / (2 * a)
            u2 = (-b - delta) / (2 * a)
            candidates = [self.start_point() + (local_segment_vector * u1),
                          self.start_point() + (local_segment_vector * u2)]
            return filter(lambda point: self.includes_point(point) and arc.includes_point(point), candidates)

    def _find_circle_intersection(self, circle):
        local_segment = self.translate_by(circle.center().negated())
        local_segment_vector = local_segment.direction_vector()

        a = local_segment_vector.norm_squared()
        b = 2 * ((local_segment_vector.x * local_segment.start_point().x) + (local_segment_vector.y * local_segment.start_point().y))
        c = local_segment.start_point().norm_squared() - (circle.radius() ** 2)

        delta = (b ** 2) - (4 * a * c)

        if delta < 0:
            # No intersection
            return []
        elif delta == 0.0:
            # Exactly one intersection (tangent)
            # Note that we no longer use the local coordinates
            u = -b / (2 * a)
            candidate = self.start_point() + (local_segment_vector * u)
            if self.includes_point(candidate):
                return [candidate]
            else:
                return []
        else:
            delta = math.sqrt(delta)
            u1 = (-b + delta) / (2 * a)
            u2 = (-b - delta) / (2 * a)
            candidates = [self.start_point() + (local_segment_vector * u1),
                          self.start_point() + (local_segment_vector * u2)]
            return filter(lambda point: self.includes_point(point), candidates)

    def _collinear_overlap_with(self, segment):
        overlap = None
        if self.includes_line_segment(segment):
            overlap = segment
        elif segment.includes_line_segment(self):
            overlap = self
        elif self.includes_point(segment.start_point()):
            overlap = LineSegment(segment.start_point(), segment._pick_segment_endpoint(self))
        elif self.includes_point(segment.end_point()):
            overlap = LineSegment(segment.end_point(), segment._pick_segment_endpoint(self))

        if not overlap:
            return None
        elif overlap.start_point() == overlap.end_point():
            return overlap.start_point()
        else:
            return overlap

    def find_intersection(self, other):
        # TODO: Remove this switch statement and make a proper polymorphic delegation
        if isinstance(other, LineSegment):
            return self._find_line_segment_intersection(other)
        elif isinstance(other, geometry.arc.Arc):
            return self._find_arc_intersection(other)
        elif isinstance(other, geometry.circle.Circle):
            return self._find_circle_intersection(other)
        elif isinstance(other, geometry.bounding_box.BoundingBox):
            return self._find_bounding_box_intersection(other)
        else:
            raise ValueError("Intersection between {0} and {1} not supported".format(self, other))

    def extended_by(self, distance):
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

    def extended_to(self, new_point):
        """
        Returns a new line segment that has been extended up to new_point. The
        extension is performed assuming the direction defined as if the line
        segment was a vector going from point a to point b.
        Fail if the resulting line segment doesn't align with previous one.
        """
        new_line_segment = LineSegment(self.a, new_point)
        # TODO: Use assertions
        if not new_line_segment.includes_point(self.b):
            raise ValueError("The resulting line segment is not collinear")
        return new_line_segment

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

    def points_at_linear_offset(self, reference_point, offset):
        circle = geometry.circle.Circle(reference_point, abs(offset))
        return self._find_circle_intersection(circle)

    def offset_for_point(self, point):
        if not self.includes_point(point):
            raise ValueError("Point {0} is not included in line segment".format(point))
        return (self.a - point).norm()

    def line_interpolation_points(self):
        return [self.a.clone(), self.b.clone()]

    def clone(self):
        return LineSegment(self.a, self.b)

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
        # Alternative to analize in the future
        # angle = self.direction_vector().angle(other.direction_vector())
        # return abs(angle) < 1

    def merge(self, other):
        return LineSegment(self.start_point(), other.end_point())

    def is_valid_path_connection(self):
        return True

    def trim_to_fit(self, bounding_box):
        if self.is_inside(bounding_box):
            return [self]
        if self.is_outside(bounding_box):
            return []

        intersections = self.find_intersection(bounding_box)
        if len(intersections) == 1:
            if bounding_box.includes_point(self.start_point()):
                return [LineSegment(self.start_point(), intersections[0])]
            elif bounding_box.includes_point(self.end_point()):
                return [LineSegment(intersections[0], self.end_point())]
            else:
                raise ValueError("Something in the math is wrong")
        elif len(intersections) == 2:
            if bounding_box.includes_point(self.start_point()) or \
               bounding_box.includes_point(self.end_point()):
                raise ValueError("Something in the math is wrong")
            return [LineSegment(intersections[0], intersections[1])]
        else:
            raise ValueError("Something in the math is wrong - Multiple intersections")

    def is_inside(self, bounding_box):
        return bounding_box.includes_point(self.start_point()) and \
            bounding_box.includes_point(self.end_point())

    def is_outside(self, bounding_box):
        return not bounding_box.includes_point(self.start_point()) and \
            not bounding_box.includes_point(self.end_point()) and \
            not self.find_intersection(bounding_box)

    def closest_point_to(self, point):
        direction = self.direction_vector()
        squared_norm = float(direction.norm_squared())

        start_to_point = point - self.start_point()

        u = (start_to_point.x * direction.x + start_to_point.y * direction.y) / squared_norm
        u = max(min(u, 1.0), 0.0)

        point = self.start_point() + (direction * u)

        if not self.includes_point(point):
            raise RuntimeError("Expecting {0} to include {1}".format(self, point))

        return self.start_point() + (direction * u)

    def _pick_segment_endpoint(self, segment):
        if self.includes_point(segment.start_point()):
            return segment.start_point()
        if self.includes_point(segment.end_point()):
            return segment.end_point()
        return None

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((hash(self.a), hash(self.b)))

    def __repr__(self):
        return "LineSegment({0}, {1})".format(self.a, self.b)
