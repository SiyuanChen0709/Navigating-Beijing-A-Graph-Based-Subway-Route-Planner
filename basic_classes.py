"""
This file is used to store all basic classes needed for the whole program.

Copyright (c) 2026 Siyuan Chen, Weichun Zhang, Hao Ouyang
All rights reserved.

This file is part of project 2.
Unauthorized copying, modification, distribution, or use of this file,
via any medium, is strictly prohibited without prior permission.
"""

from __future__ import annotations
from typing import Any
from collections import defaultdict


class Station:
    """
    A vertex representing a station of the subway.

    Instance Attributes:
    - name: the name of this station
    - neighbours: a dictionary that maps neighbour stations to a set of line(s) connect these two stations.
    - lines: a set of string showing lines that current Station belongs to
    - coordinate: a tuple (x, y), storing the coordinates of the station on canvas
    """
    name: str
    neighbours: dict[Station, set[str]]
    lines: set[str]
    coordinates: tuple[int, int]

    def __init__(self, name: str,  coordinates: tuple[int, int], neighbours: dict, lines: set) -> None:
        self.name = name
        self.coordinates = coordinates
        self.neighbours = neighbours
        self.lines = lines

    def is_connected(self, name: Any, visited: set) -> bool:
        """return whether current station and the name are connected."""

        if self.name == name:
            return True
        else:
            visited.add(self)
            for u in self.neighbours:
                if u not in visited:
                    if u.is_connected(name, visited):
                        return True
            return False

    def distance(self, coordinate: tuple) -> int:
        """
        return the distance between current station and the given coordinate.
        >>> s = Station('name', (0, 0), {}, {})
        >>> s.distance((3, 4))
        5
        >>> s.distance((-5, 12))
        13
        """
        x = abs(self.coordinates[0] - coordinate[0])
        y = abs(self.coordinates[1] - coordinate[1])
        return round((x ** 2 + y ** 2) ** 0.5)

    # def shortest_path_length(self, name: Any, visited: list, curr_step: int) -> int:
    #     """return the length of the shortest path between the current station and the name."""
    #     if self.name == name:
    #         return curr_step
    #     else:
    #         new_visited = visited.copy() + [self]
    #         steps = []
    #         for u in self.neighbours:
    #             if u not in new_visited:
    #                 steps += [u.shortest_path_length(name, new_visited, curr_step + 1)]
    #         if not steps:
    #             return 99999  # lazy to import math.inf
    #         else:
    #             return min(steps)

    # def some_possible_path(self, name: Any, visited: list, min_distance: int, target_coord: tuple) -> list:
    #     """return some possible path from current station to name"""
    #     if self.name == name:
    #         return visited + [self.name]
    #     # to avoid aimless recursion, this elif line is added. Thus, some paths that are obviously inefficient are
    #     # not considered anymore
    #     elif self.distance(target_coord) - min_distance > 50:
    #         return []
    #     else:
    #         new_visited = visited.copy() + [self.name]
    #         poss = []
    #         # update current distance
    #         new_min_distance = min(self.distance(target_coord), min_distance)
    #         for u in self.neighbours:
    #             if u.name not in new_visited:
    #                 poss += u.some_possible_path(name, new_visited, new_min_distance, target_coord)
    #         if not poss:
    #             return []
    #         else:
    #             return poss


