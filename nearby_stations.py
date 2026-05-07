"""
Find stations nearby
Copyright (c) 2026 Siyuan Chen, Weichun Zhang, Hao Ouyang
All rights reserved.

This file is part of project 2.
Unauthorized copying, modification, distribution, or use of this file,
via any medium, is strictly prohibited without prior permission.
"""
from excel_reader import convert_to_subway
import basic_classes


def _validate(cx: float, cy: float, height: float = 32 * 150.0, width: float = 28 * 150.0) -> bool:
    """Check whether the corresponding location is out of the map."""
    if cx * (cx - height) < 0 and cy * (cy - width) < 0:
        return True
    else:
        return False


def _dist(station: basic_classes.Station, cx: float, cy: float) -> float:
    """Return the squared distance between the given station and the given pair of coordinates"""
    return (station.coordinates[0] - cx) ** 2 + (station.coordinates[1] - cy) ** 2


def _candidates(subway: basic_classes.Subway, cx: float, cy: float) -> list[basic_classes.Station]:
    """Return a list of nearest stations to the given location."""

    gx = basic_classes.co2id(cx)
    gy = basic_classes.co2id(cy)

    if gy not in subway.blocks[gx]:
        lst = []
    else:
        lst = subway.blocks[gx][gy]

    return lst


def _bucket(cx: float, cy: float) -> list[tuple[float, float]]:
    """..."""
    buck = []

    for i in range(-2, 3):
        for j in range(-2, 3):
            kx = cx + i * 150.0
            ky = cy + j * 150.0
            if _validate(kx, ky):
                buck.append((kx, ky))

    return buck


def _collecting(subway: basic_classes.Subway, cx: float, cy: float) -> list[basic_classes.Station]:
    lst = []
    coords = _bucket(cx, cy)

    for cx, cy in coords:
        lst.extend(_candidates(subway, cx, cy))

    return lst


def pickup(subway: basic_classes.Subway, cx: float, cy: float) -> dict[basic_classes.Station, int]:
    """
    Return a list containing the nearest and the second nearest station to the given location
    >>> sub = convert_to_subway('station_dataset.xlsx')
    >>> res = pickup(sub, 3710, 1038)  # a location between terminal 2 and 3, but near terminal 2
    >>> result = [station.name for station in res]
    >>> result
    ['Terminal 2', 'Terminal 3']
    >>> res2 = pickup(sub, 2412, 3561)  # a location at Daxing Airport
    >>> result2 = [station.name for station in res2]
    >>> result2
    ['Daxing Airport']
    >>> res3 = pickup(sub, 52, 2749)  # a very far point
    >>> res3
    {}
    """

    cand = _collecting(subway, cx, cy)

    sx = (basic_classes.co2id(cx) - 2) * 150.0
    sy = (basic_classes.co2id(cy) - 2) * 150.0
    lx = (sx + 3) + 150.0
    ly = (sy + 3) + 150.0

    r = min(cx - sx, lx - cx, cy - sy, ly - cy)

    mapping = [(s, _dist(s, cx, cy)) for s in cand if _dist(s, cx, cy) <= r ** 2]

    mapping.sort(key=lambda x: x[1])

    if len(mapping) == 0:
        return {}
    elif len(mapping) == 1:
        dis1 = mapping[0][0].distance((cx, cy))
        return {mapping[0][0]: dis1}
    else:
        dis1 = mapping[0][0].distance((cx, cy))
        dis2 = mapping[1][0].distance((cx, cy))
        return {mapping[0][0]: dis1, mapping[1][0]: dis2}


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
        'extra-imports': ['basic_classes', 'excel_reader'],
    })
