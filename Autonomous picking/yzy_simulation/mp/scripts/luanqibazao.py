#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2022/3/7 下午3:29
"""
# import networkx as nx
# from typing import Iterator
# import tf2_ros
# import rospy
#
# rospy.init_node("ss", anonymous=True)
# rospy.sleep(1)
# # g: nx.Graph = nx.grid_graph([3, 2, 2])
# # for rid in g.nodes:
# #     print(rid)
# #
# # print([n for n in g.neighbors((0, 0, 2))])
# # print(g.has_edge((0, 0, 0), (0, 0, 1)))
# #
# # print(iter(rid for rid in g.nodes))
#
# buffer = tf2_ros.Buffer()
# listener = tf2_ros.TransformListener(buffer)
# for _ in range(10):
#     try:
#         tf = buffer.lookup_transform("base_link", "link_1", rospy.Time(0))
#         print(tf)
#     except:
#         pass


import networkx as nx
import numpy as np
from mayavi import mlab

# some graphs to try
# H=nx.krackhardt_kite_graph()
# H=nx.Graph();H.add_edge('a','b');H.add_edge('a','c');H.add_edge('a','d')
# H=nx.grid_2d_graph(4,5)
H = nx.cycle_graph(20)

# reorder nodes from 0,len(G)-1
G = nx.convert_node_labels_to_integers(H)
# 3d spring layout
pos = nx.spring_layout(G, dim=3)
# numpy array of x,y,z positions in sorted node order
xyz = np.array([pos[v] for v in sorted(G)])
# scalar colors
scalars = np.array(list(G.nodes())) + 5

pts = mlab.points3d(
    xyz[:, 0],
    xyz[:, 1],
    xyz[:, 2],
    scalars,
    scale_factor=0.1,
    scale_mode="none",
    colormap="Blues",
    resolution=20,
)

pts.mlab_source.dataset.lines = np.array(list(G.edges()))
tube = mlab.pipeline.tube(pts, tube_radius=0.01)
mlab.pipeline.surface(tube, color=(0.8, 0.8, 0.8))
mlab.show()
