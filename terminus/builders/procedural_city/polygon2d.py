from shapely.geometry import Point

# Note: These classes are imported from the procedural city generator repo so
# we can de-serialize the file contents. These classes will likely change in
# the future as we move forward, especially to provide conversion messages
# to our domain models.


class Edge(object):

    def __init__(self, vertex1, vertex2, bordering_road=True):
        self.bordering_road = bordering_road
        self.vertices = np.array((vertex1, vertex2))
        self.dir_vector = vertex2 - vertex1
        self.length = np.linalg.norm(self.dir_vector)
        v = self.dir_vector/self.length
        self.n = np.array((v[1], -v[0]))

    def __getitem__(self, i):
        return self.vertices[i]


class Polygon2D(object):

    def __init__(self, in_list, poly_type="vacant"):
        """Input may be numpy-arrays or Edge-objects"""

        if isinstance(in_list[0], Edge):
            self.edges = in_list
            self.vertices = [edge[0] for edge in self.edges]
        else:
            self.vertices = in_list
            self.edges = [Edge(v1, v2) for v1, v2 in
                          zip(in_list, in_list[1:]+[in_list[0]])]
        self.poly_type = poly_type

    def get_vertices_as_points(self, ratio):
        return list((arr[0]*ratio, arr[1]*ratio, 0) for arr in self.vertices)

    def is_lot(self):
        return self.poly_type == 'lot'

    def __repr__(self):
        s = "Polygon2D: \n"
        for vertex in self.vertices:
            s += str([round(x, 2) for x in vertex]) + "\t"
        s += "\n"
        return s
