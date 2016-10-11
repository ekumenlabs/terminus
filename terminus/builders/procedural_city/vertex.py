# Note: This class is imported from the procedural city generator repo so
# we can de-serialize the file contents. This class will likely change in
# the future as we move forward, especially to provide conversion messages
# to our domain models.


class Vertex(object):
    def __init__(self, coords):
        self.coords = coords
        self.neighbours = []
        self.minor_road = False
        self.seed = False

    def __repr__(self):
        return "Vertex: " + str(self.coords)
