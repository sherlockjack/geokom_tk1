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
        self.n = None # Node
        self.p = p
        self.arc = None
        self.left = None
        self.right = None
        self.height = 1 

class Event:
    x = 0.0       # Koordinat maksimum dari lingkaran
    p = None      # Pusat lingkaran
    pprev = None  # Titik sebelumnya dari lingkaran
    pnext = None  # Titik berikutnya dari lingkaran
    a = None      # Busur tengah dari lingkaran
    valid = True
    
    def __init__(self, x, p, a):
        self.x = x
        self.p = p
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
        self.sites = []  # Inisialisasi list 

    def finish(self, p):
        if self.done: return
        self.end = p
        self.done = True      