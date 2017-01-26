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
