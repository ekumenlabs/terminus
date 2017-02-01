from geometry.point import Point


class BoundingBox(object):

    def _normalize(self):
        new_origin = Point(min(self.origin.x, self.corner.x),
                           min(self.origin.y, self.corner.y))
        new_corner = Point(max(self.origin.x, self.corner.x),
                           max(self.origin.y, self.corner.y))
        self.origin = new_origin
        self.corner = new_corner

    def __init__(self, origin, corner):
        self.origin = origin
        self.corner = corner
        self._normalize()

    def __eq__(self, other):
        return self.origin == other.origin and self.corner == other.corner

    def merge(self, other):
        merge_origin = Point(min(self.origin.x, other.origin.x),
                             min(self.origin.y, other.origin.y))
        merge_corner = Point(max(self.corner.x, other.corner.x),
                             max(self.corner.y, other.corner.y))
        return BoundingBox(merge_origin, merge_corner)

    def merge_multiple_boundingboxes(self, box_list):
        whole_merge = box_list[0]
        for i in range(1, len(box_list)):
            whole_merge = whole_merge.merge(box_list[i])
        return whole_merge
