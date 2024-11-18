
from DataType import Point, Node, Event, Arc

import sys, math

class AVLTree(object):
    def __init__(self):
        self.node = None
        self.basen = None
        self.nodea = None
        self.nodeb = None
        self.pp = None
        self.pn = None
        
    # get the representative point on this arc
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

        return

    def intersection(self, p0, p1, X):
        # get the intersection of two parabolas
        p = p0
        if (p0.x == p1.x):
            py = (p0.y + p1.y) / 2.0
        elif (p1.x == X):
            py = p1.y
        elif (p0.x == X):
            py = p0.y
            p = p1
        else:
            # use quadratic formula
            z0 = 2.0 * (p0.x - X)
            z1 = 2.0 * (p1.x - X)

            a = 1.0/z0 - 1.0/z1;
            b = -2.0 * (p0.y/z0 - p1.y/z1)
            c = 1.0 * (p0.y**2 + p0.x**2 - X**2) / z0 - 1.0 * (p1.y**2 + p1.x**2 - X**2) / z1

            py = 1.0 * (-b-math.sqrt(b*b - 4*a*c)) / (2*a)
            
        px = 1.0 * (p.x**2 + (p.y-py)**2 - X**2) / (2*p.x-2*X)
        res = Point(px, py)
        return res
    
    # Function to insert a node # p is the point to insert, it's on arc a
    def insert_node(self, root, p):
 
        # Find the correct location and insert the node
        if not root:
            return root

        self.chkpt(root,p)
        
        if (self.pp is not None and p.y < self.pp.y) \
            and (root.left is not None):
            
            root.left = self.insert_node(root.left, p)

        elif root.right is not None and (root.arc.p.x == p.x and root.arc.p.y != p.y or \
            not ( (self.pp is None and self.pn is None) \
            or (self.pp is not None and self.pn is not None and self.pn.y == self.pp.y)\
            or (self.pn is None and self.pp is not None and p.y > self.pp.y) \
            or (self.pp is None and self.pn is not None and p.y < self.pn.y) \
            or (self.pn is not None and self.pp is not None and \
                 p.y < self.pn.y and self.pp.y < p.y))): \
              root.right = self.insert_node(root.right, p)
                
        else:
            self.basen = root
                
            if  root.right is None:
                n = Node(p)
                if self.nodea is None:
                    self.nodea = n
                else:
                    self.nodeb = n                
                root.right = n

            else:
                temp = self.getMinValueNode(root.right)
                n = Node(p)
                if self.nodea is None:
                    self.nodea = n
                else:
                    self.nodeb = n                
                temp.left = n
       
            # Update the balance factor and balance the tree
            root.height = 1 + max(self.getHeight(root.left),
                              self.getHeight(root.right))

        # Update the balance factor and balance the tree
        root.height = 1 + max(self.getHeight(root.left),
                             self.getHeight(root.right))
        balanceFactor = self.getBalance(root)
        
            # Balance the tree
        if balanceFactor > 1:
            if self.getBalance(root.left) >= 0:
                return self.rightRotate(root)
            else:
                root.left = self.leftRotate(root.left)
                return self.rightRotate(root)
        if balanceFactor < -1:
            if self.getBalance(root.right) <= 0:
                return self.leftRotate(root)
            else:
                root.right = self.rightRotate(root.right)
                return self.leftRotate(root)

        return root

    # Function to delete a node
    # e.a is the arc to be removed
    # Point(e.x,e.p.y) is the high point of the arc
    def delete_node(self, root, e):

        # Find the node to be deleted and remove it
        if root is not None:
            p = Point(e.x,e.p.y)
            self.chkpt(root,p)
        
        if not root:
            return root

        # get the fore and aft for the current arc
            # p is the high point of the circle
       
        elif root.arc.aprev is not None and \
                (root.arc.number != e.a.number) and (p.y <= self.pp.y) \
                 or root.arc.aprev.number == e.a.number:
                root.left = self.delete_node(root.left, e)                
            
        elif root.arc.number != e.a.number:
                root.right = self.delete_node(root.right, e)
                
        else:
             # Found the arc

            if root.left is None:
                temp = root.right
                root = None
                return temp
            elif root.right is None:
                temp = root.left
                root = None
                return temp
            
            temp = self.getMinValueNode(root.right)
            
            root.p = temp.p
            root.arc = temp.arc
            
            p = Point(e.x,e.p.y)
            self.chkpt(temp,p)
            if self.pn is None:
                self.pn = self.pp
                self.pn.y = 2*self.pn.y
            ty = 0.5*(self.pp.y + self.pn.y)
            et = Event(e.x, Point(0,0),temp.arc)
            
            root.right = self.delete_node(root.right, et)
        
            # Update the balance factor of nodes
            root.height = 1 + max(self.getHeight(root.left),
                              self.getHeight(root.right))

            
        return root

    # Function to perform left rotation
    def leftRotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self.getHeight(z.left),
                           self.getHeight(z.right))
        y.height = 1 + max(self.getHeight(y.left),
                           self.getHeight(y.right))
        return y

    # Function to perform right rotation
    def rightRotate(self, z):
        y = z.left
        if y != None: T3 = y.right
        else: T3 = None
        y.right = z
        z.left = T3
        z.height = 1 + max(self.getHeight(z.left),
                           self.getHeight(z.right))
        y.height = 1 + max(self.getHeight(y.left),
                           self.getHeight(y.right))
        return y

    # Get the height of the node
    def getHeight(self, root):
        if not root:
            return 0
        return root.height

    # Get balance factor of the node
    def getBalance(self, root):
        if not root:
            return 0
        return self.getHeight(root.left) - self.getHeight(root.right)

    def getMinValueNode(self, root):       
        if root is None or root.left is None:
            return root      
        return self.getMinValueNode(root.left)
