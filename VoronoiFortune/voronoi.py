import heapq
from VoronoiFortune.BeachlineTree import BeachlineTree
from VoronoiFortune.fortune import circumcenter


class Event:
    def __init__(self, point, event_type, sites=None):
        self.point = point # Tuple (x, y)
        self.event_type = event_type  # 0 for site event, 1 for circle event
        self.sites = sites # List of sites involved in the circle event (3 sites)

    # Invert comparison to ensure the correct order in the max heap
    def __lt__(self, other):
        return self.point[1] > other.point[1]

    def __eq__(self, other):
        return self.point == other.point

    def __gt__(self, other):
        return self.point[1] < other.point[1]

    def __repr__(self):
        type_str = 'site' if self.event_type == 0 else 'circle'
        return f"Event({self.point}, {type_str})"

'''
Pseudocode for Fortune's algorithm

VoronoiDiagram(P: set of points):
Q = new PriorityQueue(P) # Site events
T = new BalancedBST() # Sweep status
D = new DCEL() # Voronoi diagram
while Q is not empty:
    event = Q.pop()
    if event is a site event:
        handle_site_event(event)
    else:
        a = arc on b that will disappear
        handle_circle_event(event)
treating the remaining internal nodes of T as unbounded edges_true of D (Vor(P))
return D

HandleSiteEvent(p: Point):
    # Step 1: Check if T is empty
    if T is empty:
        # Create a new arc for the first site and insert into T
        a1 = new arc for p
        insert_into_T(a1, T)
    else:
        # Step 2: Search for the arc a directly above p in T
        a = search_for_arc_above(p, T)

        # Step 3: Remove existing circle event if it exists
        if a has a circle event in Q:
            remove it from Q

        # Step 4: Split the arc a into three arcs
        a0, a1, a2 = split(a)

        # Step 5: Create new arc a1 for the site p
        a1 = new arc for p

        # Step 6: Update T
        # Replace arc a with new arcs a0, a1, and a2 in T
        replace_in_T(a, a0, a1, a2, T)

    # Step 7: Add edges_true to the DCEL (D)
    add_edge(q, p)  # edge from q to p
    add_edge(p, q)  # edge from p to q (if needed)

    # Step 8: Check for new circle events
    check_for_circle_events(., a0, a1)  # check for circle event involving a0, a1
    check_for_circle_events(a1, a2, .)  # check for circle event involving a1, a2
'''
'''
- Edges
- edges = [ [(p_k, p_l), [start, end] , boolean], ...]
-- (pj_k, p{j+1}_l) the two sites that are seperated by the edge.
-- end can be None untill it is discovered by a circle event.
-- boolean indicates it's a complete edge. This feature is for drawing.
- edges_true = [(start, end), ...] we may add the sites that they seperate.
'''
class VoronoiDiagram:
    def __init__(self, points):
        self.points = points # List of site points
        self.events = [Event(point, 0) for point in points]  if points else [] # Site events
        heapq.heapify(self.events)
        self.beachline = BeachlineTree()
        self.edges = []

    def compute_diagram(self):
        while self.events:
            event = heapq.heappop(self.events)
            self.handle_event(event)
        # TODO: treat the remaining internal nodes of T as unbounded edges_true of D (Vor(P))
        return self.D

    def handle_event(self, event: Event):
        if event and event.event_type == 0:
            self.handle_site_event(event)
        elif event and event.event_type == 1:
            self.handle_circle_event(event)

    def handle_site_event(self, event: Event):
        # Find the arc directly above the site event
        arc_above = self.beachline.find_arc_above(event.point)

        # Remove existing circle event if it exists
        if arc_above.circle_event:
            self.events.remove(arc_above.circle_event)
            arc_above.circle_event = None

        # Split the arc above
        self.beachline.split_arc(arc_above, event.point)

        # Find the y-coordinate where the vertical line from the site event intersects the beachline (arc above)
        y_position = self.beachline.vertical_intersection(arc_above, event.point)

        # TODO: Add the edge to the DCEL and another edge if possible (when the new site intersects with a breakpoint)

        # Check for new circle events
        circumcenter, sites = self.beachline.check_circle_event(arc_above, event.point[1]) # Check for circle events involving the arc above and the new arc at the site event's y-coordinate (current sweep line position)
        circle_event = Event(circumcenter, 1, sites)
        heapq.heappush(self.events, circle_event)

    def handle_circle_event(self, event):
        # Delete circle events (check if the neighboring arcs have circle events and remove them)
        l = event.sites[0]
        arc = event.sites[1]  # The middle arc will disappear
        r = event.sites[2]
        if l.circle_event:
            try:
                self.events.remove(l.circle_event)
            except ValueError:
                pass
            l.circle_event = None
        if r.circle_event:
            try:
                self.events.remove(r.circle_event)
            except ValueError:
                pass
            r.circle_event = None

        # TODO: Add the vertex and edge to the diagram

        # Find the arc that will disappear and delete it
        self.beachline.delete_arc(arc)  # TODO: Implement the delete_arc method

        # Check for new circle events
        circumcenter, sites = self.beachline.check_circle_event(arc, event.point[1])

