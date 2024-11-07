class DCEL:
    def __init__(self):
        self.vertices = []
        self.halfedges = []
        self.faces = []

class HalfEdge:
    def __init__(self, prev, next, twin, origin, face):
        self.prev = prev # previous half of the same cell, HalfEdge
        self.next = next # next half of the same cell, HalfEdge
        self.twin = twin # opposite half of the same edge (different voronoi cell), HalfEdge
        self.origin = origin # the vertex at the start of the half-edge, Vertex
        self.face = face # the face the half-edge bounds, Face (voronoi cell)

class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.half_edges = None # half-edges that start at this vertex

    def __set_half_edges(self, half_edges: HalfEdge):
        self.half_edges = half_edges

class Face:
    def __init__(self, half_edge):
        self.half_edge = half_edge # one of the half-edges bordering the face (voronoi cell)