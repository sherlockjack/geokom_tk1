
import math, heapq

from DataType import Point, Event, Arc, Node, Segment

from BinaryTree import AVLTree

# Source: (C++) http://www.cs.hmc.edu/~mbrubeck/voronoi.html

class Voronoi:
    def __init__(self, coords):
        self.output = [] # list of line segment
        self.arc = None  # first (lowest) parabola (arc)

        self.points = []
        self.rawpoints = []
        self.event = [] # circle events
        
        self.priorpt = None
        self.node = None
        self.arcno = 0
        self.curx = None
        self.verbose = True
        self.firstx = None
        
        self.bt = AVLTree()
        
        # bounding box
        self.x0 = -50.0
        self.x1 = -50.0
        self.y0 = 550.0
        self.y1 = 550.0

        # insert points to site event
        
        for pts in coords:
            point = Point(pts[0], pts[1])
                # eliminate any duplicate point
            self.rawpoints.append(point)
                # keep track of bounding box size
            if point.x < self.x0: self.x0 = point.x
            if point.y < self.y0: self.y0 = point.y
            if point.x > self.x1: self.x1 = point.x
            if point.y > self.y1: self.y1 = point.y

        # add margins to the bounding box
        dx = (self.x1 - self.x0 + 1) / 5.0
        dy = (self.y1 - self.y0 + 1) / 5.0
        self.x0 = self.x0 - dx
        self.x1 = self.x1 + dx
        self.y0 = self.y0 - dy
        self.y1 = self.y1 + dy

        self.points = sorted(self.rawpoints,key = lambda p:[p.x,p.y], reverse = True)
        
    def process(self):
        root = None
        self.arcno = 0
        while len(self.points) > 0:
            
            if len(self.event) > 0: priority, e = self.event[0]
            else: e = None
            
            if e is not None and (e.x <= self.points[len(self.points)-1].x):
                root = self.process_event(root) # handle circle event
            else:
                if self.priorpt is None or \
                   self.points[len(self.points)-1].x != self.priorpt.x or \
                   self.points[len(self.points)-1].y != self.priorpt.y :
                       
                    self.priorpt = self.points[len(self.points)-1]
                    root = self.process_point(root) # handle site event
                else:
                    print("Removing duplicate")
                    p = self.points.pop()
                    

        # after all points, process remaining circle events
        while len(self.event) > 0:
            root = self.process_event(root)

        self.finish_edges()

        if not self.verbose:
            print("Convex hull at end:")
            self.bt.printHelper(root, "", True)
            arc = self.arc
            string = " "
            while arc is not None:
                string = string + str(arc.number) + " "
                arc = arc.anext
            print(string)

        

    def process_point(self, root):
        # get next event from site pq
        p = self.points.pop()
        self.curx = p.x
        print("Adding p:",round(p.x),round(p.y))
        
        # add new arc (parabola)
        root = self.arc_insert(root, p)
        return root

    def process_event(self, root):
        # get next event from circle pq
        priority, e = heapq.heappop(self.event)
        self.curx = e.x
        if e.valid:
            
            a = e.a
            if self.verbose: print("At x:",round(e.x),"Removing: ",e.a.number,round(a.p.y),int(e.pprev.y),int(e.pnext.y))

            root = self.bt.delete_node(root, e)
            
            if self.verbose: 
                self.bt.printHelper(root, "", True)
            
            # start new edge
            s = Segment(e.p)
            s.sites = [a.aprev.p, a.p, a.anext.p]  # Store the three sites
            self.output.append(s)

            # remove associated arc (parabola)

            if a.aprev != None:
                a.aprev.anext = a.anext
                a.aprev.s1 = s
            if a.anext != None:
                a.anext.aprev = a.aprev
                a.anext.s0 = s

            # finish the edges before and after a
            if a.s0 != None: a.s0.finish(e.p)
            if a.s1 != None: a.s1.finish(e.p)

            # recheck circle events on either side of p
            if a.aprev != None: self.check_circle_event(a.aprev, e.x)
            if a.anext != None: self.check_circle_event(a.anext, e.x)

            if self.verbose:
                arc = self.arc
                string = "Del "
                while arc is not None:
                    string = string + str(arc.number) + " "
                    arc = arc.anext
                print(string)

        else:
            a = e.a
            if self.verbose: print("At x:",round(e.x),"Ignoring: ",round(a.p.y),int(e.pprev.y),int(e.pnext.y))

            
        return root

    def arc_insert(self, root, p):
        if self.arc == None:
            self.arc = Arc(p)
            self.arcno = self.arcno+1
            self.arc.number = self.arcno
            root = Node(p)
            root.arc = self.arc
            self.firstx = p.x
        else:
            # find the current arcs at p.y
            
            self.bt.nodea = None            
            root = self.bt.insert_node(root, p)

            if self.verbose:
                print("BT start:",self.bt.basen.arc.number, \
                      round(self.bt.basen.arc.p.y))
            
            i = self.bt.basen.arc
            
            if p.x != self.firstx:
                flag, z = self.intersect(p, i)
                if flag:    # true if new parabola intersects arc i

                    flag, zz = self.intersect(p, i.anext)
                    
                    if (i.anext is not None) and (not flag):
                        # anext exists and p does not on anext
                        i.anext.aprev = Arc(i.p, i, i.anext)
                        i.anext = i.anext.aprev
                    else:
                        # No anext or p is on anext
                        i.anext = Arc(i.p, i)

                    
                    i.anext.s1 = i.s1

                    # add arc defined by p  between i and i.anext
                    i.anext.aprev = Arc(p, i, i.anext)
                    i.anext = i.anext.aprev

                    i = i.anext # now i points to the new arc
                    
                    
                    self.arcno = self.arcno+1
                    i.number = self.arcno 
                    self.arcno = self.arcno+1
                    i.anext.number = self.arcno

                    i.node = self.bt.nodea
                    self.bt.nodea.arc = i
                    
                    root = self.bt.insert_node(root, p)

                    i.anext.node = self.bt.nodeb
                    self.bt.nodeb.p = i.anext.p
                    self.bt.nodeb.arc = i.anext
                    
                    if self.verbose: self.bt.printHelper(root, "", True)

                    # add new half-edges connected to i's endpoints
                    seg = Segment(z)
                    seg.sites = [i.aprev.p, i.p, p]  # Store sites for left segment
                    self.output.append(seg)
                    i.aprev.s1 = i.s0 = seg

                    seg = Segment(z)
                    seg.sites = [i.p, p, i.anext.p]
                    self.output.append(seg)
                    i.anext.s0 = i.s1 = seg

                    # check for new circle events around the new arc
                    self.check_circle_event(i, p.x)
                    self.check_circle_event(i.aprev, p.x)
                    self.check_circle_event(i.anext, p.x)

                    if self.verbose:
                        arc = self.arc
                        string = "Ins "
                        while arc is not None:
                            string = string + str(arc.number) + " "
                            arc = arc.anext
                        print(string)
                    
                    return root

            # If p is subsequent point on sweep line start
            else:
                i.anext = Arc(p, i)
                self.arcno = self.arcno+1
                i.anext.number = self.arcno
                i.anext.node = self.bt.nodea
                self.bt.nodea.arc = i.anext
            
                # Insert new segment between p and i
                # Initial point starts at x0
                x = self.x0
                y = (i.anext.p.y + i.p.y) / 2.0;
                start = Point(x, y)

                seg = Segment(start)
                i.s1 = i.anext.s0 = seg
                self.output.append(seg)

                if self.verbose: self.bt.printHelper(root, "", True)

                if self.verbose:
                    arc = self.arc
                    string = "Ins "
                    while arc is not None:
                        string = string + str(arc.number) + " "
                        arc = arc.anext
                    print(string)

        return root
            

    def check_circle_event(self, i, x0):
        # look for a new circle event for arc i

        # invalidate a prior event referenced in arc      
        if (i.e != None): # and (i.e.x  != self.x0):
            i.e.valid = False
            
            if self.verbose: print("At x:",round(self.curx),"Invalid: ", \
                i.number,round(i.p.y),round(i.e.pprev.y),round(i.e.pnext.y))
            
        # reset reference to event in arc
        i.e = None

        if (i.aprev == None) or (i.anext == None): return

        # create a new event if possible from arc and its next and previous
        # Assure that x is defined
        flag, x, o = self.circle(i.aprev.p, i.p, i.anext.p)
        if flag: #and x != None:
            i.e = Event(x, o, i)
            i.e.pprev = i.aprev.p
            i.e.pnext = i.anext.p
            if self.verbose: print("At x:", round(self.curx),\
                                   "Adding c:",round(x),";",round(i.p.y),\
                                   round(i.aprev.p.y),round(i.anext.p.y))
            entry = [i.e.x,i.e]
            heapq.heappush(self.event,entry)
            #self.event.push(i.e)

    def circle(self, a, b, c):
        # check if bc is a "right turn" from ab
        if ((b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y)) > 0: return False, None, None

        # Joseph O'Rourke, Computational Geometry in C (2nd ed.) p.189
        A = b.x - a.x
        B = b.y - a.y
        C = c.x - a.x
        D = c.y - a.y
        E = A*(a.x + b.x) + B*(a.y + b.y)
        F = C*(a.x + c.x) + D*(a.y + c.y)
        G = 2*(A*(c.y - b.y) - B*(c.x - b.x))

        if (G == 0): return False, None, None # Points are co-linear

        # point o is the center of the circle
        ox = 1.0 * (D*E - B*F) / G
        oy = 1.0 * (A*F - C*E) / G

        # o.x plus radius equals max x coord
        x = ox + math.sqrt((a.x-ox)**2 + (a.y-oy)**2)
        o = Point(ox, oy)
           
        return True, x, o
