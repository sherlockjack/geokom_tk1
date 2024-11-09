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

    def check_circle_event(self, arc_above: Node, y_position):
        """
        Check for circle event involving the arc above and the arc to the left and right of it.
        """
        # Find the left and right neighbors of the arc above
        l_arc = self.get_left_neighbour(arc_above)
        m_arc = arc_above
        r_arc = self.get_right_neighbour(arc_above)
        l = l_arc.site if l_arc else None
        m = m_arc.site
        r = r_arc.site if r_arc else None

        lx, ly = l
        mx, my = m
        rx, ry = r

        if not l or not r: # if the arc above is the leftmost or rightmost arc
            return

        if self.collinear(l, m, r):
            return

        if ((my - ly) * (rx - lx) - (ry - ly) * (mx - lx)) > 0: # no possible circle event
            return

        c = self.circumcenter(l, m, r)

        radius = math.sqrt((c[0] - m[0]) ** 2 + (c[1] - m[1]) ** 2)
        upper_point = [c[0], radius + c[1]]

        if upper_point[1] < y_position: # no possible circle event
            return

        arc_above.circle_event = True
        l.circle_event = True
        r.circle_event = True
        return c, (l_arc, m_arc, r_arc)

    def get_left_neighbour(self, node: Node) -> Node:
        """Get the left neighbour (parabola) in the beachline."""
        current = node

        # Step 1: Move up the tree until we find a node that is a right child of its parent
        while current.parent and current.parent.left == current:
            current = current.parent

        # Step 2: If we reached the root and didn't find such a node, there's no left neighbour (node is the leftmost parabola)
        if not current.parent:
            return None

        # Step 3: Move to the left sibling
        current = current.parent.left

        # Step 4: Traverse down to find the right-most leaf
        while not current.is_leaf:
            current = current.right

        return current

    def get_right_neighbour(self, node: Node) -> Node:
        """Get the right neighbour (parabola) in the beachline."""
        current = node

        # Step 1: Move up the tree until we find a node that is a left child of its parent
        while current.parent and current.parent.right == current:
            current = current.parent

        # Step 2: If we reached the root and didn't find such a node, there's no right neighbour
        if not current.parent:
            return None

        # Step 3: Move to the right sibling
        current = current.parent.right

        # Step 4: Traverse down to find the left-most leaf
        while not current.is_leaf:
            current = current.left

        return current

    def collinear(self, p1, p2, p3):
        if p1 == p2 or p2 == p3 or p3 == p1:
            return True
        # Check if all points have the same x or y coordinate
        if p1[0] == p2[0] == p3[0] or p1[1] == p2[1] == p3[1]:
            return True
        # Calculate the area of the triangle formed by the three points
        # If the area is zero, the points are collinear
        return (p2[1] - p1[1]) * (p3[0] - p1[0]) == (p3[1] - p1[1]) * (p2[0] - p1[0])

    def circumcenter(self, p1, p2, p3):
        """ Check: ok
        compute the circumcenter
        INPUT: pi = [xi, yi]"""

        # no check for collinearity as they define a circle event!
        # auxiliaries functions
        midpoint = lambda p1, p2: ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        direction = lambda p1, p2: ((p1[0] - p2[0]), (p1[1] - p2[1]))
        inner_product = lambda x, y: -sum([x[i] * y[i] for i in range(len(x))])  # of the same length
        # l = n . (X - X0) = 0 => n.X0 = n.X
        line = lambda normal, point: (inner_product(normal, point), normal)

        midp1p2 = midpoint(p1, p2)
        midp2p3 = midpoint(p2, p3)
        # normal bisectors of pi, pj
        bisectp1p2 = line(direction(p1, p2), midp1p2)
        bisectp2p3 = line(direction(p2, p3), midp2p3)
        # As two lines intersect in one point
        c = self.lines_intersection(bisectp1p2, bisectp2p3)  # two lines intersect in
        return c

    def lines_intersection(self, l1, l2):
        """Find the intersection point of two lines given in the form [(a1, b1), c1]."""
        a1, b1 = l1[1][0], l1[1][1]
        a2, b2 = l2[1][0], l2[1][1]
        c1, c2 = -l1[0], -l2[0]

        # Calculate the determinant
        det = a1 * b2 - b1 * a2

        if det == 0:
            raise ValueError("Lines are parallel or coincident, no intersection found.")

        # by Cramer's rule
        x = (c1 * b2 - b1 * c2) / det
        y = (a1 * c2 - c1 * a2) / det

        return (x, y)

    def delete_arc(self, arc: Node):
        """Delete an arc from the beachline."""
        if not arc.is_leaf:
            raise ValueError("Cannot delete a non-leaf node.")

        # Find the parent of the arc to be deleted
        parent = arc.parent

        # Find the left and right neighbors
        left_neighbor = self.get_left_neighbour(arc)
        right_neighbor = self.get_right_neighbour(arc)

        # Remove the arc from the tree
        if parent is None:
            # If the arc is the root, set the root to None
            self.root = None
        else:
            # Determine if the arc is a left or right child
            if parent.left == arc:
                parent.left = None
            else:
                parent.right = None

        # If both neighbors exist, create a new breakpoint
        if left_neighbor and right_neighbor:
            # Create a new breakpoint node
            new_breakpoint = Node(is_leaf=False)
            new_breakpoint.sites = (left_neighbor.site, right_neighbor.site)

            # Set up the new breakpoint's children
            new_breakpoint.left = left_neighbor
            new_breakpoint.right = right_neighbor

            # Set parent pointers
            left_neighbor.parent = new_breakpoint
            right_neighbor.parent = new_breakpoint

            # Update the parent's child to the new breakpoint
            if parent is None:
                # If the deleted arc was the root, set the new breakpoint as the root
                self.root = new_breakpoint
            else:
                if parent.left == arc:
                    parent.left = new_breakpoint
                else:
                    parent.right = new_breakpoint