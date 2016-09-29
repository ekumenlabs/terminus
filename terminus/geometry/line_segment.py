
class LineSegment():
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __eq__(self, other):
        return (self.start == other.start) and (self.end == other.end) \
                or (self.start == other.end) and (self.end == other.start)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(hash(self.start) + hash(self.end))
