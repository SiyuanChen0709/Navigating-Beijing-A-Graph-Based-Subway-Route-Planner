"""
This file is used to visualize map.

Copyright (c) 2026 Siyuan Chen, Weichun Zhang, Hao Ouyang
All rights reserved.

This file is part of project 2.
Unauthorized copying, modification, distribution, or use of this file,
via any medium, is strictly prohibited without prior permission.
"""
import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from excel_reader import convert_to_subway
from nearby_stations import pickup

import finding_path

# For testing
# from basic_classes import Subway, Station


class MapViewer:
    """Visualize the subway"""

    def __init__(self, root, image_path, subway=convert_to_subway('station_dataset.xlsx')) -> None:
        self.root = root
        self.root.title("Route Planner for Beijing Subway")

        # Read the picture
        self.original_image = Image.open(image_path)
        self.orig_w, self.orig_h = self.original_image.size

        # Scaling
        self.scale = 0.2
        self.min_scale = 0.1
        self.max_scale = 5.0

        self.photo = None

        self.info_label = tk.Label(
            root,
            text="Scroll to Zoom  |  Drag on the Left to Move"
                 "  |  Left Click for Starting Location  |  Delete to Clear Selection"
                 "  |  Right click for Destination | Enter to Confirm Selection"
                 "  |  M to Change Mode",
            anchor="w"
        )
        self.info_label.pack(fill="x")

        self.compass = tk.Label(
            root,
            text="No selection yet",
            anchor="e"
        )
        self.compass.pack(fill="x")

        # Canvas
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # Anchor
        self.img_x = 150
        self.img_y = 40

        # Dragging
        self.dragging = False
        self.last_x = 0
        self.last_y = 0
        self.moved = False

        self.point_radius = 4  # Marking

        self.redraw_image(redraw_point=False)

        # Binding
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_click)

        # Delection
        self.canvas.bind("<Delete>", self.on_delete)
        self.canvas.focus_set()

        # Confirmation
        self.canvas.bind("<Return>", self.on_enter)
        self.canvas.focus_set()

        # Mode Change
        self.canvas.bind('m', self.on_change_mode)

        self.subway = subway
        # These comment lines are used to test whether all stations are on the correct location. no need to uncomment
        # for stop in self.subway._Stations:
        #     r = 4
        #     s = self.subway._Stations[stop]
        #     # converting the coordinate of pic in terms of coord in terms of canvas
        #     x = s.coordinates[0] * self.scale + self.img_x
        #     y = s.coordinates[1] * self.scale + self.img_y
        #     self.canvas.create_oval(
        #         x - r, y - r,
        #         x + r, y + r,
        #         fill="blue", outline="blue",
        #         tags="point"
        #     )
        #     for u in s.neighbours:
        #         x_1 = u.coordinates[0] * self.scale + self.img_x
        #         y_1 = u.coordinates[1] * self.scale + self.img_y
        #         self.canvas.create_line(x, y, x_1, y_1)
        # storing the coordinate of point in terms of canvas

        self.start_ids = []
        self.start_coordinates = []
        self.dest_ids = []
        self.dest_coordinates = []
        self.path_ids = []
        self.path_coordinates = []

        # change mode
        self.is_most_efficient = False

    def redraw_image(self, redraw_point=True) -> None:
        """Refresh"""
        new_w = int(self.orig_w * self.scale)
        new_h = int(self.orig_h * self.scale)

        """Trade-off between performance and quality
        https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-filters
        """
        resized = self.original_image.resize(size=(new_w, new_h), resample=Image.Resampling.BOX)
        self.photo = ImageTk.PhotoImage(resized)

        self.canvas.delete("image")
        self.canvas.create_image(
            self.img_x, self.img_y,
            anchor=tk.NW,
            image=self.photo,
            tags="image"
        )
        if redraw_point:
            for i in range(len(self.start_coordinates)):
                p_id = self.canvas.create_oval(
                    self.start_coordinates[i][0] - self.point_radius,
                    self.start_coordinates[i][1] - self.point_radius,
                    self.start_coordinates[i][0] + self.point_radius,
                    self.start_coordinates[i][1] + self.point_radius,
                    fill="red", outline="red",
                    tags="point")
                self.start_ids.append(p_id)

            for i in range(len(self.dest_coordinates)):
                p_id = self.canvas.create_oval(
                    self.dest_coordinates[i][0] - self.point_radius,
                    self.dest_coordinates[i][1] - self.point_radius,
                    self.dest_coordinates[i][0] + self.point_radius,
                    self.dest_coordinates[i][1] + self.point_radius,
                    fill="blue", outline="blue",
                    tags="point")
                self.dest_ids.append(p_id)

            for i in range(len(self.path_coordinates)):
                p_id = self.canvas.create_oval(
                    self.path_coordinates[i][0] - self.point_radius-2,
                    self.path_coordinates[i][1] - self.point_radius-2,
                    self.path_coordinates[i][0] + self.point_radius+2,
                    self.path_coordinates[i][1] + self.point_radius+2,
                    fill="green", outline="green",
                    tags="point")
                self.path_ids.append(p_id)

    def on_mousewheel(self, event) -> None:
        """Zooming the canvas centring at the cursor"""
        old_scale = self.scale

        # Zooming-in or zooming-out
        if hasattr(event, "delta") and event.delta != 0:
            if event.delta > 0:
                new_scale = self.scale * 1.1
            else:
                new_scale = self.scale / 1.1
        elif event.num == 4:
            new_scale = self.scale * 1.1
        elif event.num == 5:
            new_scale = self.scale / 1.1
        else:
            return

        # Avoid over-zooming
        new_scale = max(self.min_scale, min(new_scale, self.max_scale))
        if abs(new_scale - old_scale) < 1e-12:
            return

        # Location of the cursor
        cx = event.x
        cy = event.y

        # Original location of the cursor
        orig_x = (cx - self.img_x) / old_scale
        orig_y = (cy - self.img_y) / old_scale

        # Before zooming
        p_sc = []
        p_dc = []
        p_pc = []
        for coord in self.start_coordinates:
            p_sc.append([(coord[0] - self.img_x) / old_scale, (coord[1] - self.img_y) / old_scale])

        for coord in self.dest_coordinates:
            p_dc.append([(coord[0] - self.img_x) / old_scale, (coord[1] - self.img_y) / old_scale])

        for coord in self.path_coordinates:
            p_pc.append([(coord[0] - self.img_x) / old_scale, (coord[1] - self.img_y) / old_scale])

        # Update the scale
        self.scale = new_scale

        # Calibration
        self.img_x = cx - orig_x * self.scale
        self.img_y = cy - orig_y * self.scale
        temp_ids = self.start_ids.copy()

        for i in range(len(self.start_coordinates)):
            self.start_coordinates[i][0] = self.img_x + p_sc[i][0] * self.scale
            self.start_coordinates[i][1] = self.img_y + p_sc[i][1] * self.scale
            self.canvas.delete(temp_ids[i])

        temp_ids = self.dest_ids.copy()

        for i in range(len(self.dest_coordinates)):
            self.dest_coordinates[i][0] = self.img_x + p_dc[i][0] * self.scale
            self.dest_coordinates[i][1] = self.img_y + p_dc[i][1] * self.scale
            self.canvas.delete(temp_ids[i])

        temp_ids = self.path_ids.copy()

        for i in range(len(self.path_coordinates)):
            self.path_coordinates[i][0] = self.img_x + p_pc[i][0] * self.scale
            self.path_coordinates[i][1] = self.img_y + p_pc[i][1] * self.scale
            self.canvas.delete(temp_ids[i])

        self.start_ids = []
        self.dest_ids = []
        self.path_ids = []

        self.redraw_image()

    def on_button_press(self, event) -> None:
        """Prepare for dragging"""
        self.dragging = True
        self.last_x = event.x
        self.last_y = event.y
        self.moved = False

    def mark(self, event, colour: str, coordinate=None) -> None:
        """Mark the current location"""

        # Convert to original coordinates
        orig_x = (event.x - self.img_x) / self.scale
        orig_y = (event.y - self.img_y) / self.scale

        # Validate the coordinates
        if 0 <= orig_x <= self.orig_w and 0 <= orig_y <= self.orig_h:

            self.info_label.config(
                text="Scroll to Zoom  |  Drag on the Left to Move"
                     "  |  Left Click for Starting Location  |  Delete to Clear Selection"
                     "  |  Right click for Destination | Enter to Confirm Selection"
                     "  |  M to Change Mode",
                anchor="w"
            )

            self.compass.config(
                text=f"On Canvas: ({event.x}, {event.y})    Original: ({orig_x:.1f}, {orig_y:.1f})"
            )

            r = self.point_radius

            if colour == 'red':
                self.start_coordinates += [[event.x, event.y]]
                self.start_ids += [self.canvas.create_oval(
                    event.x - r, event.y - r,
                    event.x + r, event.y + r,
                    fill='red', outline='red',
                    tags="point"
                )]
            elif colour == 'blue':
                self.dest_coordinates += [[event.x, event.y]]
                self.dest_ids += [self.canvas.create_oval(
                    event.x - r, event.y - r,
                    event.x + r, event.y + r,
                    fill='blue', outline='blue',
                    tags="point"
                )]
            else:
                graph_x = coordinate[0] * self.scale + self.img_x
                graph_y = coordinate[1] * self.scale + self.img_y
                self.path_coordinates += [[graph_x, graph_y]]
                self.path_ids += [
                    self.canvas.create_oval(
                        graph_x - r - 2, graph_y - r - 2,
                        graph_x + r + 2, graph_y + r + 2,
                        fill='green', outline='green',
                        tags="point")]
                self.canvas.update()  # visualize that point
            # print(f"Original: ({orig_x:.1f}, {orig_y:.1f})")
        else:
            self.info_label.config(text="Oops, out of the map. Please try again.")

    def on_drag(self, event) -> None:
        """Moving by the left button"""
        if not self.dragging:
            return

        dx = event.x - self.last_x
        dy = event.y - self.last_y

        if dx != 0 or dy != 0:
            self.moved = True

        self.img_x += dx
        self.img_y += dy

        # self.redraw_image()
        # using canvas.move to make the process smoother
        self.canvas.move('image', dx, dy)
        self.canvas.move('point', dx, dy)
        self.last_x = event.x
        self.last_y = event.y

        # updating points location
        for coord in self.start_coordinates:
            coord[0] += dx
            coord[1] += dy

        for coord in self.dest_coordinates:
            coord[0] += dx
            coord[1] += dy

        for coord in self.path_coordinates:
            coord[0] += dx
            coord[1] += dy

    def on_button_release(self, event) -> None:
        """Release the left button: clicking if undragged"""
        if not self.dragging:
            return

        self.dragging = False

        # Clicking if undragged
        if self.moved:
            return

        self.mark(event, 'red')

    def on_right_click(self, event) -> None:
        """Right Click"""
        self.mark(event, 'blue')

    def on_delete(self, event) -> None:
        """Being called when <delete> button is pressed"""

        for pid in self.start_ids:
            self.canvas.delete(pid)
        for pid in self.dest_ids:
            self.canvas.delete(pid)
        for pid in self.path_ids:
            self.canvas.delete(pid)
        self.start_ids = []
        self.dest_ids = []
        self.path_ids = []

        self.start_coordinates = []
        self.dest_coordinates = []
        self.path_coordinates = []

    def on_change_mode(self, event) -> None:
        """Change the path selection mode between less transfer station and less stops"""
        self.is_most_efficient = not self.is_most_efficient
        if self.is_most_efficient:
            messagebox.showinfo(title='SUCCESS',
                                message=f'Successfully changed the selection mode. '
                                        f'Current mode is Most Efficient Mode.')
        else:
            messagebox.showinfo(title='SUCCESS',
                                message=f'Successfully changed the selection mode. '
                                        f'Current mode is Minimum Station Mode.')

    def on_enter(self, event) -> None:
        """Confirm the selection when 'Enter' is pressed"""
        # print('enter')
        if len(self.start_coordinates) != 1 or len(self.dest_coordinates) != 1:
            messagebox.showwarning(title='WARNING', message='Invalid Selection. Please try again.')
            return
        else:
            messagebox.showinfo(title='SUCCESS',
                                message='Selection submitted. Loading...(feel free to close this window)')

            # converting the given points' coordination in terms of the picture coordination
            start_x = (self.start_coordinates[0][0] - self.img_x) / self.scale
            start_y = (self.start_coordinates[0][1] - self.img_y) / self.scale
            end_x = (self.dest_coordinates[0][0] - self.img_x) / self.scale
            end_y = (self.dest_coordinates[0][1] - self.img_y) / self.scale

            # getting the nearest and second nearest station
            start = pickup(self.subway, start_x, start_y)
            end = pickup(self.subway, end_x, end_y)
            # for s in start:
            #     print(s.name)
            # for e in end:
            #     print(e.name)

            possible_paths = []
            if not self.is_most_efficient:
                search_method = finding_path.BreadthFirstSearch(self.subway)
            else:
                search_method = finding_path.Dijkstra(self.subway)

            for s in start:
                for e in end:
                    possible_paths.append((search_method.finding_path(s.name, e.name), end[e] + start[s]))
            final = self.finalize_result(possible_paths)
            self.visualize_path(final, event)

    def finalize_result(self, lst: list[tuple[list[str], int]]) -> tuple[list[str], tuple]:
        """
        Finalize the result and return a final path.
        This finalization function calculate the total amount of time for each path roughly, and pick the fastest path.
        This is the way of calculate time:
        Total = (distance between start point and start station) * walking speed +
                (average time spent for subway on each station) * number of stops +
                (distance between end point and end station) * walking speed
        To make calculation easier, we made these two assumptions:
            1. minimum distance (i.e. distance = 1) takes 0.15 minutes.
            2. average time spend on each regular station: 3 minutes.
            3. average time spend on each transfer station: (3 + 4) minutes.
        These assumptions, admittedly, are rough,
        but reasonable and acceptable based on official website of Beijing Subway:
        https://www.bjsubway.com/
        Note: since it's a Chinese website, the url above may be opened slowly and/or can't be opened successfully.
        """
        final_so_far = []
        time_so_far = (999999999, 0)
        all_stations = self.subway.show_stations()

        for path in lst:
            # check the amount of transfer station
            transfer = 0
            for i in range(len(path[0]) - 2):
                # print(666, all_stations[path[i]].lines.intersection(
                #            all_stations[path[i+1]].lines, all_stations[path[i+2]].lines))

                if len(all_stations[path[0][i]].lines.intersection(
                           all_stations[path[0][i+1]].lines, all_stations[path[0][i+2]].lines)) == 0:
                    transfer += 1

            # compute the total amount of time for current path
            t = (len(path[0]) - 1) * 3 + path[1] * 0.15 + transfer * 4
            # print(t, path[0], path[1])
            if t < time_so_far[0]:
                final_so_far = path[0]
                time_so_far = (round(t), transfer)

        return final_so_far, time_so_far

    def visualize_path(self, lst: tuple[list[str], tuple], event) -> None:
        """visualize the given final path."""
        all_station = self.subway.show_stations()
        exception_1 = ["Sidao Qiao", "Jin'anqiao", "Pingguoyuan", "Yangzhuang"]
        exception_2 = ["Life Science Park", "Xi'erqi", "Qinghe Railway Station", "Shangdi"]
        exception_3 = ["Zhufangbei", "Xi'erqi", "Qinghe Railway Station", "Longze"]
        print(lst)
        if len(lst[0]) == 0:
            messagebox.showwarning('ERROR', "Your start/end point is too far to the subway!")
        else:
            e1 = all(station in lst[0] for station in exception_1)
            e2 = all(station in lst[0] for station in exception_2)
            e3 = all(station in lst[0] for station in exception_3)
            e = [e1, e2, e3]
            exception_num = e.count(True)
            for stop in lst[0]:
                station = all_station[stop]
                self.mark(event=event, colour='green', coordinate=station.coordinates)

                time.sleep(0.3)
            messagebox.showinfo(title='RESULT',
                                message=f'Current path has {len(lst[0])-1} stops, \n'
                                        f'{lst[1][1]+exception_num} transfer stations, \n'
                                        f'roughly takes {round(lst[1][0])+exception_num*4} minutes.')


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
        'extra-imports': ['time', 'tkinter', 'PIL', 'excel_reader', 'nearby_stations', 'finding_path'],
        'allowed-io': []
    })
