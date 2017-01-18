import math


class LineSegment(object):

    def __init__(self, point_a, point_b):
        self.a = point_a
        self.b = point_b

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
