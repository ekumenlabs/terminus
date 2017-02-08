from geometry.point import Point


class BoundingBox(object):

    def __init__(self, origin, corner):
        self.origin = origin
        self.corner = corner
        self._normalize()

    @classmethod
    def from_boxes(cls, box_list):
        try:
            whole_merge = box_list[0]
            for i in range(1, len(box_list)):
                whole_merge = whole_merge.merge(box_list[i])
            return whole_merge
        except:
            raise Exception('box_list should be a non empty list of bounding boxes')

    def __hash__(self):
        return hash(hash(origin), hash(corner))

    def __eq__(self, other):
        return self.origin == other.origin and self.corner == other.corner

    def merge(self, other):
        merge_origin = Point(min(self.origin.x, other.origin.x),
                             min(self.origin.y, other.origin.y))
        merge_corner = Point(max(self.corner.x, other.corner.x),
                             max(self.corner.y, other.corner.y))
        return BoundingBox(merge_origin, merge_corner)

    def _normalize(self):
        new_origin = self.origin.min(self.corner)
        new_corner = self.origin.max(self.corner)
        self.origin = new_origin
        self.corner = new_corner
