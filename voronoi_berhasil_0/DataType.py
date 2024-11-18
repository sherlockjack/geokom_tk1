
class Point:
   x = 0.0
   y = 0.0
   
   def __init__(self, x, y):
       self.x = x
       self.y = y
       
class Node:
   p = None
   arc = None  
   def __init__(self,p):
        self.node = None
        self.p = p
        self.arc = None
        self.left = None
        self.right = None
        self.height = 1 
    
class Event:
    x = 0.0       # This is the max x coord of circle
    p = None      # This is the center of the circle
    pprev = None  # These are the prev and prior points of the circle
    pnext = None
    a = None      # This is the middle arc of the circle
    valid = True
    
    def __init__(self, x, p, a):
        self.x = x
        self.p = p
        pprev = None
        pnext = None
        self.a = a
        self.valid = True

class Arc:
    number = None
    p = None
    aprev = None
    anext = None
    left = None
    right = None
    height = 1
    node = None
    e = None
    s0 = None
    s1 = None
    
    def __init__(self, p, a=None, b=None):
        self.p = p
        self.aprev = a
        self.anext = b
        self.e = None
        self.s0 = None
        self.s1 = None

class Segment:
    start = None
    end = None
    done = False
    sites = None  

    
    def __init__(self, p):
        self.start = p
        self.end = None
        self.done = False
        self.sites = []  # Initialize the list

    def finish(self, p):
        if self.done: return
        self.end = p
        self.done = True        

