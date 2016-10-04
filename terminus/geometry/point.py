import numpy as np


class Point():
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def from_array(cls, array):
        if len(array) == 2:
            return cls(array[0], array[1])
        else:
            return cls(array[0], array[1], array[2])

    def __repr__(self):
        return "({0},{1},{2})".format(self.x, self.y, self.z)

    def angle_2d_to(self, other_point):
        alpha = np.arctan2(self.x - other_point.x, self.y - other_point.y)
        if alpha < 0:
            alpha += 2 * np.pi
        return alpha

    def __eq__(self, other_point):
        return (self.x == other_point.x) and \
               (self.y == other_point.y) and \
               (self.z == other_point.z)

    def __ne__(self, other_point):
        return not self.__eq__(other_point)

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
