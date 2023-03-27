# STP

## 伪代码

```python
def solve():
    while not sol_found or not will_terminate:
        search_path()

def search_path():
    # 1. 计算lead
    p = 0.95
    if rng < p:
        lead = shotest_path()
    else:
        lead = random_walk()
    
    # 2. 在每个cell中采样
    max_states = max(cell.states for cell in lead)
    for cell in lead:
        # 设置概率，减少对已经密集采样过的cell的重复采样
    	p = 1 - (cell.states / max_states)
        if rng < p:
            for _ in range(10):
                nbrs = [cell, *cell.nbrs]  # 取出cell及其邻接cell
                nbrs = shuffle([cell, *cell.nbrs])  # 打乱顺序
                seed = nbrs里随机挑一个cell，在cell里随机挑一个state
                # 根据seed，在cell中进行随机采样、计算ik，然后加入cell.states里
     
     # 3. 尝试cell与cell间的连接，使得每个cell能与两端的cell连通
    while num_connected_cell < len(lead):  # 若还存在cell不与两端cell连通
		for i in range(1, len(lead)):
            r1 = lead[i]
            r2 = lead[i-1]
            if r1和r2都至少与lead的一端连通:
                p = 1 - len(cell.states_in_tree) / len(cell.states)
                if rng < p:
                    将r1和r2中的state两两连接起来（On^2, check_motion）
                    check_motion后，如果跨cell的话，需要在经过的cell中落state
            else:
                从连通cell里随机选择一个intree的state,朝不连通的cell里随机采样的一个state进行check_motion以扩张
                扩张失败即退出while,然后重新进行第1步
    # 有0.05的概率强制把所有cell挨个前后连接一下(On^2遍历连接state)
    
    # 如果第3步中，所有cell都至少与一端连通，那么：
    # 4.
    # 遍历lead，找到有没有cell之间不连通的，尝试连通一下(就是前一个和start连，后一个和goal连，这俩不连通)
    # 所有cell前后都是连通的时候，找到那个同时和两端了连通的cell，尝试内部连接（内部用prm的方法）
    # 实在没有就算了，重新开始第一步
```

把connectRegions改成，前后两个cell的states两两check_motion，最后剩下的states都保证有跨cell边。

start的cell里的所有state可以当做都是intree的，最后再在start cell内进行prm。



主线：

1. 从头到尾遍历，expand_to_cell()，最后剩下lead[-2]和lead[-1]不连通；
2. 连通lead[-2]和lead[-1]
3. 在lead[-1]内做prm
4. 成功

case 1:

1. expand_to_cell()在lead[j]时，中道崩殂；
2. 重算lead
3. 从头再次遍历，如果已经连通的，就多采样几点继续连接（因为顺序遍历，因此能连接则都是in tree的），如果没有连通的， 就想办法expand_to_cell()
4. 成功回归主线第2点。

case 2:

1. 在expand_to_cell阶段，一定概率触发强制全cell连接