#! /usr/bin/env python
#-*- coding: utf-8 -*-

# A binary ordered  example

class Node(object):
    """
    Represents a node.
    """
    def __init__(self, data):
        """
        Initialization.
        """
        self.left = None
        self.right = None
        self.data = data

class OrderedBinaryTree(object):
    """
    Represents a binary ordered .
    """
    def __init__(self):
        """
        Initializes the root member.
        """
        self.root = None

    def addNode(self, data):
        """
        Creates a new node and returns it.
        """
        return Node(data)

    def insert(self, root, data):
        """
        Inserts a new data.
        """
        if root == None:
            # it there isn't any data
            # adds it and returns
            return self.addNode(data)
        else:
            # enters into the
            if data['article_date'] <= root.data['article_date']:
                # if the data is less than the stored one
                # goes into the left-sub-
                root.left = self.insert(root.left, data)
            else:
                # processes the right-sub-
                root.right = self.insert(root.right, data)
            return root

    def lookup(self, root, target):
        """
        Looks for a value into the .
        """
        if root == None:
            return 0
        else:
            # if it has found it...
            if target == root.data:
                return 1
            else:
                if target['article_date'] < root.data['article_date']:
                    # left side
                    return self.lookup(root.left, target)
                else:
                    # right side
                    return self.lookup(root.right, target)

    def minValue(self, root):
        """
        Goes down into the left
        arm and returns the last value.
        """
        while(root.left != None):
            root = root.left
        return root.data

    def maxValue(self, root):
        """
        Goes down into the right
        arm and returns the last value.
        """
        while(root.right != None):
            root = root.right
        return root.data

    def maxDepth(self, root):
        """
        Return the maximum depth.
        """
        if root == None:
            return 0
        else:
            # computes the two depths
            ldepth = self.maxDepth(root.left)
            rdepth = self.maxDepth(root.right)
            # returns the appropriate depth
            return max(ldepth, rdepth) + 1

    def size(self, root):
        if root == None:
            return 0
        else:
            return self.size(root.left) + 1 + self.size(root.right)

    def pre_order_traversal(self, root, result=[]):
        """
        Depth-first. Pre-order traversal.
        """
        if root == None:
            pass
        else:
            result.append(root.data)
            self.in_order_traversal(root.left, result)
            self.in_order_traversal(root.right, result)
        return result

    def in_order_traversal(self, root, result=[]):
        """
        Depth-first. In-order traversal.
        """
        if root == None:
            pass
        else:
            self.in_order_traversal(root.left, result)
            result.append(root.data)
            self.in_order_traversal(root.right, result)
        return result

    def post_order_traversal(self, root, result=[]):
        """
        Depth-first. Post-order traversal.
        """
        if root == None:
            pass
        else:
            self.in_order_traversal(root.left, result)
            self.in_order_traversal(root.right, result)
            result.append(root.data)
        return result

    def __str__(self):
        """
        Pretty display.
        """
        return ", ".join([article["article_title"] for article in self.in_order_traversal(self.root)])

if __name__ == "__main__":
    # Point of entry in execution mode.
    # create the tree
    tree = OrderedBinaryTree()
    # add the root node
    root = tree.addNode(0)
    # ask the user to insert values
    for i in range(0, 5):
        data = int(input("insert the node value nr %d: " % i))
        # insert values
        tree.insert(root, data)

    tree.printTree(root)
    print()
    tree.printRevTree(root)
    print()
    data = int(input("Insert a value to find: "))
    if tree.lookup(root, data):
        print("found")
    else:
        print("not found")

    print(tree.minValue(root))
    print(tree.maxDepth(root))
    print(tree.size(root))
