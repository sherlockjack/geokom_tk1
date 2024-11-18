class DCEL:
    def __init__(self):
        self.vertices = []
        self.half_edges = []
        self.faces = []

class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class HalfEdge:
    def __init__(self, origin=None):
        self.origin = origin
        self.next = None
        self.prev = None
        self.twin = None
        self.incident_face = None

class Face:
    def __init__(self, outer_component=None):
        self.outer_component = outer_component

