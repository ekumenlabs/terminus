# Note: This class is imported from the procedural city generator repo so
# we can de-serialize the file contents. This class will likely change in
# the future as we move forward, especially to provide conversion messages
# to our domain models.

from geometry.point import Point


class Vertex(object):
    def __init__(self, coords):
        self.coords = coords
        self.neighbours = []
        self.minor_road = True
        self.seed = False

    def __repr__(self):
        return "Vertex: " + str(self.coords)


class GraphNode(object):
    def __init__(self, location, is_minor_road=True):
        self.location = location
        self.neighbours = []
        self.is_minor_road = is_minor_road

    @classmethod
    def from_vertex(cls, vertex, ratio):
        '''
        Shapely has issues with too-detailed floating points, so we round them
        to 7 decimals (which is just a 0.0000001 meter precision lost)
        http://gis.stackexchange.com/questions/50399/how-best-to-fix-a-non-noded-intersection-problem-in-postgis
        http://freigeist.devmag.net/r/691-rgeos-topologyexception-found-non-noded-intersection-between.html
        '''
        location = Point(vertex.coords[0] * ratio, vertex.coords[1] * ratio, 0).rounded_to(7)
        return cls(location, vertex.minor_road)

    def set_neighbours(self, neighbours):
        self.neighbours = neighbours

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)

    def neighbours_count(self):
        return len(self.neighbours)

    def prepare_traversal(self):
        self.neighbours_to_traverse = list(self.neighbours)

    def neighbours_to_traverse_count(self):
        return len(self.neighbours_to_traverse)

    def get_neighbours_to_traverse(self):
        return self.neighbours_to_traverse

    def pop_neighbours_to_traverse(self):
        return self.neighbours_to_traverse.pop()

    def remove_neighbour_to_traverse(self, node):
        return self.neighbours_to_traverse.remove(node)
