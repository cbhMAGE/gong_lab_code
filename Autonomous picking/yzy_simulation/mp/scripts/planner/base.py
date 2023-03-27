#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:yzy
@file:base.py
@time:2022/01/17
"""
import numpy as np
from typing import List, Tuple
import math


def wrap_to_pi(angle: float or List or np.ndarray):
    if isinstance(angle, float):
        return (angle + np.pi) % (2 * np.pi) - np.pi
    else:
        return [wrap_to_pi(a) for a in angle]


class Magic:
    DATA_TYPE = np.float64


class State:
    def __init__(self, data):
        self._data = np.array(data, dtype=Magic.DATA_TYPE)
        # self._rid = None

    @property
    def data(self):
        return self._data.copy()

    @property
    def data_view(self):
        return self._data

    def __hash__(self):
        return hash(''.join(map(str, self.data)))

    def expand(self, to_s: 'State', ratio=1.0) -> 'State':
        return State((to_s.data - self._data) * ratio + self._data)

    def to_list(self) -> List:
        return self._data.tolist()

    def __getitem__(self, item) -> Magic.DATA_TYPE:
        return self._data[item]

    def __str__(self):
        return f'{self.__class__}{str(self._data)}'

    def __repr__(self):
        return self.__str__()


class Space:
    def __init__(self, lower_bound, upper_bound, check_motion_resolution=0.05):
        self.dim = len(lower_bound)
        self._lower_bound = np.array(lower_bound, dtype=Magic.DATA_TYPE)
        self._upper_bound = np.array(upper_bound, dtype=Magic.DATA_TYPE)
        self._check_motion_resolution = check_motion_resolution

    def satisfied(self, s: State) -> bool:
        return np.all(self._lower_bound <= s.data < self._upper_bound)

    def sample_uniform(self, num=1) -> List[State]:
        return [State(_) for _ in np.random.uniform(self._lower_bound, self._upper_bound, size=(num, self.dim))]

    @property
    def lower_bound(self):
        return self._lower_bound.copy()

    @property
    def upper_bound(self):
        return self._upper_bound.copy()

    # def cut(self, region_id, slices):
    #     delta = (self._upper_bound - self._lower_bound) / slices
    #     lb = delta * region_id + self._lower_bound
    #     return Space(lb, lb + delta, )

    def check_validity(self, s: State) -> bool:
        raise NotImplementedError

    def check_motion(self, s1: State, s2: State) -> bool:
        count = math.ceil(self.distance(s1, s2) / self._check_motion_resolution)
        q = [(1, count)]
        while q:
            i1, i2 = q.pop(0)
            mid = (i1 + i2) // 2
            if not self.check_validity(s1.expand(s2, mid / count)):
                return False
            if i1 < mid:
                q.append((i1, mid - 1))
            if i2 > mid:
                q.append((mid + 1, i2))
        return True

    @staticmethod
    def distance(s1: 'State', s2: 'State') -> float:
        return np.linalg.norm(s1.data_view - s2.data_view)


if __name__ == '__main__':
    pass
    print(np.rad2deg(wrap_to_pi(np.pi * 3 + np.pi / 3)))
    # s1 = State([1.1, 2, 3])
    # s2 = State(s1.data_view)
    # print(hash(s1) == hash(s2))
