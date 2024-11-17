import heapq
import math

class Event:
    def __init__(self, y, x, event_type, point=None, arc=None, circle_center=None):
        self.y = y
        self.x = x
        self.type = event_type  # 'site' or 'circle'
        self.point = point      # For site events
        self.arc = arc          # For circle events
        self.circle_center = circle_center  # For circle events
        self.valid = True       # For invalidating circle events

    def __lt__(self, other):
        # For priority queue (higher y-coordinate has higher priority)
        # In heapq, the smallest element is popped first, so we invert the comparison
        if self.y == other.y:
            return self.x < other.x
        return self.y > other.y

class EventQueue:
    def __init__(self):
        self.heap = []

    def push(self, event):
        heapq.heappush(self.heap, event)

    def pop(self):
        return heapq.heappop(self.heap)

    def remove(self, event):
        # Mark the event as invalid; it will be skipped when popped
        event.valid = False

    def is_empty(self):
        return len(self.heap) == 0

class Arc:
    def __init__(self, site):
        self.site = site
        self.prev = None
        self.next = None
        self.event = None  # Circle event

class Edge:
    def __init__(self, start, left, right):
        self.start = start  # Start point (vertex)
        self.end = None     # End point (vertex)
        self.left = left    # Left site
        self.right = right  # Right site
        self.neighbor = None  # The twin edge in DCEL

