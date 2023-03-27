#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:yzy
@file:workspace.py
@time:2022/01/17
"""
from typing import Tuple
from base import State, SE, Space
import numpy as np


class PlanarWorkspace:
    def __init__(self, upper_bound, lower_bound, slices: Tuple):
        self.space = Space(lower_bound, upper_bound)
        self.dim = 2
        self.slices = slices
        self.free_vols = np.ones(slices, dtype=np.float64)

    def project_to_region(self, s: State) -> Tuple:
        pt = self.fk(s).point
        coord = []
        for idx, val in enumerate(pt):
            coord.append(int(val // self.slices[idx]))
        return tuple(coord)

    @staticmethod
    def fk(s: State) -> SE:
        pass

    @staticmethod
    def ik(s: SE) -> State:
        pass

    def get_freevol(self, rid: Tuple) -> float:
        return self.free_vols[rid]

    @staticmethod
    def sample_rotation():
        return np.random.random()

    def sample_from_region(self, rid) -> State:
        s = self.space.cut(rid, self.slices).sample_uniform(num=1)[0]
        return self.ik(SE(s, self.sample_rotation()))


class SE3Workspace(PlanarWorkspace):

    @staticmethod
    def sample_rotation():
        u1, u2, u3 = np.random.uniform([0, 0, 0], [1, np.pi * 2, np.pi * 2])
        a = np.sqrt(1 - u1)
        b = np.sqrt(u1)
        return a * np.sin(u2), a * np.cos(u2), b * np.sin(u3), b * np.cos(u3)