class Subway:
    """
    A graph contains all stations of the subway

    Instance Attributes:
    - _Stations: a dictionary mapping the name of the station to the Station
    - _Lines: a set storing all lines in the subway
    - blocks: a defaultdict mapping every block of the map to stations in the block
    """
    blocks: defaultdict
    _Stations: dict[str, Station]
    _Lines: set[str]

    def __init__(self) -> None:
        self.blocks = defaultdict(dict)
        self._Stations = {}
        self._Lines = set()

    def add_station(self, station: Station) -> None:
        """add the given Station into the subway"""
        gx = co2id(station.coordinates[0])
        gy = co2id(station.coordinates[1])

        if gy not in self.blocks[gx]:
            self.blocks[gx][gy] = []

        self.blocks[gx][gy].append(station)
        self._Stations[station.name] = station
        self._Lines = self._Lines.union(station.lines)

    def show_stations(self) -> dict[str, Station]:
        """showing all stations"""
        return self._Stations

    def distance(self, item1: Any, item2: Any) -> int:
        """return the distance between two given item"""
        v1 = self._Stations[item1]
        v2_co = self._Stations[item2].coordinates
        return v1.distance(v2_co)

    def add_neighbours(self, station1: str, station2: str):
        """
        Let giving stations become neighbours.
        >>> stop1 = Station('stop1', (0, 0), {}, {'Line 1'})
        >>> stop2 = Station('stop2', (1, 0), {}, {'Line 1', 'Line 3'})
        >>> subway = Subway()
        >>> subway.add_station(stop1)
        >>> subway.add_station(stop2)
        >>> subway.add_neighbours(stop1.name, stop2.name)
        >>> n = [(stop.name, stop1.neighbours[stop]) for stop in stop1.neighbours]
        >>> n
        [('stop2', {'Line 1'})]
        """
        try:
            s1 = self._Stations[station1]
        except KeyError:
            print(f'{station1} is not in the subway.')
            return
        try:
            s2 = self._Stations[station2]
        except KeyError:
            print(f'{station2} is not in the subway.')
            return
        s1.neighbours[s2] = s1.lines.intersection(s2.lines)
        s2.neighbours[s1] = s2.lines.intersection(s1.lines)

    # def shortest_path_length(self, item1: Any, item2: Any) -> int:
    #     """
    #     Given the two item, the function will find the shortest length of the path between this two items.
    #     ValueError will be raised if: 1. item1 or item2 not in self, or 2. item1 and item2 are not connected.
    #     The function treated every station same(i.e. no differences between transfer station and regular station).
    #     """
    #     if not (item1 in self._Stations and item2 in self._Stations):
    #         raise ValueError("At least one item are not in the Subway")
    #     elif not self._Stations[item1].is_connected(item2, set()):
    #         raise ValueError("Given items are not connected")
    #     else:
    #         v = self._Stations[item1]
    #         return v.shortest_path_length(item2, [], 0)

    # def some_possible_path(self, item1: Any, item2: Any) -> list:
    #     """The function will return a list of lists, each list represent a path from item1 to item2"""
    #     if not (item1 in self._Stations and item2 in self._Stations):
    #         raise ValueError("At least one item are not in the Subway")
    #     elif not self._Stations[item1].is_connected(item2, set()):
    #         raise ValueError("Given items are not connected")
    #
    #     v1 = self._Stations[item1]
    #     v2_coord = self._Stations[item2].coordinates
    #     distance = v1.distance(v2_coord)
    #     final = v1.some_possible_path(item2, [], distance, v2_coord)
    #     result = []
    #     curr_ind = 0
    #     for i in range(len(final)):
    #         if final[i] == item2:
    #             result += [final[curr_ind: i + 1]]
    #             curr_ind = i + 1
    #     return result
    #
    # def efficient_path(self, candidates: list[list], is_less_transfer=False) -> list:
    #     """
    #     The function will return the most efficient path between two given stations.
    #     When is_less_transfer is False, return the path with least stops.
    #     Otherwise, return the path with least transfer station.
    #     """
    #     curr = []
    #     min_length = 999  # lazy to import math.inf
    #     if not is_less_transfer:
    #         for path in candidates:
    #             if len(path) < min_length:
    #                 min_length = len(path)
    #                 curr = [path]
    #             elif len(path) == min_length:
    #                 curr.append(path)
    #         if len(curr) == 1:
    #             # print('a')
    #             return curr[0]
    #         else:  # case that two possible path have same number of stops
    #             # print('b')
    #             return self.efficient_path(curr, is_less_transfer=True)
    #     else:
    #         # getting the number of transfer station for each path
    #         num_trans = [(99999, -1)]
    #         for j in range(len(candidates)):
    #             tr_sf = 0
    #             for i in range(1, len(candidates[j])-1):
    #                 next_stop = self._Stations[candidates[j][i+1]]
    #                 prev_stop = self._Stations[candidates[j][i-1]]
    #                 curr_stop = self._Stations[candidates[j][i]]
    #                 if len(next_stop.lines.intersection(prev_stop.lines, curr_stop.lines)) == 0:
    #                     tr_sf += 1
    #             if tr_sf < num_trans[0][0]:
    #                 # print(tr_sf)
    #                 num_trans = [(tr_sf, j)]
    #             elif tr_sf == num_trans[0][0]:
    #                 # print(tr_sf, 2)
    #                 num_trans += [(tr_sf, j)]
    #         # only one path has least number of transfer station
    #         if len(num_trans) == 1:
    #             # print('c')
    #             return candidates[num_trans[0][1]]
    #         # more than one path has same number of transfer station
    #         else:
    #             new_candidate = []
    #             ind = {po[1] for po in num_trans}
    #             for i in range(len(candidates)):
    #                 if i in ind:
    #                     new_candidate += [candidates[i]]
    #             cur = [-1, 2**30]
    #             for i in range(len(new_candidate)):
    #                 dis_sf = 0
    #                 tar_cod = self._Stations[new_candidate[i][-1]].coordinates
    #                 for j in range(len(new_candidate[i])):
    #                     station = self._Stations[new_candidate[i][j]]
    #                     dis_sf += station.distance(tar_cod)
    #                 # print(dis_sf)
    #                 if dis_sf < cur[1]:
    #                     cur[0] = i
    #                     cur[1] = dis_sf
    #             # print('d')
    #             return new_candidate[cur[0]]


def co2id(c: float) -> int:
    """Convert the given coordinate to the corresponding index"""
    return int(c // 150.0)


if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
    # when doing doctest, all examples are failed. But when doing tests by right-click the function, all are passed.
    # we don't know why
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['__future__', 'typing', 'collection'],
        'allowed-io': []
    })
