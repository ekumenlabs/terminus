class Vertex(object):
    """
    Vertex, used as a counterpart of the Vertex class in the
    procedural_city_generation.roadmap submodule.
    - coords : numpy.ndarray(2, )
        XY-Coordinates of this Vertex
    - neighbours : list<Vertex>
        List of all Vertices that this Vertex is currently connected to
    - minor_road : boolean
        Describes whether this road is a minor road
    - seed : boolean
        Describes whether this (major) road is a seed
    """
    def __init__(self, coords):
        self.coords = coords
        self.neighbours = []
        self.minor_road = False
        self.seed = False

    def __cmp__(self, other):
        if isinstance(other, Vertex):
            if self.coords[0] > other.coords[0]:
                return 1
            elif self.coords[0] < other.coords[0]:
                return -1
            else:
                if self.coords[1] > other.coords[1]:
                    return 1
                elif self.coords[1] < other.coords[1]:
                    return -1
            return 0
