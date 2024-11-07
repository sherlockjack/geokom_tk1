# fortune.py
import heapq
import math

class Event:
    def __init__(self, point, y, is_site_event=True, arc=None):
        self.point = point      # For site events, this is the site (x, y)
        self.y = y              # Y-coordinate of the event
        self.is_site_event = is_site_event
        self.arc = arc          # For circle events, the arc that will disappear
        self.valid = True       # Used to invalidate circle events

    def __lt__(self, other):
        # Events are ordered by their y-coordinate (sweep line position)
        return self.y > other.y  # Max-heap based on y-coordinate

class Arc:
    def __init__(self, site):
        self.site = site        # The site (x, y) associated with this arc
        self.prev = None        # Left neighbor in the beach line
        self.next = None        # Right neighbor in the beach line
        self.event = None       # Potential circle event
        self.edge_left = None   # Edge between this arc and the left arc
        self.edge_right = None  # Edge between this arc and the right arc

class Edge:
    def __init__(self, start, left_site, right_site):
        self.start = start          # Starting point of the edge (vertex)
        self.end = None             # Ending point of the edge (vertex)
        self.left_site = left_site  # Site to the left of the edge
        self.right_site = right_site  # Site to the right of the edge
        self.direction = (right_site[1] - left_site[1], -(right_site[0] - left_site[0]))  # Perpendicular to line between sites
        self.f = None               # Function to compute points along the edge
        self.neighbour = None       # The other edge sharing the start point

class FortuneAlgorithm:
    def __init__(self, sites):
        self.sites = sites
        self.event_queue = []
        self.edges = []
        self.beachline = None
        self.vertices = []
        self.x0 = min(x for x, y in sites) - 1
        self.x1 = max(x for x, y in sites) + 1
        self.y0 = min(y for x, y in sites) - 1
        self.y1 = max(y for x, y in sites) + 1

    def run(self):
        # Initialize event queue with site events
        for x, y in self.sites:
            heapq.heappush(self.event_queue, Event((x, y), y, True))

        # Process events
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            if event.is_site_event:
                self.process_site_event(event)
            else:
                if event.valid:
                    self.process_circle_event(event)

        # Finish edges
        self.finish_edges()

    def process_site_event(self, event):
        site = event.point
        if not self.beachline:
            self.beachline = Arc(site)
            return

        arc = self.get_arc_above(site[0])
        if arc.event:
            arc.event.valid = False

        # Create new edges
        start_point = (site[0], self.get_y(arc.site, site[0], event.y))
        edge_left = Edge(start_point, arc.site, site)
        edge_right = Edge(start_point, site, arc.site)
        edge_left.neighbour = edge_right
        edge_right.neighbour = edge_left
        self.edges.append(edge_left)
        self.edges.append(edge_right)

        # Replace arc with three new arcs
        arc_new = Arc(site)
        arc_left = Arc(arc.site)
        arc_right = Arc(arc.site)

        arc_left.prev = arc.prev
        arc_left.next = arc_new
        arc_new.prev = arc_left
        arc_new.next = arc_right
        arc_right.prev = arc_new
        arc_right.next = arc.next

        if arc_left.prev:
            arc_left.prev.next = arc_left
        if arc_right.next:
            arc_right.next.prev = arc_right

        arc_left.edge_right = edge_left
        arc_right.edge_left = edge_right
        arc_new.edge_left = edge_left
        arc_new.edge_right = edge_right

        if arc == self.beachline:
            self.beachline = arc_left

        # Check for new circle events
        self.check_circle_event(arc_left)
        self.check_circle_event(arc_right)
        self.check_circle_event(arc_new)

    def process_circle_event(self, event):
        arc = event.arc
        vertex = (event.point[0], event.y)
        self.vertices.append(vertex)

        # Set the end point of left and right edges
        if arc.edge_left:
            arc.edge_left.end = vertex
        if arc.edge_right:
            arc.edge_right.end = vertex

        # Remove arc from beach line
        if arc.prev:
            arc.prev.next = arc.next
            arc.prev.edge_right = arc.edge_left
        if arc.next:
            arc.next.prev = arc.prev
            arc.next.edge_left = arc.edge_right

        # Check for new circle events
        self.check_circle_event(arc.prev)
        self.check_circle_event(arc.next)

    def check_circle_event(self, arc):
        if not arc or not arc.prev or not arc.next:
            return

        # Check if the three sites are converging
        circle = self.compute_circle(arc.prev.site, arc.site, arc.next.site)
        if not circle:
            return

        x, y, r = circle
        if y - r >= self.get_sweep_line_y():
            return

        # Add circle event to the queue
        event = Event((x, y), y - r, False, arc)
        arc.event = event
        heapq.heappush(self.event_queue, event)

    def get_arc_above(self, x):
        arc = self.beachline
        while arc:
            y = self.get_y(arc.site, x, self.get_sweep_line_y())
            if arc.prev:
                y_prev = self.get_y(arc.prev.site, x, self.get_sweep_line_y())
                if y_prev > y:
                    arc = arc.prev
                    continue
            if arc.next:
                y_next = self.get_y(arc.next.site, x, self.get_sweep_line_y())
                if y_next < y:
                    arc = arc.next
                    continue
            break
        return arc

    def compute_circle(self, a, b, c):
        # Compute the circle passing through points a, b, c
        # Returns (x_center, y_center, radius)
        ax, ay = a
        bx, by = b
        cx, cy = c
        # Calculate the determinant
        d = 2 * (ax*(by - cy) + bx*(cy - ay) + cx*(ay - by))
        if d == 0:
            return None
        # Calculate the circle's center coordinates
        x = ((ax**2 + ay**2)*(by - cy) + (bx**2 + by**2)*(cy - ay) + (cx**2 + cy**2)*(ay - by)) / d
        y = ((ax**2 + ay**2)*(cx - bx) + (bx**2 + by**2)*(ax - cx) + (cx**2 + cy**2)*(bx - ax)) / d
        # Calculate the radius
        r = math.hypot(ax - x, ay - y)
        return (x, y, r)

    def get_y(self, site, x, directrix):
        # Compute the y-coordinate of the parabola at x given the directrix
        px, py = site
        dp = 2 * (py - directrix)
        if dp == 0:
            return py
        a1 = 1 / dp
        b1 = -2 * px / dp
        c1 = (px * px + py * py - directrix * directrix) / dp
        return (a1 * x * x + b1 * x + c1)

    def get_sweep_line_y(self):
        if self.event_queue:
            return self.event_queue[0].y
        else:
            return self.y0 - (self.y1 - self.y0)

    def finish_edges(self):
        # Finish edges by extending them to the bounding box
        l = self.x0
        r = self.x1
        t = self.y1
        b = self.y0
        for edge in self.edges:
            if edge.end is None:
                p = edge.start
                dx, dy = edge.direction
                if dx == 0:
                    x = p[0]
                    if dy > 0:
                        y = t
                    else:
                        y = b
                else:
                    m = dy / dx
                    if dy > 0:
                        y = t
                        x = p[0] + (t - p[1]) / m
                    else:
                        y = b
                        x = p[0] + (b - p[1]) / m
                edge.end = (x, y)

# Now the rest of the code remains the same, but we need to make sure that edges have their end points.
