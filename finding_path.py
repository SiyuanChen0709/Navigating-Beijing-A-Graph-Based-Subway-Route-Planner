"""
Finding the suitable path from station A to B

Copyright (c) 2026 Siyuan Chen, Weichun Zhang, Hao Ouyang
All rights reserved.

This file is part of project 2.
Unauthorized copying, modification, distribution, or use of this file,
via any medium, is strictly prohibited without prior permission.
"""
from basic_classes import Subway, Station
from typing import Any
from excel_reader import convert_to_subway

# For convinence, I copied codes of Queue/PriorityQueue from Course Notes and made some small modifications


class Queue:
    """A first-in-first-out (FIFO) queue of items.

    Stores data in a first-in, first-out order. When removing an item from the
    queue, the least recently-added item is the one that is removed.

    >>> q = Queue()
    >>> q.is_empty()
    True
    >>> q.enqueue('hello')
    >>> q.is_empty()
    False
    >>> q.enqueue('goodbye')
    >>> q.dequeue()
    'hello'
    >>> q.dequeue()
    'goodbye'
    >>> q.is_empty()
    True
    """
    # Private Instance Attributes:
    #   - _items: The items stored in this queue. The front of the list represents
    #             the front of the queue.
    _items: list

    def __init__(self) -> None:
        """Initialize a new empty queue."""
        self._items = []

    def is_empty(self) -> bool:
        """Return whether this queue contains no items.
        """
        return self._items == []

    def enqueue(self, item: Any) -> None:
        """Add <item> to the back of this queue.
        """
        self._items.append(item)

    def dequeue(self) -> Any:
        """Remove and return the item at the front of this queue.

        Raise an EmptyQueueError if this queue is empty.
        """
        if self.is_empty():
            raise EmptyQueueError
        else:
            return self._items.pop(0)


class PriorityQueue:
    """A queue of items that can be dequeued in priority order.

    When removing an item from the queue, the highest-priority item is the one
    that is removed.
    """
    # Private Instance Attributes:
    #   - _items: a list of the items in this priority queue
    _items: list[tuple[int, Any]]

    def __init__(self) -> None:
        """Initialize a new and empty priority queue."""
        self._items = []

    def is_empty(self) -> bool:
        """Return whether this priority queue contains no items.
        """
        return self._items == []

    def dequeue(self, is_return_priority=False) -> Any:
        """Remove and return the item with the highest priority.

        Raise an EmptyPriorityQueueError when the priority queue is empty.
        """
        if self.is_empty():
            raise EmptyQueueError
        else:
            _priority, item = self._items.pop()
            if is_return_priority:
                return item, _priority
            else:
                return item

    def enqueue(self, priority: int, item: Any) -> None:
        """Add the given item with the given priority to this priority queue.
        Note:
            priority = 0 means most important
        """
        i = 0
        while i < len(self._items) and self._items[i][0] > priority:
            # Loop invariant: all items in self._items[0:i]
            # have a lower priority than <priority>.
            i = i + 1

        self._items.insert(i, (priority, item))


class EmptyQueueError(Exception):
    """Exception raised when calling dequeue on an empty queue."""

    def __str__(self) -> str:
        """Return a string representation of this error."""
        return 'dequeue may not be called on an empty queue'

# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————


class SuitablePath:
    """Abstract class represent ways to find a suitable path."""
    subway: Subway

    def __init__(self, subway: Subway) -> None:
        self.subway = subway

    def finding_path(self, station1: Any, station2: Any) -> list[str]:
        """finding the suitable path from station1 to station2"""
        raise NotImplementedError


