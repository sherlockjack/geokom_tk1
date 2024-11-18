from Components import Point, Node, Event
import sys, math

class AVLTree(object):
    def __init__(self):
        self.node = None
        self.basen = None
        self.nodea = None
        self.nodeb = None
        self.pp = None
        self.pn = None
        
    # dapatkan titik representatif pada busur
    def chkpt(self,n,p):
        
        self.pp = None
        self.pn = None
        
        if n.arc is None: return n.p
        
        if n.arc.number != 1 and n.arc.aprev is None and n.arc.anext is None:
            self.pp = n.arc.p
            self.pn = n.arc.p
            return
        
        if (n.arc.anext is not None):
            self.pn = self.intersection(n.arc.p, n.arc.anext.p, p.x)
        else: self.pn = None

        if (n.arc.aprev is not None):
            self.pp = self.intersection(n.arc.aprev.p, n.arc.p, p.x)
        else: self.pp = None

    def intersection(self, p0, p1, X):
        # dapatkan intersection dari dua parabola
        p = p0
        if (p0.x == p1.x):
            py = (p0.y + p1.y) / 2.0
        elif (p1.x == X):
            py = p1.y
        elif (p0.x == X):
            py = p0.y
            p = p1
        else:
            # rumus kuadrat
            z0 = 2.0 * (p0.x - X)
            z1 = 2.0 * (p1.x - X)

            a = 1.0/z0 - 1.0/z1
            b = -2.0 * (p0.y/z0 - p1.y/z1)
            c = 1.0 * (p0.y**2 + p0.x**2 - X**2) / z0 - 1.0 * (p1.y**2 + p1.x**2 - X**2) / z1

            py = 1.0 * (-b-math.sqrt(b*b - 4*a*c)) / (2*a)
            
        px = 1.0 * (p.x**2 + (p.y-py)**2 - X**2) / (2*p.x-2*X)
        res = Point(px, py)
        return res
    
    # insert node, dimana p adalah point yang diinsert dan berada di arc a
    def insert_node(self, root, p):
 
        # cari lokasi yang benar dan insert node
        if not root:
            return root

        self.chkpt(root,p)
        
        if self.should_go_left(root, p):
            root.left = self.insert_node(root.left, p)
        elif self.should_go_right(root, p): 
              root.right = self.insert_node(root.right, p)        
        else:
            self.insert_node_at_base(root, p)

        # update balance factor dan balance tree
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
        balance_factor = self.get_balance(root)
        
        # balance tree
        if balance_factor > 1:
            if self.get_balance(root.left) >= 0:
                return self.right_rotate(root)
            else:
                root.left = self.left_rotate(root.left)
                return self.right_rotate(root)
        if balance_factor < -1:
            if self.get_balance(root.right) <= 0:
                return self.left_rotate(root)
            else:
                root.right = self.right_rotate(root.right)
                return self.left_rotate(root)

        return root
    

    def should_go_left(self, root, p):
        return (self.pp is not None and p.y < self.pp.y) and (root.left is not None)

    def should_go_right(self, root, p):
        return (root.right is not None and (root.arc.p.x == p.x and root.arc.p.y != p.y or not ( (self.pp is None and self.pn is None) 
                or (self.pp is not None and self.pn is not None and self.pn.y == self.pp.y)
                or (self.pn is None and self.pp is not None and p.y > self.pp.y)
                or (self.pp is None and self.pn is not None and p.y < self.pn.y) 
                or (self.pn is not None and self.pp is not None and p.y < self.pn.y and self.pp.y < p.y))))

    def insert_node_at_base(self, root, p):
        self.basen = root
            
        if  root.right is None:
            n = Node(p)
            if self.nodea is None:
                self.nodea = n
            else:
                self.nodeb = n                
            root.right = n

        else:
            temp = self.get_min_value_node(root.right)
            n = Node(p)
            if self.nodea is None:
                self.nodea = n
            else:
                self.nodeb = n                
            temp.left = n
    
        # update balance factor dan balance tree
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))

    # e.a = arc yang akan diremove
    # Point(e.x,e.p.y) = high point dari arc
    def delete_node(self, root, e):
        if not root:
            return None
        
        p = Point(e.x,e.p.y)
        self.chkpt(root,p)

        # dapatkan bagian depan dan belakang untuk arc saat ini
        # p adalah titik tertinggi lingkaran
        if root.arc.aprev is not None and (root.arc.number != e.a.number) and (p.y <= self.pp.y) or root.arc.aprev.number == e.a.number:
            root.left = self.delete_node(root.left, e)                
        elif root.arc.number != e.a.number:
            root.right = self.delete_node(root.right, e)       
        else:
            # arc ketemu
            if root.left is None:
                temp = root.right
                root = None
                return temp
            elif root.right is None:
                temp = root.left
                root = None
                return temp
            
            temp = self.get_min_value_node(root.right)
            
            root.p = temp.p
            root.arc = temp.arc
            
            p = Point(e.x,e.p.y)
            self.chkpt(temp,p)
            if self.pn is None:
                self.pn = self.pp
                self.pn.y = 2*self.pn.y
            et = Event(e.x, Point(0,0),temp.arc)
            
            root.right = self.delete_node(root.right, et)
        
            # update balace factor dari nodes
            root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
            
        return root

    def left_rotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def right_rotate(self, z):
        y = z.left
        if y != None: T3 = y.right
        else: T3 = None
        y.right = z
        z.left = T3
        z.height = 1 + max(self.get_height(z.left),
                           self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left),
                           self.get_height(y.right))
        return y

    def get_height(self, root):
        if not root:
            return 0
        return root.height

    # get balance factor
    def get_balance(self, root):
        if not root:
            return 0
        return self.get_height(root.left) - self.get_height(root.right)

    def get_min_value_node(self, root):       
        if root is None or root.left is None:
            return root      
        return self.get_min_value_node(root.left)

    # print the tree
    def print_helper(self, currPtr, indent, last):
        if currPtr != None:
            sys.stdout.write(indent)
            if last:
                sys.stdout.write("R----")
                indent += "     "
            else:
                sys.stdout.write("L----")
                indent += "|    "
            if currPtr.arc is not None:
                print(currPtr.arc.number,round(currPtr.p.y))
            else:
                print(round(currPtr.p.y))                
            self.print_helper(currPtr.left, indent, False)
            self.print_helper(currPtr.right, indent, True)


