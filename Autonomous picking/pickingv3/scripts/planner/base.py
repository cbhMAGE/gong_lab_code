#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:yzy
@file:base.py
@time:2022/01/17
"""
import numpy as np
from typing import List, Tuple


class State:
    DTYPE = np.float64

    def __init__(self, data):
        self._data = np.array(data, dtype=Space.DTYPE)
        self._rid = None

    @property
    def data(self):
        return self._data.copy()

    @property
    def rid(self) -> Tuple:
        return self._rid

    def __hash__(self):
        return hash(str(self.data))

    def dis_to(self, other: 'State') -> float:
        return np.linalg.norm(self._data - other.data)

    def expand(self, to_s: 'State', ratio=1.0) -> 'State':
        return State((to_s.data - self._data) * ratio + self._data)


class Space:
    DTYPE = np.float64

    def __init__(self, lower_bound, upper_bound):
        self.dim = len(lower_bound)
        self._lower_bound = np.array(lower_bound, dtype=Space.DTYPE)
        self._upper_bound = np.array(upper_bound, dtype=Space.DTYPE)

    def satisfied(self, s: State) -> bool:
        return np.all(self._lower_bound <= s.data < self._upper_bound)

    def sample_uniform(self, num=1) -> List[State]:
        return [State(_) for _ in np.random.uniform(self._lower_bound, self._upper_bound, size=(self.dim, num))]

    @property
    def lower_bound(self):
        return self._lower_bound.copy()

    @property
    def upper_bound(self):
        return self._upper_bound.copy()

    def cut(self, region_id, slices):
        delta = (self._upper_bound - self._lower_bound) / slices
        lb = delta * region_id + self._lower_bound
        return Space(lb, lb + delta, )


class SE:
    def __init__(self, _pt, _sox):
        self._pt = _pt
        self._sox = _sox

    @property
    def point(self):
        return self._pt
    
    @property
    def rotation(self):
        return self._sox
