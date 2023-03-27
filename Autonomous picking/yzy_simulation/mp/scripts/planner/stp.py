#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: zhiyu YANG
@Email: ZhiyuYANG96@outlook.com
@Date: 2022-02-24 18:02:09
"""
from .base import State, Space, Magic
import networkx as nx
from typing import List, Union, Tuple, Iterable, Iterator
import logging
import numpy as np
import scipy.spatial
import time


class Cell:
    def __init__(self, rid_: Tuple, space_: Space):
        self.start_set: List[State] = []
        self.goal_set: List[State] = []
        self.space = space_
        self.rid: Tuple = rid_
        self.all_states: List[State] = []

    @property
    def is_connected_to_start(self) -> bool:
        return len(self.start_set) > 0

    @property
    def is_connected_to_goal(self) -> bool:
        return len(self.goal_set) > 0

    def sample_start_set(self) -> Union[State, None]:
        if not self.start_set:
            return None
        return self.start_set[np.random.randint(0, len(self.start_set))]

    def sample_goal_set(self) -> Union[State, None]:
        if not self.goal_set:
            return None
        return self.goal_set[np.random.randint(0, len(self.goal_set))]

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

        # build graph data structure
        self.g: nx.Graph = nx.grid_graph(self.slices)  # 用来计算 lead
        self.cell_g: nx.Graph = nx.grid_graph(self.slices)  # 用来维护 cell 之间的连接关系
        self.cell_g.clear_edges()
        self.cells = {}
        for rid in self.g.nodes:
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

    def compute_lead(self, start_cell: Cell, goal_cell: Cell) -> List[Cell]:
        lead = nx.dijkstra_path(self.g, start_cell.rid, goal_cell.rid, weight='w')
        return [self.get_cell(rid) for rid in lead]

    def get_cell(self, rid: Tuple) -> Cell:
        return self.cells[rid]

    # 仅采样, 不保证无碰撞
    def _sample_in_cell(self, cell: Cell, seed=None) -> Union[State, None]:
        raise NotImplementedError

    def sample_in_cell(self, cell: Cell) -> Union[State, None]:
        nbr_cells = [cell, *(self.cells[rid] for rid in self.cell_g.neighbors(cell.rid))]
        np.random.shuffle(nbr_cells)
        seed = None
        for _cell in nbr_cells:
            seed = _cell.sample_start_set()
            if seed:
                break
        if seed:
            return self._sample_in_cell(cell, seed=seed)
        else:
            return self._sample_in_cell(cell, seed=None)

    def publish_cells(self, cells: Iterable[Cell], rgba: Tuple):
        raise NotImplementedError

    def is_cell_connected(self, cell_a: Cell, cell_b: Cell) -> bool:
        return self.cell_g.has_edge(cell_a.rid, cell_b.rid)

    def add_cell_edge(self, cell_a: Cell, cell_b: Cell):
        self.cell_g.add_edge(cell_a.rid, cell_b.rid)


class STP:
    def __init__(self, space_: Space, decomposition_: Decomposition):
        self.space = space_
        self.decomposition = decomposition_

        # self.milestones = []
        # self.sates = []
        self.g = nx.Graph()

        self.sol_found = False
        self.start_state = None
        self.goal_state = None

        # 参数
        self.TIMEOUT = 30.0  # s
        # self.ROADMAP_BUILD_TIME = 2.0  # s
        # self.FIND_VALID_STATE_ATTEMPTS_WITHOUT_TERMINATION_CHECK = 2
        # self.NEAREST_NEIGHBORS = 10

    def construct_solution(self) -> List[State]:
        return nx.dijkstra_path(self.g, self.start_state, self.goal_state, weight='w')

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
        start_cell.start_set.append(self.start_state)

        goal_cell = self.decomposition.project(self.goal_state)
        goal_cell.goal_set.append(self.goal_state)
        print("goal_cell", goal_cell)
        cnt = 0
        while not self.sol_found and time.time() - start_time < self.TIMEOUT:
            # 1. 计算 lead
            lead = self.decomposition.compute_lead(start_cell, goal_cell)
            print("lead: ", lead)
            self.decomposition.publish_cells(lead, rgba=(0.9, 0, 0, 0.8))
            # 2. 在 lead 中搜索
            self.search_in_lead(lead)
            # 3. 下一个循环
            cnt += 1
            print(f"loop {cnt:d}")

        print(f"STP cost {time.time() - start_time:.3f} s, xxx states")
        return self.construct_solution() if self.sol_found else None

    def search_in_lead(self, lead: List[Cell]):
        start_cell = lead[0]
        goal_cell = lead[-1]

        # 1. 尝试前后连接lead中的cell
        lead_len = len(lead)
        connect_cell_attempts = 5  # TODO: param
        if lead_len > 1:
            for i in range(1, lead_len):
                prev_cell = lead[i - 1]
                cur_cell = lead[i]
                print(f"check: {str(cur_cell)}")
                if cur_cell.is_connected_to_start:
                    # TODO: 按照采样和连通性密度计算 p
                    p = 0.6
                    if np.random.random() < p:
                        for _ in range(3):
                            prev_s = prev_cell.sample_start_set()
                            assert prev_s is not None
                            new_s = self.decomposition.sample_in_cell(cur_cell)
                            if not new_s:
                                continue
                            if self.space.check_motion(prev_s, new_s):
                                self.g.add_node(new_s)
                                self.g.add_edge(prev_s, new_s, w=self.space.distance(prev_s, new_s))
                                cur_cell.start_set.append(new_s)
                else:
                    print(f"connect: {str(prev_cell)} -> {str(cur_cell)}")
                    # 连接前后两个cell, 尝试几次
                    for _ in range(connect_cell_attempts):
                        prev_s = prev_cell.sample_start_set()
                        assert prev_s is not None
                        # TODO: 不能重复
                        new_s = cur_cell.sample_goal_set()
                        try_goal = True
                        if not new_s:
                            new_s = self.decomposition.sample_in_cell(cur_cell)
                            try_goal = False
                        if not new_s:
                            continue
                        if self.space.check_motion(prev_s, new_s):
                            if try_goal:
                                self.g.add_edge(prev_s, new_s, w=self.space.distance(prev_s, new_s))
                                self.sol_found = True
                                return
                            else:
                                self.g.add_node(new_s)
                                self.g.add_edge(prev_s, new_s, w=self.space.distance(prev_s, new_s))
                            cur_cell.start_set.append(new_s)
                            self.decomposition.add_cell_edge(prev_cell, cur_cell)
                            break
                    print("connect result:", cur_cell.is_connected_to_start)
                if not cur_cell.is_connected_to_start:
                    print("find", Cell, "connect failed")
                    break
        # 2. 如果都连上了的话
        if goal_cell.is_connected_to_start:
            for _gs in goal_cell.goal_set:
                for _ss in goal_cell.start_set:
                    if self.space.check_motion(_gs, _ss):
                        self.g.add_edge(_gs, _ss)
                        self.sol_found = True
                        return


if __name__ == '__main__':
    # c = Coord([1, 1, 1])
    # print(c)
    # space = Space([0, 0, 0], [1, 2, 3])
    # Decomposition(space, (3, 3, 3))
    pass
