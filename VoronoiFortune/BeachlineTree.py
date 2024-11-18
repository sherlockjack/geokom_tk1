# TODO: Convert this to be usable for fortune's algorithm

class Node:
    def __init__(self, is_leaf = False):
        self.is_leaf = is_leaf
        self.left = None
        self.right = None
        self.parent = None
        self.height = 1  # Height of node starts at 1 for new leaf nodes

        # for leaf (arc) nodes
        self.site = None # site = (x, y)
        self.circle_event = None

        # for internal (breakpoint) nodes
        self.sites = None # (site, site)
        self.edge = None # Pointer to the half-edge in the DCEL (not yet implemented)

    def __repr__(self):
        if self.is_leaf:
            return f"LeafNode(site={self.site})"
        else:
            return f"BreakpointNode({self.sites})"

class BeachlineTree:
    def __init__(self):
        self.root = None

    def insert(self, site):
        """Insert a new site into the beachline, splitting the arc above it."""
        # If tree is empty, create first arc
        if self.root is None:
            new_arc = Node(is_leaf=True)
            new_arc.site = site
            self.root = new_arc
            return new_arc

        # Find the arc directly above the new site
        arc_above = self.find_arc_above(site)
        return self.split_arc(arc_above, site)

    def create_arc_node(self, site):
        """Helper function to create a new leaf node representing an arc."""
        node = Node(is_leaf=True)
        node.site = site
        return node

    def split_arc(self, arc_above, site):
        """
        Split an existing arc by a new site point.
        Returns the newly created middle arc (a1).

        Structure created:
               (p,q)
              /     \
            a0     (q,p)
                   /    \
                  a1    a2

        Where:
        - p is the focus of the original arc (arc_above)
        - q is the new site point
        - a0, a1, a2 are arcs in left-to-right order
        """
        # Create three arc nodes (leaves)
        a0 = self.create_arc_node(arc_above.site)  # Left copy of original arc
        a1 = self.create_arc_node(site)  # New arc from site
        a2 = self.create_arc_node(arc_above.site)  # Right copy of original arc

        # Create two breakpoint nodes
        left_breakpoint = Node(is_leaf=False)
        right_breakpoint = Node(is_leaf=False)

        # Set up the breakpoint sites
        left_breakpoint.sites = (arc_above.site, site)  # (p,q)
        right_breakpoint.sites = (site, arc_above.site)  # (q,p)

        # Build the tree structure
        left_breakpoint.left = a0
        left_breakpoint.right = right_breakpoint
        right_breakpoint.left = a1
        right_breakpoint.right = a2

        # Set parent pointers
        a0.parent = left_breakpoint
        right_breakpoint.parent = left_breakpoint
        a1.parent = right_breakpoint
        a2.parent = right_breakpoint

        # Replace the old arc in the tree
        if arc_above.parent is None:
            # If splitting the root
            self.root = left_breakpoint
            left_breakpoint.parent = None
        else:
            # If splitting a non-root arc
            left_breakpoint.parent = arc_above.parent
            if arc_above.parent.left == arc_above:
                arc_above.parent.left = left_breakpoint
            else:
                arc_above.parent.right = left_breakpoint

        # Transfer any circle event from the old arc
        # Important: The circle event should be invalidated as the arc is being split
        if arc_above.circle_event:
            a0.circle_event = None  # Circle event is no longer valid
            a2.circle_event = None  # Circle event is no longer valid

        return a1  # Return the middle arc for potential circle event checking

    # TEST FAILED
    def find_arc_above(self, site) -> Node:
        current = self.root
        while not current.is_leaf:
            current = current.left if site[0] < current.sites[0][0] else current.right
        return current

    # TEST FAILED
    # Modified from:
    # GitHub: https://github.com/akaalharbi/voronoi-fortune/blob/main/python/fortune.py
    def vertical_intersection(self, parabola:Node, point):
        """ Check:
        The parabola is given by its focal point where the directrix is
        y = point[1]. This function returns the intersection of the vertical line,
        passes through point,  and the parabola. (returns the y-coordinate of the intersection)
        --------------------
        INPUT: pi = [xi, yi] """
        px, py = parabola.site  # unpack them
        x0, y0 = point
        return ( (x0**2 - px**2)**2 + py**2 - y0**2) / (2*(py - y0))