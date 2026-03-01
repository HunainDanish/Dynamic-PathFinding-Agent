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
def get_manhattan(p1, p2): return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
def get_euclidean(p1, p2): return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def search(grid, start_pos, goal_pos, algo, heuristic_type):
    start_node = grid[start_pos[0]][start_pos[1]]
    goal_node = grid[goal_pos[0]][goal_pos[1]]
    
    for row in grid:
        for node in row:
            node.parent, node.g, node.f = None, float('inf'), float('inf')

    start_node.g = 0
    h_func = get_manhattan if heuristic_type == "Manhattan" else get_euclidean
    start_node.h = h_func(start_pos, goal_pos)
    start_node.f = start_node.h
    
    pq = [(start_node.f, start_node)]
    visited = set()
    frontier_set = {start_node}
    start_time = time.perf_counter()
    
    while pq:
        current = heapq.heappop(pq)[1]
        if current in visited: continue
        if (current.row, current.col) == goal_pos:
            path = []
            temp = current
            while temp:
                path.append((temp.row, temp.col))
                temp = temp.parent
            return path[::-1], visited, frontier_set, (time.perf_counter() - start_time) * 1000

        visited.add(current)
        for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
            r, c = current.row + dr, current.col + dc
            if 0 <= r < ROWS and 0 <= c < COLS and not grid[r][c].is_wall:
                neighbor = grid[r][c]
                if neighbor in visited: continue
                
                new_g = current.g + 1
                if new_g < neighbor.g:
                    neighbor.parent = current
                    neighbor.g = new_g
                    neighbor.h = h_func((r, c), goal_pos)
                    neighbor.f = neighbor.g + neighbor.h if algo == "A*" else neighbor.h
                    if neighbor not in frontier_set:
                        heapq.heappush(pq, (neighbor.f, neighbor))
                        frontier_set.add(neighbor)
    return [], visited, frontier_set, 0

class PathfindingVisualizer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font = pygame.font.SysFont("Courier", 16, bold=True)
        self.grid = [[Node(r, c) for c in range(COLS)] for r in range(ROWS)]
        self.start, self.goal = (17, 10), (10, 10)
        self.agent_pos = self.start
        self.path, self.visited_nodes, self.frontier_nodes = [], set(), set()
        self.algo, self.heuristic, self.dynamic_mode = "A*", "Manhattan", False
        self.exec_time = 0
        self.generate_random_map(DENSITY)

    def generate_random_map(self, density):
        for r in range(ROWS):
            for c in range(COLS):
                self.grid[r][c].is_wall = random.random() < density
        self.grid[self.start[0]][self.start[1]].is_wall = False
        self.grid[self.goal[0]][self.goal[1]].is_wall = False

    def draw(self):
        self.screen.fill((30, 30, 30))
        for row in self.grid:
            for node in row:
                color = (50, 50, 50) # Default grid
                if node.is_wall: color = BLACK
                elif (node.row, node.col) == self.start: color = ORANGE
                elif (node.row, node.col) == self.goal: color = RED
                elif (node.row, node.col) == self.agent_pos: color = PURPLE
                elif (node.row, node.col) in self.path: color = GREEN
                elif node in self.visited_nodes: color = BLUE
                elif node in self.frontier_nodes: color = YELLOW
                pygame.draw.rect(self.screen, color, (node.x, node.y, GRID_SIZE-1, GRID_SIZE-1))

        # Dashboard Logic
        metrics = [
            f"ALGO: {self.algo} | HEURISTIC: {self.heuristic}",
            f"DYNAMIC MODE: {'ON' if self.dynamic_mode else 'OFF'}",
            f"NODES VISITED: {len(self.visited_nodes)}",
            f"PATH COST: {len(self.path)}",
            f"EXEC TIME: {self.exec_time:.2f} ms"
        ]
        for i, text in enumerate(metrics):
            surface = self.font.render(text, True, WHITE)
            self.screen.blit(surface, (10, ROWS * GRID_SIZE + 10 + (i * 20)))
        pygame.display.flip()

    def run(self):
        run = True
        while run:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: run = False
                if pygame.mouse.get_pressed()[0]: # Manual Wall Placement
                    mx, my = pygame.mouse.get_pos()
                    r, c = my // GRID_SIZE, mx // GRID_SIZE
                    if r < ROWS and c < COLS: self.grid[r][c].is_wall = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.path, self.visited_nodes, self.frontier_nodes, self.exec_time = \
                            search(self.grid, self.agent_pos, self.goal, self.algo, self.heuristic)
                    if event.key == pygame.K_a: self.algo = "GBFS" if self.algo == "A*" else "A*"
                    if event.key == pygame.K_h: self.heuristic = "Euclidean" if self.heuristic == "Manhattan" else "Manhattan"
                    if event.key == pygame.K_d: self.dynamic_mode = not self.dynamic_mode
                    if event.key == pygame.K_r: self.generate_random_map(DENSITY)

            if self.dynamic_mode and self.path:
                self.agent_pos = self.path.pop(0)
                if random.random() < 0.1: # 10% spawn chance per step
                    r, c = random.randint(0, ROWS-1), random.randint(0, COLS-1)
                    if (r, c) not in [self.agent_pos, self.goal]:
                        self.grid[r][c].is_wall = True
                        if (r, c) in self.path: # RE-PLANNING
                            self.path, self.visited_nodes, self.frontier_nodes, self.exec_time = \
                                search(self.grid, self.agent_pos, self.goal, self.algo, self.heuristic)
                time.sleep(0.05)
        pygame.quit()
if __name__ == "__main__":
    visualizer = PathfindingVisualizer()
    visualizer.run()
