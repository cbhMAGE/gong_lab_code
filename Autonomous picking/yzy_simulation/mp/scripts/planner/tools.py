#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:yzy
@file:tools.py
@time:2022/02/03
"""
import time


class Timer:
    def __init__(self, name=""):
        self.name = name
        self.t = time.time()

    def __del__(self):
        print(f"[{self.name}] cost {(time.time() - self.t) * 1000.0:.3f} ms")
