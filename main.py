import pygame
import random
import math
import heapq
import time
import tkinter as tk
from tkinter import simpledialog

# --- User Input Setup ---
def get_user_params():
    root = tk.Tk()
    root.withdraw()
    r = simpledialog.askinteger("Input", "Number of Rows:", initialvalue=30, minvalue=10, maxvalue=60)
    c = simpledialog.askinteger("Input", "Number of Columns:", initialvalue=40, minvalue=10, maxvalue=80)
    d = simpledialog.askfloat("Input", "Obstacle Density (0.1 to 0.5):", initialvalue=0.3, minvalue=0.0, maxvalue=1.0)
    return r, c, d

ROWS, COLS, DENSITY = get_user_params()
GRID_SIZE = 20
WIDTH, HEIGHT = COLS * GRID_SIZE, (ROWS * GRID_SIZE) + 120 # Extra space for dashboard

# --- Colors ---
WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (200, 200, 200)
GREEN, RED, ORANGE = (0, 255, 0), (255, 0, 0), (255, 165, 0)
BLUE, YELLOW, PURPLE = (0, 0, 255), (255, 255, 0), (128, 0, 128)

class Node:
    def __init__(self, row, col):
        self.row, self.col = row, col
        self.x, self.y = col * GRID_SIZE, row * GRID_SIZE
        self.is_wall = False
        self.parent = None
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')

    def __lt__(self, other): return self.f < other.f
