class AVLNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1  # Height of node starts at 1 for new leaf nodes

class AVLTree:
    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

    def right_rotate(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = max(self.get_height(y.left), self.get_height(y.right)) + 1
        x.height = max(self.get_height(x.left), self.get_height(x.right)) + 1
        return x

    def left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = max(self.get_height(x.left), self.get_height(x.right)) + 1
        y.height = max(self.get_height(y.left), self.get_height(y.right)) + 1
        return y

    def insert(self, root, key):
        if not root:
            return AVLNode(key)
        elif key < root.key:
            root.left = self.insert(root.left, key)
        else:
            root.right = self.insert(root.right, key)

        root.height = max(self.get_height(root.left), self.get_height(root.right)) + 1
        balance = self.get_balance(root)

        # Left Left Case
        if balance > 1 and key < root.left.key:
            return self.right_rotate(root)
        # Right Right Case
        if balance < -1 and key > root.right.key:
            return self.left_rotate(root)
        # Left Right Case
        if balance > 1 and key > root.left.key:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        # Right Left Case
        if balance < -1 and key < root.right.key:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def min_value_node(self, node):
        if node is None or node.left is None:
            return node
        return self.min_value_node(node.left)

    def delete(self, root, key):
        if not root:
            return root
        elif key < root.key:
            root.left = self.delete(root.left, key)
        elif key > root.key:
            root.right = self.delete(root.right, key)
        else:
            if root.left is None:
                temp = root.right
                root = None
                return temp
            elif root.right is None:
                temp = root.left
                root = None
                return temp

            temp = self.min_value_node(root.right)
            root.key = temp.key
            root.right = self.delete(root.right, temp.key)

        if root is None:
            return root

        root.height = max(self.get_height(root.left), self.get_height(root.right)) + 1
        balance = self.get_balance(root)

        # Balance the tree after deletion
        if balance > 1 and self.get_balance(root.left) >= 0:
            return self.right_rotate(root)
        if balance > 1 and self.get_balance(root.left) < 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and self.get_balance(root.right) <= 0:
            return self.left_rotate(root)
        if balance < -1 and self.get_balance(root.right) > 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def pre_order(self, root):
        if root:
            print(f"{root.key} ", end="")
            self.pre_order(root.left)
            self.pre_order(root.right)


# Example usage
avl_tree = AVLTree()
root = None
keys = [10, 85, 15, 70, 20, 60, 30]

for key in keys:
    root = avl_tree.insert(root, key)

print("Preorder traversal of the constructed AVL tree is:")
avl_tree.pre_order(root)
print()

# Delete a key and show the result
key_to_delete = 15
root = avl_tree.delete(root, key_to_delete)
key_to_delete = 10
root = avl_tree.delete(root, key_to_delete)
print(f"Preorder traversal after deletion of {key_to_delete}:")
avl_tree.pre_order(root)
print()
