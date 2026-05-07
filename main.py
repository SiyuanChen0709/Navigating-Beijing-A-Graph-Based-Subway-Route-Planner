"""
Main

Copyright (c) 2026 Siyuan Chen, Weichun Zhang, Hao Ouyang
All rights reserved.

This file is part of project 2.
Unauthorized copying, modification, distribution, or use of this file,
via any medium, is strictly prohibited without prior permission.
"""
from map_visualizer import MapViewer
import tkinter as tk

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("1200x800")

    app = MapViewer(root, "Beijing Rail Transit Lines English.png")

    root.mainloop()

