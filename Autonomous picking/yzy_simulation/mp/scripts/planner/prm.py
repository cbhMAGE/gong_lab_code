#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:yzy
@file:prm.py
@time:2022/01/25
"""
import logging

from .base import State, Space, Magic
from .tools import Timer
import numpy as np
import scipy.spatial
import time
import networkx as nx
from typing import List, Union


class PRM:
    def __init__(self, space_: Space):
        self.space = space_

        self.milestones = []
        self.sates = []
        self.roadmap = nx.Graph()

        self.sol_found = False
        self.start_state = None
        self.goal_state = None

        # 参数
        self.TIMEOUT = 30.0  # s
        self.ROADMAP_BUILD_TIME = 2.0  # s
        self.FIND_VALID_STATE_ATTEMPTS_WITHOUT_TERMINATION_CHECK = 2
        self.NEAREST_NEIGHBORS = 10

    def get_nearest_neighbors_count(self):
        return self.NEAREST_NEIGHBORS

    def get_neighbors(self, s_: State):
        kd_tree = scipy.spatial.KDTree(self.milestones)
        neighbors = kd_tree.query(s_.data_view, k=self.get_nearest_neighbors_count())
        num = len(self.milestones)
        return [self.sates[idx] for idx in neighbors[1] if idx < num]

    def add_milestone(self, s_: State):
        self.roadmap.add_node(s_)
        nbr_states = self.get_neighbors(s_)
        for nbr_state in nbr_states:
            if self.space.check_motion(nbr_state, s_):
                self.roadmap.add_edge(nbr_state, s_, w=1.0)
        self.milestones = np.vstack((self.milestones, s_.data_view))
        self.sates.append(s_)

    def grow_roadmap(self, time_):
        start_t = time.time()
        while time.time() - start_t < time_:
            states = self.space.sample_uniform(num=self.FIND_VALID_STATE_ATTEMPTS_WITHOUT_TERMINATION_CHECK)
            success = False
            for s in states:
                if self.space.check_validity(s):
                    self.add_milestone(s)
                    success = True
                    break
            if success and self.check_solution():
                self.sol_found = True
                break

    def expand_roadmap(self, time_):
        # todo
        pass

    def check_solution(self) -> bool:
        return nx.has_path(self.roadmap, self.start_state, self.goal_state)

    def construct_solution(self) -> List[State]:
        return nx.dijkstra_path(self.roadmap, self.start_state, self.goal_state, weight='w')

    def solve(self, start_state_: State, goal_state_: State) -> Union[List[State], None]:
        if not self.space.check_validity(start_state_) or not self.space.check_validity(goal_state_):
            logging.error("start or goal state is invalid")
            return None
        self.start_state = start_state_
        self.roadmap.add_node(start_state_)
        self.sates.append(start_state_)
        self.milestones = np.array([start_state_.data_view], dtype=Magic.DATA_TYPE)

        self.goal_state = goal_state_
        self.add_milestone(goal_state_)

        grow = True
        start_t = time.time()
        while not self.sol_found and time.time() - start_t < self.TIMEOUT:
            if grow:
                self.grow_roadmap(2.0 * self.ROADMAP_BUILD_TIME)
            else:
                self.expand_roadmap(self.ROADMAP_BUILD_TIME)
            grow = not grow
        print(f"PRM cost {time.time() - start_t:.3f} s, {len(self.sates):d} states")
        return self.construct_solution() if self.sol_found else None
