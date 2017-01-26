from math import hypot
from geometry.point import Point


class LineSegment(object):

    def __init__(self, point_a, point_b):
        self.a = point_a
        self.b = point_b

    @classmethod
    def from_tuples(cls, t1, t2):
        return cls(Point.from_tuple(t1), Point.from_tuple(t2))

    def includes_point(self, point, buffer=0.001):
        # First check if the a->b and a->point are colinear. If they are,
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

    def is_orthogonal_to(self, line_segment, buffer=0.001):
        return abs((self.b - self.a).dot_product(line_segment.b - line_segment.a)) < buffer

    def find_intersection(self, segment):
        '''
        Finds intersections between two line segments and
        returns the intersection point.
        Base on http://stackoverflow.com/a/14795484
        '''
        s10_x = self.b.x - self.a.x
        s10_y = self.b.y - self.a.y
        s32_x = segment.b.x - segment.a.x
        s32_y = segment.b.y - segment.a.y
        denom = s10_x * s32_y - s32_x * s10_y
        if denom == 0:
            return None  # collinear

        denom_is_positive = denom > 0
        s02_x = self.a.x - segment.a.x
        s02_y = self.a.y - segment.a.y
        s_numer = s10_x * s02_y - s10_y * s02_x

        if (s_numer < 0) == denom_is_positive:
            return None  # no collision
        t_numer = s32_x * s02_y - s32_y * s02_x

        if (t_numer < 0) == denom_is_positive:
            return None  # no collision
        if (s_numer > denom) == denom_is_positive or\
           (t_numer > denom) == denom_is_positive:
            return None  # no collision

        # collision detected
        t = float(t_numer) / float(denom)
        return Point(self.a.x + (t * s10_x),
                     self.a.y + (t * s10_y), 0)

    def extend(self, distance):
        '''
        Returns a new line segment that has been extended by distance. The extension
        is performed assuming the direction defined as if the line segment was a
        vector going from point a to point b
        '''
        dx = self.b.x - self.a.x
        dy = self.b.y - self.a.y
        linelen = hypot(dx, dy)

        new_end = Point(self.b.x + dx / linelen * distance,
                        self.b.y + dy / linelen * distance)
        return LineSegment(self.a, new_end)

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((hash(self.a), hash(self.b)))

    def __repr__(self):
        return "LineSegment({0}, {1})".format(self.a, self.b)
