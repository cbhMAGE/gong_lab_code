#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:yzy
@file:stp.py
@time:2022/01/03
spatial-temporal planner
"""
from base import State, Space, SE
import networkx as nx
import numpy as np
from typing import Tuple, List, Callable
import collections
import rospy
from workspace import PlanarWorkspace, SE3Workspace
from scipy.spatial import KDTree
from copy import deepcopy
import math


class STP:
    def __init__(self):
        self.ws = SE3Workspace([-1, -1, -1], [1, 1, 1], (5, 5))
        # weight graph
        self.wg: nx.Graph = nx.grid_graph(dim=self.ws.slices)

        self.state_validity_fn: Callable[['State'], bool] = lambda _: True
        self.road_map = nx.Graph()
        self.road_map_pts = np.array([], dtype=np.float64)

        self.sel = collections.defaultdict(int)

        # params
        self.max_iter = 30
        self.check_motion_resolution = 0.05

        self.history = []

    def compute_lead(self, from_rid: Tuple, to_rid: Tuple) -> List[Tuple]:
        return nx.shortest_path(self.wg, from_rid, to_rid, weight='w')

    def random_dfs(self, from_rid: Tuple, to_rid: Tuple) -> List[Tuple]:
        def dfs(_from_rid: Tuple, route: List):
            nbrs = [n for n in self.wg.neighbors(from_rid)]
            np.random.shuffle(nbrs)
            nxt = nbrs[0]
            if to_rid in nbrs:
                return route
            route.append(_from_rid)
            dfs(nxt, route)

        r = []
        dfs(from_rid, r)
        return r

    def sample_along_lead(self, lead: List[Tuple]) -> List[State]:
        ss = []
        for rid in lead:
            s = self.ws.sample_from_region(rid)
            if self.state_validity_fn(s):
                ss.append(s)
                self.road_map.add_node(s)
        self.road_map_pts = np.vstack(self.road_map_pts, ss)
        return ss

    def connect_regions(self, new_states: List[State]):
        kd_tree = KDTree(self.road_map_pts)
        for s in new_states:
            dists, idxes = kd_tree.query(s.data, k=10)
            for idx in idxes:
                if self.check_motion(s, self.road_map_pts[idx]):
                    self.road_map.add_edge(s, self.road_map.nodes[idx])

    def check_solution_path(self, from_s, to_s):
        return nx.dijkstra_path(self.road_map, from_s, to_s)

    def update_weight(self):
        vv = collections.defaultdict(int)
        ee = collections.defaultdict(int)
        for n in self.road_map.nodes:
            n: State = n
            vv[n.rid] += 1
            if len(self.road_map.neighbors(n)) > 0:
                ee[n.rid] += 1
        alpha = -1
        beta = -10
        gamma = -1
        phi = 1
        for e in self.wg.edges:
            _, v = e
            if vv[v] == 0:
                self.wg.edges[e]['w'] = 1 / (phi * self.ws.get_freevol(v) ** 2)
            else:
                self.wg.edges[e]['w'] = \
                    np.exp(beta * ee[v] / vv[v]) * \
                    np.exp(alpha * vv[v] / len(self.road_map.nodes)) * \
                    (1 - np.exp(gamma * self.sel[v])) / \
                    (phi * self.ws.get_freevol(v) ** 2)

    def check_motion(self, from_s: State, to_s: State) -> bool:
        count = math.ceil(from_s.dis_to(to_s) / self.check_motion_resolution)
        q = [(1, count)]
        while q:
            i1, i2 = q.pop(0)
            mid = (i1 + i2) // 2
            if not self.state_validity_fn(from_s.expand(to_s, mid / count)):
                return False
            if i1 < mid:
                q.append((i1, mid - 1))
            if i2 > mid:
                q.append((mid + 1, i2))
        return True

    def calc_cur_scene_feature(self):
        free_vols = self.ws.free_vols.copy()
        x, y, z = free_vols.shape
        k = np.zeros((x // 2, y // 2, z // 2), dtype=np.float64)
        # max-pooling
        for _x in range(0, x, 2):
            for _y in range(0, y, 2):
                for _z in range(0, z, 2):
                    k[_x // 2, _y // 2, _z //
                        2] = np.max(free_vols[_x:_x + 2, _y:_y + 2, _z:_z + 2])
        return k.reshape(-1)

    def save_history(self):
        self.history.append([self.calc_cur_scene_feature(),
                             self.road_map.copy(), self.road_map_pts.copy()])

    def load_history(self):
        cur_k = self.calc_cur_scene_feature()
        if len(self.history) > 0:
            self.history.sort(key=lambda _k: np.abs(cur_k - _k))
            scene = self.history[0]
            k = scene[0]
            if sum(np.abs(cur_k - k)) / len(k) < 0.3:
                self.road_map:nx.Graph = scene[1]
                self.road_map_pts = scene[2]
                self.road_map.clear_edges()
                self.connect_regions()
                return
        self.road_map = nx.Graph()
        self.road_map_pts = np.array([], dtype=np.float64)

    def solve(self, start: State, goal: Space):
        self.load_history()

        start_rid = self.ws.project_to_region(start)
        goal_rid = self.ws.project_to_region(goal.sample_uniform(1)[0])
        goal_state = goal.sample_uniform(num=1)[0]
        self.road_map.add_node(start)
        self.road_map.add_node(goal)
        traj = None
        self.update_weight()
        for _ in range(self.max_iter):
            # compute lead
            if np.random.random() < 0.95:
                lead = self.compute_lead(start_rid, goal_rid)
            else:
                lead = self.random_dfs(start_rid, goal_rid)

            # update sel
            for rid in lead:
                self.sel[rid] += 1

            # prm plan
            for _ in range(3):
                new_states = self.sample_along_lead(lead)
                self.connect_regions(new_states)
                traj = self.check_solution_path(start, goal_state)
                if traj:
                    break
            # next
            self.update_weight()

        if traj:
            self.save_history()


def main():
    rospy.init_node("stp", anonymous=True)
    stp = STP()
    start = State(np.deg2rad([120, -40, 70, 16, 30, 0]))
    goal_state = np.deg2rad([90, -90, 120, 10, 40, 0])
    goal = Space(
        goal_state - np.deg2rad([3 for _ in range(6)]),
        goal_state + np.deg2rad([3 for _ in range(6)])
    )
    traj = stp.solve(start, goal)
    print(traj)


if __name__ == '__main__':
    main()
