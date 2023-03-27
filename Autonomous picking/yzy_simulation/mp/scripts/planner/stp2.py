#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2022/4/10 下午12:54
"""

import numpy as np
from .base import State, Space
import networkx as nx
from typing import Tuple, List, Union, Iterable, Dict
import collections
import heapq
import logging
import time


class Cell:
    def __init__(self, rid_: Tuple, space_: Space):
        self.space = space_
        self.rid: Tuple = rid_
        #
        # self.all_states: List[State] = []
        # self.start_set: List[State] = []
        # self.goal_set: List[State] = []
        self.w: float = 1.0
        self.obs_w: float = 0.0

    def __str__(self):
        return f'Cell{str(self.rid)}'

    def __repr__(self):
        return self.__str__()


class Decomposition:
    def __init__(self, workspace_: Space, slices_: Tuple):
        self.workspace = workspace_
        self.slices = slices_
        assert len(self.slices) == self.workspace.dim
        self.interval: np.ndarray = (self.workspace.upper_bound - self.workspace.lower_bound) / self.slices
        #
        self.cell_grid: nx.Graph = nx.grid_graph(self.slices)  # 用来计算 lead
        self.cells: Dict[Tuple, Cell] = {}
        for rid in self.cell_grid.nodes:
            self.cells[rid] = Cell(rid, Space(
                self.workspace.lower_bound + self.interval * rid,
                self.workspace.lower_bound + self.interval * tuple(map(lambda x: x + 1, rid))
            ))

    def fk(self, s: State) -> State:
        raise NotImplementedError

    def project(self, s: State) -> Cell:
        coord = self.fk(s)
        rid = (coord.data_view[:self.workspace.dim] - self.workspace.lower_bound) / self.interval
        rid = tuple(map(int, rid))
        return self.get_cell(rid)

    def get_cell(self, rid: Tuple) -> Cell:
        return self.cells[rid]

    def compute_lead(self, start_cell: Cell, goal_cell: Cell):
        q = [(0.0, start_cell.rid, ())]
        dis = {}
        while q:
            cur_w, u, route = heapq.heappop(q)
            if u in dis:
                continue
            route = (*route, u)
            dis[u] = route
            if u == goal_cell.rid:
                return [self.cells[rid] for rid in route]
            for nbr_rid in self.cell_grid.neighbors(u):
                if nbr_rid in dis:
                    continue
                extra_factor = 1 / np.sqrt(2)
                if len(route) > 2:
                    tmp = 0
                    for j in range(self.workspace.dim):
                        if route[-2][j] == route[-1][j] == nbr_rid[j]:
                            tmp += 1
                    if tmp == self.workspace.dim - 1:
                        extra_factor = 1.0
                heapq.heappush(q, (cur_w + self.cells[route[-1]].w * extra_factor, nbr_rid, route))
        raise RuntimeError

    def publish_cells(self, cells: Iterable[Cell], rgba: Tuple):
        raise NotImplementedError


class STP2:
    def __init__(self, space_: Space, decomposition_: Decomposition):
        self.space = space_
        self.decomposition = decomposition_

        self.g = nx.Graph()

        self.sol_found = False
        self.start_state = None
        self.goal_state = None

    def solve(self, start_state_: State, goal_state_: State) -> Union[List[State], None]:
        # 0.0 记录开始时间
        start_time = time.time()

        # 0.1 检查 start_state 和 goal_state
        if not self.space.check_validity(start_state_) or not self.space.check_validity(goal_state_):
            logging.error("start or goal state is invalid")
            return None

        self.start_state = start_state_
        self.goal_state = goal_state_
        self.g.add_node(self.start_state)
        self.g.add_node(self.goal_state)

        start_cell = self.decomposition.project(self.start_state)
        # start_cell.start_set.append(self.start_state)

        goal_cell = self.decomposition.project(self.goal_state)
        # goal_cell.goal_set.append(self.goal_state)

        lead = self.decomposition.compute_lead(start_cell, goal_cell)
        print("lead: ", lead)
        self.decomposition.publish_cells(lead, rgba=(0.9, 0, 0, 0.8))
