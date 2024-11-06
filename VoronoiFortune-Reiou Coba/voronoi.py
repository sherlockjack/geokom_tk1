from AVLTree import AVLTree
from DCEL import DCEL
from PointHeap import PointHeap

class VoronoiDiagram:
    def __init__(self, points):
        self.points = points
        self.Q = PointHeap(points) # Site events as Priority Queue (based on y-coordinates)
        self.T = AVLTree()
        self.D = DCEL()

    def compute_diagram(self):
        while self.Q.points:
            event = self.Q.pop()
            if event in self.points: # Check if event is a site event
                self.handle_site_event(event)
            else:
                arc = self.handle_circle_event(event)
        # treat the remaining internal nodes of T as unbounded edges of D (Vor(P))
        return self.D

    def handle_site_event(self, event):
        pass

    def handle_circle_event(self, event):
        pass