#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/11/9 下午3:31
"""
from base.config import JointLimitsTool

if __name__ == '__main__':
    jl = JointLimitsTool()
    jl.overwrite()
    jl.print_current_config()