class Voronoi:
    def __init__(self, points):
        self.points = points
        self.arcs = None
        self.edges = []
        self.event_queue = EventQueue()
        self.bounding_box = None
        self.vertices = []

    def process(self):
        # Initialize the event queue with site events
        for point in self.points:
            event = Event(point[1], point[0], 'site', point=point)
            self.event_queue.push(event)

        # Process events
        while not self.event_queue.is_empty():
            event = self.event_queue.pop()
            if not event.valid:
                continue
            if event.type == 'site':
                self.handle_site_event(event)
            elif event.type == 'circle':
                self.handle_circle_event(event)

    def handle_site_event(self, event):
        point = event.point
        if self.arcs is None:
            self.arcs = Arc(point)
            return

        arc = self.find_arc_above(point)
        if arc.event:
            self.event_queue.remove(arc.event)
            arc.event = None

        # Create new edges
        start = (point[0], self.get_y(arc.site, point[0], point[1]))
        edge1 = Edge(start, arc.site, point)
        edge2 = Edge(start, point, arc.site)
        edge1.neighbor = edge2
        edge2.neighbor = edge1
        self.edges.append(edge1)
        self.edges.append(edge2)

        # Replace arc by new arcs
        new_arc_left = Arc(arc.site)
        new_arc_center = Arc(point)
        new_arc_right = Arc(arc.site)

        # Set up doubly linked list
        new_arc_left.prev = arc.prev
        new_arc_left.next = new_arc_center
        new_arc_center.prev = new_arc_left
        new_arc_center.next = new_arc_right
        new_arc_right.prev = new_arc_center
        new_arc_right.next = arc.next

        if arc.prev:
            arc.prev.next = new_arc_left
        if arc.next:
            arc.next.prev = new_arc_right

        if arc == self.arcs:
            self.arcs = new_arc_left

        # Check for circle events
        self.check_circle_event(new_arc_left)
        self.check_circle_event(new_arc_right)

    def handle_circle_event(self, event):
        arc = event.arc
        if not arc.event.valid:
            return

        # Create a vertex at the circle center
        vertex = (event.circle_center[0], event.circle_center[1])
        self.vertices.append(vertex)

        # Set the end point of edges
        if arc.prev:
            edge = Edge(vertex, arc.prev.site, arc.site)
            self.edges.append(edge)
        if arc.next:
            edge = Edge(vertex, arc.site, arc.next.site)
            self.edges.append(edge)

        # Remove the arc from the beach line
        if arc.prev:
            arc.prev.next = arc.next
            arc.prev.event = None
        if arc.next:
            arc.next.prev = arc.prev
            arc.next.event = None

        if arc.prev and arc.next:
            self.check_circle_event(arc.prev)
            self.check_circle_event(arc.next)

    def find_arc_above(self, point):
        arc = self.arcs
        x = point[0]
        while arc:
            x_left = self.get_breakpoint(arc.prev, arc, point[1]) if arc.prev else float('-inf')
            x_right = self.get_breakpoint(arc, arc.next, point[1]) if arc.next else float('inf')
            if x_left <= x <= x_right:
                return arc
            arc = arc.next
        return None  # Should not reach here

    def get_breakpoint(self, arc_left, arc_right, directrix):
        # Compute the x-coordinate of the breakpoint between two arcs
        p = arc_left.site
        r = arc_right.site
        dp = 2.0 * (p[1] - directrix)
        dr = 2.0 * (r[1] - directrix)

        if dp == dr:
            return (p[0] + r[0]) / 2.0

        a = 1.0 / dp - 1.0 / dr
        b = -2.0 * (p[0] / dp - r[0] / dr)
        c = (p[0] * p[0] + p[1] * p[1] - directrix * directrix) / dp - \
            (r[0] * r[0] + r[1] * r[1] - directrix * directrix) / dr

        discriminant = b * b - 4.0 * a * c
        if discriminant < 0:
            return (p[0] + r[0]) / 2.0  # Should not happen

        x1 = (-b + math.sqrt(discriminant)) / (2.0 * a)
        x2 = (-b - math.sqrt(discriminant)) / (2.0 * a)

        if p[1] < r[1]:
            return max(x1, x2)
        else:
            return min(x1, x2)

    def get_y(self, site, x, directrix):
        # Compute the y-coordinate of the parabolic arc at x
        dp = 2.0 * (site[1] - directrix)
        if dp == 0:
            return float('inf')
        y = ((x - site[0]) ** 2 + site[1] ** 2 - directrix ** 2) / dp
        return y

    def check_circle_event(self, arc):
        if arc.event:
            self.event_queue.remove(arc.event)
            arc.event = None

        if not arc.prev or not arc.next:
            return

        a = arc.prev.site
        b = arc.site
        c = arc.next.site

        if self.ccw(a, b, c) != 1:
            return

        circle = self.circle_center(a, b, c)
        if circle is None:
            return

        x, y, r = circle
        directrix = y - r

        if directrix <= arc.site[1]:
            return

        event = Event(directrix, x, 'circle', arc=arc, circle_center=(x, y))
        arc.event = event
        self.event_queue.push(event)

    def circle_center(self, a, b, c):
        # Compute circle center given three points
        ax, ay = a[0], a[1]
        bx, by = b[0], b[1]
        cx, cy = c[0], c[1]

        A = bx - ax
        B = by - ay
        C = cx - ax
        D = cy - ay
        E = A * (ax + bx) + B * (ay + by)
        F = C * (ax + cx) + D * (ay + cy)
        G = 2.0 * (A * (cy - by) - B * (cx - bx))

        if G == 0:
            return None

        x = (D * E - B * F) / G
        y = (A * F - C * E) / G
        r = math.hypot(ax - x, ay - y)
        return (x, y, r)

    def ccw(self, a, b, c):
        # Check if three points make a counter-clockwise turn
        area = (b[0] - a[0]) * (c[1] - a[1]) - \
               (b[1] - a[1]) * (c[0] - a[0])
        if area > 0:
            return 1
        elif area < 0:
            return -1
        else:
            return 0

def main():
    # Input: List of points
    points = [(1.0, 2.0), (1.1, 2.1), (2.0, 1.0), (3.0, 4.0)]

    voronoi = Voronoi(points)
    voronoi.process()

    # Output the edges
    print("Voronoi Diagram Edges:")
    for edge in voronoi.edges:
        if edge.start and edge.end:
            print(f"Edge from {edge.start} to {edge.end}")
        else:
            print(f"Half-edge starting at {edge.start}")

if __name__ == "__main__":
    main()
