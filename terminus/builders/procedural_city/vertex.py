class Vertex(object):
    def __init__(self, coords):
        self.coords = coords
        self.neighbours = []
        self.minor_road = False
        self.seed = False

    def __repr__(self):
        return "Vertex: " + str(self.coords)
