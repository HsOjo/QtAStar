import functools
import math
import random
from typing import List

STAT_OBSTACLE = 0  # 障碍物
STAT_FREE = 1  # 可通行


class Map:
    def __init__(self, width, height):
        self._w = width
        self._h = height

        self._points = [[STAT_FREE for _ in range(width)] for _ in range(height)]
        self.__iter__ = self._points.__iter__

    @property
    def w(self):
        return self._w

    @property
    def h(self):
        return self._h

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._points[item]
        elif isinstance(item, tuple):
            [x, y] = item
            return self._points[y][x]

    def __setitem__(self, key, value):
        [x, y] = key
        self._points[y][x] = value

    def get_points_by_status(self, status) -> List[tuple]:
        """获取所有可通行的点"""
        points = []
        for y in range(self._h):
            for x in range(self._w):
                if self[x, y] == status:
                    points.append((x, y))
        return points

    def generate_obstacle(self, num: int):
        """生成一定数量的障碍物"""
        f_points = self.get_points_by_status(STAT_FREE)
        count = min(num, len(f_points))
        for _ in range(count):
            r_index = random.randint(1, len(f_points)) - 1
            [x, y] = f_points.pop(r_index)
            self[x, y] = STAT_OBSTACLE

    @staticmethod
    def distance(p1, p2):
        [x1, y1] = p1
        [x2, y2] = p2
        return math.sqrt(pow(abs(x1 - x2), 2) + pow(abs(y1 - y2), 2))

    def find_path(self, sp, ep, is_eight):
        p_open = []
        p_closed = []
        p_info = {}

        def open_point(p, r, pp):
            # 探测某个点，并记录相关信息
            d = self.distance(p, ep)
            p_open.append(p)
            p_info[p] = {
                'range': r,  # 到达该点所需移动的步数
                'distance': d,  # 离终点所需的距离
                'weight': -(r + d),  # 寻路权重
                'parent': pp,  # 到达该点的上一个点
            }

        def close_point(p):
            # 关闭某个点，标记为已经探测过
            p_open.remove(p)
            p_closed.append(p)

        def check_available_point(p):
            # 检查是否为可通行且未探测过的点
            [x, y] = p
            if x < 0 or x >= self._w or y < 0 or y >= self._h:
                return False
            else:
                return self[x, y] == STAT_FREE and p not in p not in p_closed and p not in p_open

        if is_eight:
            # 遍历八个方向中，可通行的点
            selected = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        else:
            # 遍历四个方向中，可通行的点
            selected = [(0, -1), (-1, 0), (1, 0), (0, 1)]

        def find(p=sp, r=0):
            [x, y] = p
            p_open_current = p_open.copy()

            # 探测当前所在的点各个方向可通行的点
            for ox, oy in selected:
                pp = (x + ox, y + oy)
                if check_available_point(pp):
                    open_point(pp, r + 1, p)
                    p_open_current.append(pp)

            # 排序，获取权重最高的点，作为下一步的路径
            @functools.cmp_to_key
            def custom_sort(a, b):
                aw, bw = p_info[a]['weight'], p_info[b]['weight']
                if aw > bw:
                    return 1
                elif aw < bw:
                    return -1
                else:
                    return 0

            p_open_current = sorted(p_open_current, key=custom_sort, reverse=True)
            # 如果被打开的所有点都被关闭，则不可达
            if len(p_open) == 0:
                return False
            np = p_open_current[0]
            close_point(np)

            # 递归查找，直到找到终点
            if np != ep:
                return find(np, p_info[np]['range'])
            else:
                return True

        # 初始化开始的点
        open_point(sp, 0, None)
        close_point(sp)

        if find():
            # 关闭的点所形成的列表便是所找到的路径
            # 但该路径包含试错路径，需要从终点一步步返回，得到最短路径
            p = p_closed[-1]
            path = []
            while True:
                path.insert(0, p)
                p = p_info[p]['parent']
                if p is None:
                    break

            return path
        else:
            return None
