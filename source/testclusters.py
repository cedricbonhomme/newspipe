#! /usr/bin/env python
#-*- coding: utf-8 -*-

import clusters

K = 7

blognames,words,data = clusters.readfile("blogdata1.txt")

coords = clusters.scaledown(data)

print "Generating clusters..."
kclust = clusters.kcluster(data, k=K, distance=clusters.pearson)
print
print "Clusters:"
for i in range(K):
    print "Cluster" + str(i)
    print ", ".join([blognames[r] for r in kclust[i]])
    print




clusters.draw2d(coords,blognames,jpeg='mds2d.jpg')
