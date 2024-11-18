# DCEL.py

class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.incident_edge = None  # An arbitrary half-edge originating from the vertex

    def __repr__(self):
        return f"Vertex({self.x}, {self.y})"


class HalfEdge:
    def __init__(self):
        self.origin = None          # Vertex at the origin of the half-edge
        self.twin = None            # Twin half-edge (opposite direction)
        self.incident_face = None   # Face to the left of the half-edge
        self.next = None            # Next half-edge in the face
        self.prev = None            # Previous half-edge in the face

    def __repr__(self):
        return f"HalfEdge(origin={self.origin})"


class Face:
    def __init__(self):
        self.site = None              # The site (point) associated with this face
        self.outer_component = None   # An arbitrary half-edge on the outer boundary
        self.inner_components = []    # List of half-edges on inner boundaries (holes)

    def __repr__(self):
        return f"Face(site={self.site})"


class DCEL:
    def __init__(self):
        self.vertices = []    # List of all vertices
        self.half_edges = []  # List of all half-edges
        self.faces = []       # List of all faces (cells)

    def create_vertex(self, x, y):
        vertex = Vertex(x, y)
        self.vertices.append(vertex)
        return vertex

    def create_half_edge_pair(self):
        he1 = HalfEdge()
        he2 = HalfEdge()
        he1.twin = he2
        he2.twin = he1
        self.half_edges.extend([he1, he2])
        return he1, he2

    def create_face(self, site=None):
        face = Face()
        face.site = site
        self.faces.append(face)
        return face