class BreadthFirstSearch(SuitablePath):
    """Using Breadth First Search (BFS) method to find a path."""

    def __init__(self, subway: Subway) -> None:
        super().__init__(subway)

    def finding_path(self, station1: Any, station2: Any) -> list[str]:
        """
        Using Breadth Search First (BFS) method to find a path.

        Preconditions:
            - station1 in self.subway._Stations
            - station2 in self.subway._Stations
            - self.subway is connected

        >>> subway = convert_to_subway("station_dataset.xlsx")
        >>> fp = BreadthFirstSearch(subway)
        >>> p1 = fp.finding_path('Xizhimen', 'National Library')
        >>> p1
        ['Xizhimen', 'Beijing Zoo', 'National Library']

        # the path from northwest to southeast
        >>> pp = fp.finding_path('Jiahuihu',"Bei'anhe")
        >>> len(pp)
        32

        """

        all_stations = self.subway.show_stations()
        s1 = all_stations[station1]
        s2 = all_stations[station2]
        q = Queue()
        q.enqueue(s1)
        prev = {s1: None}
        while not q.is_empty():
            curr = q.dequeue()
            if curr == s2:
                break
            else:
                for u in curr.neighbours:
                    if u not in prev:
                        prev[u] = curr
                        q.enqueue(u)
        path = []
        cur = s2
        while cur is not None:
            path.append(prev[cur])
            cur = prev[cur]
        # pop out the None element
        path.pop()
        path.reverse()
        # add the last element
        path.append(s2)
        path = [p.name for p in path]
        return path


class Dijkstra(SuitablePath):
    """Using Dijkstra method to find a path."""

    def __init__(self, subway: Subway) -> None:
        super().__init__(subway)

    def finding_path(self, station1: Any, station2: Any) -> list[str]:
        """Using Dijkstra method to find a path.

        Preconditions:
            - station1 in self.subway._Stations
            - station2 in self.subway._Stations
            - self.subway is connected

        >>> subway = convert_to_subway("station_dataset.xlsx")
        >>> fp = Dijkstra(subway)
        >>> p1 = fp.finding_path('Xizhimen', 'National Library')
        >>> p1
        ['Xizhimen', 'Beijing Zoo', 'National Library']
        >>> p2 = fp.finding_path('Xizhimen', "Ping'anli")
        >>> p2
        ['Xizhimen', 'Xinjie Kou', "Ping'anli"]
        """
        all_stations = self.subway.show_stations()
        s1 = all_stations[station1]
        s2 = all_stations[station2]

        if s1 == s2:
            return [s1.name]

        # a dictionary, storing the minimum distance from s1 to each station.
        distance = {}
        prev = {}
        priorityqueue = PriorityQueue()

        for line in s1.lines:
            start_state = (s1, line)
            # since at current station, the time it takes is 0.
            distance[start_state] = 0
            prev[start_state] = None
            priorityqueue.enqueue(0, start_state)

        while not priorityqueue.is_empty():
            curr_state, dis = priorityqueue.dequeue(is_return_priority=True)
            # print(curr_state[0].name, 'a')
            if dis > distance[curr_state]:
                continue
            if curr_state[0] == s2:
                break

            for u in curr_state[0].neighbours:
                for line in curr_state[0].neighbours[u]:
                    if curr_state[1] != line:
                        # print(curr_state[0].name, line, 'b', u.name)
                        cost_curr_to_u = 7
                    else:
                        # print(curr_state[0].name, line, 'c', u.name)
                        cost_curr_to_u = 3
                    next_state = (u, line)
                    if (next_state not in distance or
                            distance[curr_state] + cost_curr_to_u < distance[next_state]):
                        # print(next_state[0].name, 'd')
                        distance[next_state] = distance[curr_state] + cost_curr_to_u
                        priorityqueue.enqueue(distance[next_state], next_state)
                        prev[next_state] = curr_state
        some_finals = [final for final in distance if final[0].name == s2.name]
        list.sort(some_finals, key=lambda final: distance[final])
        # print(some_finals)
        final_curr = some_finals[0]
        final_so_far = []
        while final_curr is not None:
            final_so_far.append(final_curr[0].name)
            final_curr = prev[final_curr]

        final_so_far.reverse()
        return final_so_far


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
        'extra-imports': ['basic_classes', 'typing', 'excel_reader'],
        'allowed-io': []
    })
