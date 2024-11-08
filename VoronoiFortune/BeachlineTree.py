# TODO: Convert this to be usable for fortune's algorithm
import math


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
    def __init__(self, root:Node=None):
        self.root = root

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
        Handles both one and two breakpoint scenarios.

        Args:
            arc_above: The Node instance representing the arc to split.
            site: The new site tuple (x, y).
            breakpoints: List of current breakpoints between arc_above and its neighbors.

        Returns:
            The newly created middle arc (a1).
        """
        if arc_above.site[1] == site[1]:
            # Single breakpoint scenario
            # Structure:
            #        (p, q)
            #       /      \
            #      a0      a1
            p = arc_above.site
            q = site

            # Create two arc nodes
            a0 = self.create_arc_node(p)  # Left copy of original arc
            a1 = self.create_arc_node(q)  # New arc from site

            # Create one breakpoint node
            breakpoint = Node(is_leaf=False)
            breakpoint.sites = (p, q)  # (p, q)

            # Build the tree structure
            breakpoint.left = a0
            breakpoint.right = a1

            # Set parent pointers
            a0.parent = breakpoint
            a1.parent = breakpoint

            # Replace the old arc in the tree
            if arc_above.parent is None:
                # If splitting the root
                self.root = breakpoint
                breakpoint.parent = None
            else:
                # If splitting a non-root arc
                breakpoint.parent = arc_above.parent
                if arc_above.parent.left == arc_above:
                    arc_above.parent.left = breakpoint
                else:
                    arc_above.parent.right = breakpoint

            # Transfer any circle event from the old arc
            if arc_above.circle_event:
                a0.circle_event = None  # Circle event is no longer valid

            return a1  # Return the new arc for potential circle event checking

        else:
            # Two breakpoints scenario
            # Structure created:
            #        (p, q)
            #       /      \
            #      a0    (q, p)
            #           /      \
            #          a1      a2

            p = arc_above.site
            q = site

            # Create three arc nodes (leaves)
            a0 = self.create_arc_node(p)  # Left copy of original arc
            a1 = self.create_arc_node(q)  # New arc from site
            a2 = self.create_arc_node(p)  # Right copy of original arc

            # Create two breakpoint nodes
            left_breakpoint = Node(is_leaf=False)
            right_breakpoint = Node(is_leaf=False)

            # Set up the breakpoint sites
            left_breakpoint.sites = (p, q)  # (p, q)
            right_breakpoint.sites = (q, p)  # (q, p)

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
            if arc_above.circle_event:
                a0.circle_event = None  # Circle event is no longer valid
                a2.circle_event = None  # Circle event is no longer valid

            return a1  # Return the middle arc for potential circle event checking

    def find_arc_above(self, site):
        """
        Find the arc in the beachline that lies directly above the given site.

        Args:
            site: The new site tuple (x, y).

        Returns:
            A tuple containing:
                - The Node instance representing the arc above.
                - The list of current breakpoints between this arc and its neighbors.
        """
        current = self.root
        directrix = site[1]

        while not current.is_leaf:
            parabola1, parabola2 = current.sites
            # handle the case where the new site is at the same y-coordinate as the focus of one of the parabolas
            if parabola1[1] == directrix or parabola2[1] == directrix:
                if parabola1[0] < site[0]:
                    current = current.right
                else:
                    current = current.left
                continue
            breakpoints = self.compute_breakpoints(parabola1, parabola2, directrix)

            if not breakpoints:
                raise ValueError("No intersection found between parabolas")

            if len(breakpoints) == 1:
                # Only one breakpoint, decide based on x-coordinate
                x, _ = breakpoints[0]
                if site[0] <= x:
                    current = current.left
                else:
                    current = current.right
            elif len(breakpoints) == 2:
                # Two breakpoints
                # if the first breakpoint site is higher than the second breakpoint site, take the left breakpoint
                x1, _ = breakpoints[0]
                x2, _ = breakpoints[1]
                if current.sites[0][1] > current.sites[1][1]:
                    if site[0] <= x1:
                        current = current.left
                    else:
                        current = current.right
                else:
                    if site[0] <= x2:
                        current = current.left
                    else:
                        current = current.right
            else:
                raise ValueError("Unexpected number of breakpoints computed.")

        return current

    def compute_breakpoints(self, parabola1, parabola2, directrix):
        """
        Compute the intersection points (breakpoints) between two upward-facing parabolas.

        Args:
            parabola1: First parabola focus point (x1, y1)
            parabola2: Second parabola focus point (x2, y2)
            directrix: y-coordinate of the directrix (horizontal line)

        Returns:
            List of (x,y) coordinates where the parabolas intersect.
            Can return 0, 1, or 2 points depending on if/how parabolas intersect.
        """
        # Extract focus points
        x1, y1 = parabola1
        x2, y2 = parabola2

        def get_y_coordinate(x, focus):
            """Calculate the y-coordinate of a parabola given x and focus point."""
            x1, y1 = focus
            return ((x - x1) ** 2 + y1 ** 2) / (2 * (y1 - directrix))

        # If the foci and directrix are identical, parabolas are the same
        if x1 == x2 and y1 == y2:
            return []

        if y1 == y2: # if the foci are on the same line, the parabolas are parallel, return the midpoint
            return [[(x1 + x2) / 2, get_y_coordinate((x1 + x2) / 2, parabola1)]]

        # Calculate quadratic coefficients
        a = (1 / (2 * (y1 - directrix))) - (1 / (2 * (y2 - directrix)))
        b = (x2 / (y2 - directrix)) - (x1 / (y1 - directrix))
        c = ((x1 ** 2 + y1 ** 2 - directrix ** 2) / (2 * (y1 - directrix))) - \
            ((x2 ** 2 + y2 ** 2 - directrix ** 2) / (2 * (y2 - directrix)))

        # If a is zero, parabolas don't intersect properly (division by zero)
        if abs(a) < 1e-10:
            return []

        # Calculate discriminant
        discriminant = b * b - 4 * a * c

        # No real solutions if discriminant is negative
        if discriminant < 0:
            return []

        # One solution if discriminant is zero
        if abs(discriminant) < 1e-10:
            x = -b / (2 * a)
            y = get_y_coordinate(x, parabola1)
            return [(x, y)]

        # Two solutions if discriminant is positive
        x1 = (-b + math.sqrt(discriminant)) / (2 * a)
        x2 = (-b - math.sqrt(discriminant)) / (2 * a)
        x1, x2 = min(x1, x2), max(x1, x2)  # Ensure x1 < x2
        # Calculate corresponding y coordinates
        points = []
        y1 = get_y_coordinate(x1, parabola1)
        y2 = get_y_coordinate(x2, parabola1)
        points.append((x1, y1))
        points.append((x2, y2))
        return points

    # UNTESTED
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
        return ((x0 - px) ** 2 + py ** 2 - y0 ** 2)/(2*(py-y0))