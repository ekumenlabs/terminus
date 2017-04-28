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

from geometry.circle import Circle
from geometry.point import Point
# Avoid module circular dependencies
import geometry.line_segment


class Arc(object):

    def __init__(self, start_point, theta, radius, angular_length):
        """
        start_point: The point in the circumference where the arc starts
        theta: The heading of the tangent in start_point
        radius: The radius of the circular arc
        angular_length: The angle formed between then center -> start point
        and center -> end point. If the angular_length is > 0 the arc direction
        is considered counter-clockwise
        """
        self._start_point = start_point
        self._theta = theta % 360
        self._radius = radius
        self._angular_length = angular_length
        self._end_point = self._compute_point_at(angular_length)

    @classmethod
    def from_points_in_circle(cls, start_point, end_point, circle):
        """
        Returns a counter-clockwise arc from start point to end point on the given circle
        """
        center = circle.center
        start_point_angle = Point(1, 0).angle((start_point - center))
        start_heading = start_point_angle + 90
        angle_between_vectors = (start_point - center).angle(end_point - center)
        if angle_between_vectors >= 0:
            angular_length = angle_between_vectors
        else:
            angular_length = 360 + angle_between_vectors
        return cls(start_point, start_heading, circle.radius, angular_length)

    def start_point(self):
        return self._start_point

    def end_point(self):
        return self._end_point

    def start_heading(self):
        return self._theta

    def end_heading(self):
        return self._theta + self._angular_length

    def theta(self):
        return self._theta

    def radius(self):
        return self._radius

    def angular_length(self):
        return self._angular_length

    def clone(self):
        return Arc(self._start_point, self._theta, self._radius, self._angular_length)

    def center_point(self):
        """
        Answers the point that is the center of the circular arc
        """
        theta_in_radians = math.radians(self._theta)
        direction_multiplier = math.copysign(1, self._angular_length)
        vector = Point(-self._radius * direction_multiplier * math.sin(theta_in_radians),
                       self._radius * direction_multiplier * math.cos(theta_in_radians))
        return self._start_point + vector

    def circle(self):
        return Circle(self.center_point(), self.radius())

    def length(self):
        """
        The length of the perimeter of the arc
        """
        return abs(math.pi * self._radius * self._angular_length / 180.0)

    def _clip_angle_to_360(self, angle):
        return angle % 360

    def counter_clockwise(self):
        """
        If the arc has clockwise direction, it returns the same arc traveled in
        counter-clockwise direction. If it already has counter-clockwise direction,
        it returns the same arc.
        """
        if self.angular_length() >= 0:
            # Nothing to do, already counter clockwise
            return self
        return Arc(self.end_point(), self.end_heading() + 180, self.radius(), -self.angular_length())

    def contains_arc(self, other):
        # this method doesn't consider arc directions
        if not self.circle().almost_equal_to(other.circle()):
            return False
        elif (not self.includes_point(other.start_point())) or (not self.includes_point(other.end_point())):
            return False
        else:
            arc1 = self.counter_clockwise()
            arc2 = other.counter_clockwise()
            return arc1.almost_equal_to(arc2) or \
                (not arc2.includes_point(arc1.start_point())) or \
                (not arc2.includes_point(arc1.end_point()))

    def find_intersection(self, other):
        # TODO: Remove this switch statement and make a proper polymorphic delegation
        if isinstance(other, Arc):
            return self._find_arc_intersection(other)
        elif isinstance(other, geometry.line_segment.LineSegment):
            return other._find_arc_intersection(self)
        elif isinstance(other, geometry.circle.Circle):
            return self._find_circle_intersection(other)
        else:
            raise ValueError("Intersection between {0} and {1} not supported".format(self, other))

    def _find_circle_intersection(self, circle):
        my_circle = self.circle()
        candidates = my_circle.intersection(circle)
        return filter(lambda point: self.includes_point(point), candidates)

    def _find_arc_intersection(self, other):
        circle1 = self.circle()
        circle2 = other.circle()
        if not circle1.almost_equal_to(circle2):
            candidates = circle1.intersection(circle2)
            return filter(lambda point: self.includes_point(point) and other.includes_point(point), candidates)
        arc1 = self.counter_clockwise()
        arc2 = other.counter_clockwise()
        if arc1.contains_arc(arc2):
            return [arc2]
        elif arc2.contains_arc(arc1):
            return [arc1]
        else:
            if arc1.end_point().almost_equal_to(arc2.start_point(), 5) and arc2.end_point().almost_equal_to(arc1.start_point(), 5):
                return [arc1.end_point(), arc1.start_point()]
            elif arc1.end_point().almost_equal_to(arc2.start_point(), 5):
                return [arc2.start_point()]
            elif arc2.end_point().almost_equal_to(arc1.start_point(), 5):
                return [arc1.start_point()]
            elif arc1.includes_point(arc2.start_point()) and arc1.includes_point(arc2.end_point()):
                return [Arc.from_points_in_circle(arc2.start_point(), arc1.end_point(), circle1),
                        Arc.from_points_in_circle(arc1.start_point(), arc2.end_point(), circle1)]
            elif arc1.includes_point(arc2.start_point()):
                return [Arc.from_points_in_circle(arc2.start_point(), arc1.end_point(), circle1)]
            elif arc1.includes_point(arc2.end_point()):
                return [Arc.from_points_in_circle(arc1.start_point(), arc2.end_point(), circle1)]
            else:
                return []

    def includes_point(self, point, buffer=1e-7):
        """
        Answer if a given point is part of the arc's perimeter. Allow to
        parametrize with a given buffer to contemplate rounding errors
        """
        center = self.center_point()
        center_start = self._start_point - center
        center_point = point - center
        if abs(center_point.norm() - self._radius) > buffer:
            return False
        angle_between_vectors = center_start.angle(center_point)
        if abs(angle_between_vectors) < buffer:
            # this solves some problems that come from approximate calculations
            return True
        if self._angular_length >= 0:
            return buffer >= self._clip_angle_to_360(angle_between_vectors) - self._angular_length
        else:
            return self._angular_length - (self._clip_angle_to_360(angle_between_vectors) - 360) < buffer or \
                abs(angle_between_vectors) < buffer

    def extend(self, distance):
        """
        Extend the arc by a given distance, following the arc's direction
        """
        angular_delta = 180 * distance / (math.pi * self._radius)
        return Arc(self._start_point, self._theta, self._radius, self._angular_length + angular_delta)

    def point_at_offset(self, offset):
        """
        Returns a point in the arc taken as an offset from the start of the arc.
        """
        if offset > self.length():
            raise ValueError("Offset ({0})is greater than arc length ({1})".format(offset, self.length()))
        angular_offset = math.copysign(offset, self._angular_length) * 180 / (math.pi * self._radius)
        return self._compute_point_at(angular_offset)

    def offset_for_point(self, point):
        """
        Answer how far is a given point from the start of the arc, measured as
        a distance on the arc's perimeter.
        """
        angle = self._angular_offset_for_point(point)
        return abs(math.pi * self._radius * angle / 180.0)

    def points_at_linear_offset(self, reference_point, offset):
        circle1 = Circle(self.center_point(), self.radius())
        circle2 = Circle(reference_point, abs(offset))
        intersections = circle1.intersection(circle2)
        return filter(lambda point: self.includes_point(point), intersections)

    def split_into(self, pairs):
        arcs = []
        for start, end in pairs:
            start_angular_offset = self._angular_offset_for_point(start)
            end_angular_offset = self._angular_offset_for_point(end)
            start_heading = self._theta + start_angular_offset
            arc = Arc(start, start_heading, self._radius, end_angular_offset - start_angular_offset)
            arcs.append(arc)
        return arcs

    def can_be_merged_with(self, other):
        return self.__class__ is other.__class__ and \
            self.radius() == other.radius() and \
            self.end_heading() == other.start_heading() and \
            self.end_point().almost_equal_to(other.start_point(), 5) and \
            self.center_point().almost_equal_to(other.center_point(), 5)

    def merge(self, other):
        return Arc(self.start_point(),
                   self.theta(),
                   self.radius(),
                   self.angular_length() + other.angular_length())

    def line_interpolation_points(self, step=1):
        """
        Return a collection of points used to interpolate the arc.
        """
        points = []
        length = self.length()
        last_point = length - step
        traversed = 0
        while traversed <= last_point:
            points.append(self.point_at_offset(traversed))
            traversed += step
        if length - traversed > step / 2:
            points.append(self.point_at_offset(traversed))
        points.append(self.end_point().clone())
        return points

    def heading_at_offset(self, offset):
        """
        Answer the heading of a point at a given offset.
        """
        if offset > self.length():
            raise ValueError("Offset ({0}) is greater than segment length ({1})".format(offset, self.length()))
        angular_offset = math.copysign(offset, self._angular_length) * 180 / (math.pi * self._radius)
        return self._clip_angle_to_360(self._theta + angular_offset)

    def _compute_point_at(self, angular_offset):
        """
        Great explanation on some of the math here:
        http://math.stackexchange.com/questions/275201/how-to-find-an-end-point-of-an-arc-given-another-end-point-radius-and-arc-dire
        """
        theta_in_radians = math.radians(self._theta)
        angular_length_in_radians = math.radians(angular_offset)
        direction_multiplier = math.copysign(1, angular_offset)
        start_end_angle = theta_in_radians + angular_length_in_radians
        start_end_vector = Point(self._radius * direction_multiplier * (math.sin(start_end_angle) - math.sin(theta_in_radians)),
                                 self._radius * direction_multiplier * (math.cos(theta_in_radians) - math.cos(start_end_angle)))
        return self._start_point + start_end_vector

    def _angular_offset_for_point(self, point):
        if not self.includes_point(point):
            raise ValueError("{0} is not included in arc {1}".format(point, self))
        center = self.center_point()
        center_start = self._start_point - center
        center_point = point - center
        return center_start.angle(center_point)

    def is_valid_path_connection(self):
        return round(self.radius(), 7) > 4.1

    def almost_equal_to(self, other, decimals=5):
        return self.circle().almost_equal_to(other.circle(), decimals) and \
            self.start_point().almost_equal_to(other.start_point(), decimals) and \
            self.end_point().almost_equal_to(other.end_point(), decimals) and \
            self.angular_length() * other.angular_length() > 0

    def __eq__(self, other):
        return self._start_point == other._start_point and \
            self._theta == other._theta and \
            self._radius == other._radius and \
            self._angular_length == other._angular_length

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._start_point, self._theta, self._radius, self._angular_length))

    def __repr__(self):
        return "Arc({0}, {1}, {2}, {3})".format(self._start_point, self._theta, self._radius, self._angular_length)
