#! /usr/bin/env python
#-*- coding: utf-8 -*-

# A binary ordered tree example

class CNode(object):
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

class CBOrdTree(object):
    """
    Represents a binary ordered tree.
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
        return CNode(data)

    def insert(self, root, data):
        """
        Inserts a new data.
        """
        if root == None:
            # it there isn't any data
            # adds it and returns
            return self.addNode(data)
        else:
            # enters into the tree
            if data['article_date'] <= root.data['article_date']:
                # if the data is less than the stored one
                # goes into the left-sub-tree
                root.left = self.insert(root.left, data)
            else:
                # processes the right-sub-tree
                root.right = self.insert(root.right, data)
            return root

    def lookup(self, root, target):
        """
        Looks for a value into the tree.
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

    def printTree(self, root):
        """
        Prints the tree path.
        """
        if root == None:
            pass
        else:
            self.printTree(root.left)
            print(root.data, end=' ')
            self.printTree(root.right)

    def printRevTree(self, root):
        """
        Prints the tree path in reverse order.
        """
        if root == None:
            pass
        else:
            self.printRevTree(root.right)
            print(root.data, end=' ')
            self.printRevTree(root.left)

if __name__ == "__main__":
    # Point of entry in execution mode.
    # create the binary tree
    BTree = CBOrdTree()
    # add the root node
    root = BTree.addNode(0)
    # ask the user to insert values
    for i in range(0, 5):
        data = int(input("insert the node value nr %d: " % i))
        # insert values
        BTree.insert(root, data)

    BTree.printTree(root)
    print()
    BTree.printRevTree(root)
    print()
    data = int(input("Insert a value to find: "))
    if BTree.lookup(root, data):
        print("found")
    else:
        print("not found")

    print(BTree.minValue(root))
    print(BTree.maxDepth(root))
    print(BTree.size(root))
