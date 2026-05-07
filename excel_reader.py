"""
This file is used to read realworld data and convert them into corresponding classes

Copyright (c) 2026 Siyuan Chen, Weichun Zhang, Hao Ouyang
All rights reserved.

This file is part of project 2.
Unauthorized copying, modification, distribution, or use of this file,
via any medium, is strictly prohibited without prior permission.
"""

import pandas
from typing import Any
from basic_classes import Station, Subway
# download openpyxl


def _read_excel(file_name: str) -> dict[str, list[Any]]:
    """read the file_name's Excel table and convert it into a dictionary"""
    data = pandas.read_excel(file_name)
    stations = {}
    for row in data.values.tolist():
        neigh = set(row[1].split(','))
        line = set(row[2].split(','))
        coord = (int(row[3]), int(row[4]))
        stations[row[0]] = [neigh, line, coord]
    return stations


def convert_to_subway(file_name: str) -> Subway:
    """Converting the given file to Subway"""
    data = _read_excel(file_name)
    subway = Subway()
    # create all Station based on given data
    for s in data:
        station = Station(name=s, neighbours={}, lines=data[s][1], coordinates=data[s][2])
        subway.add_station(station)

    # adding neighbours to all the Stations, lines to the subway.
    stops = subway.show_stations()
    for s in stops:
        for nei in data[s][0]:
            subway.add_neighbours(s, nei)
    return subway


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
        'extra-imports': ['basic_classes', 'excel_reader', 'pandas', 'typing'],
        'allowed-io': ['_read_excel']
    })
