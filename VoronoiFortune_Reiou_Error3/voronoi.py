import heapq
import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Event:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.valid = True  # For circle events to detect invalidated events


    def __lt__(self, other):
        # For the priority queue (max-heap based on y-coordinate)
        return self.y > other.y or (self.y == other.y and self.x < other.x)


class SiteEvent(Event):
    def __init__(self, point):
        super().__init__(point.y, point.x)
        self.point = point


class CircleEvent(Event):
    def __init__(self, y, x, center, arc):
        super().__init__(y, x)
        self.center = center  # Circle center
        self.arc = arc        # The arc that will disappear


class Arc:
    def __init__(self, site):
        self.site = site
        self.prev = None
        self.next = None
        self.circle_event = None
        self.edge_left = None
        self.edge_right = None


class Edge:
    def __init__(self, start, direction):
        self.start = start  # Starting point of the edge
        self.direction = direction  # Direction vector
        self.end = None  # Endpoint, if known
        self.neighbor = None  # Twin edge in DCEL


class Voronoi:
    def __init__(self, sites):
        self.sites = [Point(x, y) for x, y in sites]
        self.event_queue = []
        self.output = []
        self.beach_line = None
        self.edges = []
        self.vertices = []
        self.sweep_line = None


    def run(self):
        # Initialize the event queue with site events
        for site in self.sites:
            heapq.heappush(self.event_queue, SiteEvent(site))


        # Process the events
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.sweep_line = event.y
            if not event.valid:
                continue
            if isinstance(event, SiteEvent):
                self.handle_site_event(event)
            elif isinstance(event, CircleEvent):
                self.handle_circle_event(event)


        # Finish the edges (edges to infinity)
        self.finish_edges()
        return self.edges


    def handle_site_event(self, event):
        site = event.point
        if self.beach_line is None:
            # Create the first arc
            self.beach_line = Arc(site)
            return


        arc = self.find_arc_above(site.x)
        if arc.circle_event:
            arc.circle_event.valid = False


        # Create new edges
        start_point = Point(site.x, self.get_y(arc.site, site.x, self.sweep_line))
        edge_left = Edge(start_point, None)
        edge_right = Edge(start_point, None)
        edge_left.neighbor = edge_right
        edge_right.neighbor = edge_left
        self.edges.append(edge_left)
        self.edges.append(edge_right)


        # Replace arc with three new arcs
        arc_right = Arc(arc.site)
        arc_left = Arc(arc.site)
        arc_middle = Arc(site)


        # Re-link arcs
        arc_left.prev = arc.prev
        arc_left.next = arc_middle
        arc_middle.prev = arc_left
        arc_middle.next = arc_right
        arc_right.prev = arc_middle
        arc_right.next = arc.next


        if arc_left.prev:
            arc_left.prev.next = arc_left
        if arc_right.next:
            arc_right.next.prev = arc_right


        arc_left.edge_right = edge_left
        arc_right.edge_left = edge_right
        arc_middle.edge_left = edge_left
        arc_middle.edge_right = edge_right


        # Replace in beach line
        if arc == self.beach_line:
            self.beach_line = arc_left


        # Check for circle events
        self.check_circle_event(arc_left)
        self.check_circle_event(arc_right)


    def handle_circle_event(self, event):
        arc = event.arc
        if not arc.circle_event.valid:
            return


        # Create vertex at circle event
        vertex = Point(event.center.x, event.center.y)
        self.vertices.append(vertex)


        # Update edges
        if arc.edge_left:
            arc.edge_left.end = vertex
        if arc.edge_right:
            arc.edge_right.end = vertex


        # Remove arc from beach line
        if arc.prev:
            arc.prev.next = arc.next
            arc.prev.edge_right = Edge(vertex, None)
            self.edges.append(arc.prev.edge_right)
        if arc.next:
            arc.next.prev = arc.prev
            arc.next.edge_left = Edge(vertex, None)
            self.edges.append(arc.next.edge_left)


        # Invalidate circle events
        if arc.prev:
            self.check_circle_event(arc.prev)
        if arc.next:
            self.check_circle_event(arc.next)


    def finish_edges(self):
        # Extend edges to infinity
        pass  # Implement as needed


    def find_arc_above(self, x):
        arc = self.beach_line
        while arc:
            x_left = self.get_breakpoint(arc.prev, arc, self.sweep_line) if arc.prev else float('-inf')
            x_right = self.get_breakpoint(arc, arc.next, self.sweep_line) if arc.next else float('inf')
            if x_left <= x <= x_right:
                return arc
            elif x < x_left:
                arc = arc.prev
            else:
                arc = arc.next
        return None


    def get_breakpoint(self, arc_left, arc_right, directrix):
        site_left = arc_left.site
        site_right = arc_right.site


        # Handle special cases where sites have the same y-coordinate
        if site_left.y == site_right.y:
            return (site_left.x + site_right.x) / 2.0


        # Compute breakpoint
        d_left = 2.0 * (site_left.y - directrix)
        d_right = 2.0 * (site_right.y - directrix)


        a = 1.0 / d_left - 1.0 / d_right
        b = -2.0 * (site_left.x / d_left - site_right.x / d_right)
        c = (site_left.x**2 + site_left.y**2 - directrix**2) / d_left - (site_right.x**2 + site_right.y**2 - directrix**2) / d_right


        discriminant = b**2 - 4 * a * c
        if discriminant < 0:
            return None
        x1 = (-b + math.sqrt(discriminant)) / (2 * a)
        x2 = (-b - math.sqrt(discriminant)) / (2 * a)
        if site_left.y < site_right.y:
            return max(x1, x2)
        else:
            return min(x1, x2)


    def get_y(self, site, x, directrix):
        # Compute the y-coordinate of the parabola at x
        dp = 2.0 * (site.y - directrix)
        if dp == 0:
            return site.y
        return ((x - site.x)**2) / dp + (dp / 4.0) + directrix


    def check_circle_event(self, arc):
        if arc.circle_event:
            arc.circle_event.valid = False
        if not arc.prev or not arc.next:
            return


        A = arc.prev.site
        B = arc.site
        C = arc.next.site


        # Check if points are counterclockwise
        if (B.x - A.x)*(C.y - A.y) - (B.y - A.y)*(C.x - A.x) >= 0:
            return


        # Compute circle center
        ax = A.x
        ay = A.y
        bx = B.x
        by = B.y
        cx = C.x
        cy = C.y


        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if d == 0:
            return


        ux = ((ax**2 + ay**2)*(by - cy) + (bx**2 + by**2)*(cy - ay) + (cx**2 + cy**2)*(ay - by)) / d
        uy = ((ax**2 + ay**2)*(cx - bx) + (bx**2 + by**2)*(ax - cx) + (cx**2 + cy**2)*(bx - ax)) / d
        radius = math.hypot(ux - ax, uy - ay)


        # Bottom of the circle
        y = uy - radius
        if y >= self.sweep_line:
            return


        center = Point(ux, uy)
        event = CircleEvent(y, ux, center, arc)
        arc.circle_event = event
        heapq.heappush(self.event_queue, event)


# Example usage
sites = [(1.0, 2.5), (3.2, 4.8), (5.0, 7.3), (6.1, 3.9), (9.5, 1.2), (2.2, 8.0)]
voronoi = Voronoi(sites)
edges = voronoi.run()


# Output edges
for edge in voronoi.edges:
    print(f"Edge from ({edge.start.x}, {edge.start.y}) to ", end="")
    if edge.end:
        print(f"({edge.end.x}, {edge.end.y})")
    else:
        print("infinity")