# In Voronoi.py, inside the Voronoi class

    def compute_circles(self):
        circles = []
        for seg in self.output:
            if seg.start and seg.end and seg.sites:
                # The vertex is at the intersection of edges
                vertex = seg.start
                sites = seg.sites
                if len(sites) >= 3:
                    # Compute circle centered at vertex passing through the sites
                    circle = self.circumcircle(sites[0], sites[1], sites[2])
                    if circle:
                        # Check if the circle is empty
                        if self.is_circle_empty(circle, sites):
                            circles.append(circle)
        return circles

    def circumcircle(self, a, b, c):
        # Compute the circumcircle of three points a, b, c
        # Returns a tuple (center_point, radius)
        # Using the formula for circumcircle
        d = 2 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y))
        if d == 0:
            return None  # Points are colinear
        ux = ((a.x**2 + a.y**2) * (b.y - c.y) +
            (b.x**2 + b.y**2) * (c.y - a.y) +
            (c.x**2 + c.y**2) * (a.y - b.y)) / d
        uy = ((a.x**2 + a.y**2) * (c.x - b.x) +
            (b.x**2 + b.y**2) * (a.x - c.x) +
            (c.x**2 + c.y**2) * (b.x - a.x)) / d
        center = Point(ux, uy)
        radius = math.hypot(center.x - a.x, center.y - a.y)
        return (center, radius)

    def is_circle_empty(self, circle, sites):
        center, radius = circle
        for p in self.rawpoints:
            if p in sites:
                continue  # Skip the sites that define the circle
            dist = math.hypot(center.x - p.x, center.y - p.y)
            if dist < radius:
                return False  # A site is inside the circle
        return True

    def get_largest_empty_circles(self):
        circles = self.compute_circles()
        if not circles:
            return []
        # Find the maximum radius
        max_radius = max([circle[1] for circle in circles])
        # Collect all circles with the maximum radius
        largest_circles = [circle for circle in circles if circle[1] == max_radius]
        return largest_circles



    def intersect(self, p, i):
        # check whether a new parabola at point p intersect with arc i
        if (i is None): return False, None
        if (i.p.x == p.x): return False, None

        a = 0.0
        b = 0.0

        if i.aprev is not None:
            a = (self.bt.intersection(i.aprev.p, i.p, 1.0*p.x)).y
        if i.anext is not None:
            b = (self.bt.intersection(i.p, i.anext.p, 1.0*p.x)).y

        if (((i.aprev is None) or (a <= p.y)) and ((i.anext is None) or (p.y <= b))):
            py = p.y
            px = 1.0 * ((i.p.x)**2 + (i.p.y-py)**2 - p.x**2) / (2*i.p.x - 2*p.x)
            res = Point(px, py)
            return True, res
        return False, None
    
    def finish_edges(self):
        l = self.x1 + (self.x1 - self.x0) + (self.y1 - self.y0)
        i = self.arc
        while i.anext is not None:
            if i.s1 is not None:
                p = self.bt.intersection(i.p, i.anext.p, l*2.0)
                i.s1.finish(p)
            i = i.anext

    def print_output(self):
        it = 0
        for o in self.output:
            it = it + 1
            p0 = o.start
            p1 = o.end
            print (p0.x, p0.y, p1.x, p1.y)

    def get_output(self):
        res = []
        for o in self.output:
            p0 = o.start
            p1 = o.end
            res.append((round(p0.x), round(p0.y), round(p1.x), round(p1.y)))
        return res
