"""Maze generation examples using DFS and Kruskal algorithms.

This script creates 30x30 mazes with two different algorithms and renders
an ASCII preview for each. It is intended as a quick reference for classic
maze generation techniques.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

Direction = str
Coords = Tuple[int, int]

# Cardinal direction utilities
OPPOSITE: Dict[Direction, Direction] = {"N": "S", "S": "N", "E": "W", "W": "E"}
DELTAS: Dict[Direction, Tuple[int, int]] = {
    "N": (0, -1),
    "S": (0, 1),
    "E": (1, 0),
    "W": (-1, 0),
}


def neighbors(x: int, y: int, width: int, height: int) -> Iterable[Tuple[Coords, Direction]]:
    """Yield neighbor coordinates within bounds with their direction from (x, y)."""
    for direction, (dx, dy) in DELTAS.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            yield (nx, ny), direction


def new_cell() -> Dict[Direction, bool]:
    """Create a cell with all four walls intact."""
    return {"N": True, "S": True, "E": True, "W": True}


def carve_passage(maze: List[List[Dict[Direction, bool]]], a: Coords, b: Coords, direction: Direction) -> None:
    """Remove walls between cells a and b in the given direction."""
    ax, ay = a
    bx, by = b
    maze[ay][ax][direction] = False
    maze[by][bx][OPPOSITE[direction]] = False


# Depth-First Search (recursive backtracking) -------------------------------

def generate_maze_dfs(width: int, height: int, *, seed: int | None = None) -> List[List[Dict[Direction, bool]]]:
    """Generate a maze using depth-first search with an explicit stack."""
    if seed is not None:
        random.seed(seed)

    maze = [[new_cell() for _ in range(width)] for _ in range(height)]
    stack: List[Coords] = [(0, 0)]
    visited = {(0, 0)}

    while stack:
        x, y = stack[-1]
        unvisited = [(coords, direction) for coords, direction in neighbors(x, y, width, height) if coords not in visited]
        if not unvisited:
            stack.pop()
            continue

        (nx, ny), direction = random.choice(unvisited)
        carve_passage(maze, (x, y), (nx, ny), direction)
        visited.add((nx, ny))
        stack.append((nx, ny))

    return maze


# Kruskal's algorithm -------------------------------------------------------

@dataclass
class DisjointSet:
    parent: Dict[Coords, Coords]
    rank: Dict[Coords, int]

    @classmethod
    def create(cls, width: int, height: int) -> "DisjointSet":
        parent = {(x, y): (x, y) for y in range(height) for x in range(width)}
        rank = {(x, y): 0 for y in range(height) for x in range(width)}
        return cls(parent=parent, rank=rank)

    def find(self, item: Coords) -> Coords:
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, a: Coords, b: Coords) -> bool:
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False

        if self.rank[root_a] < self.rank[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        if self.rank[root_a] == self.rank[root_b]:
            self.rank[root_a] += 1
        return True


def generate_maze_kruskal(width: int, height: int, *, seed: int | None = None) -> List[List[Dict[Direction, bool]]]:
    """Generate a maze using Kruskal's algorithm over grid edges."""
    if seed is not None:
        random.seed(seed)

    maze = [[new_cell() for _ in range(width)] for _ in range(height)]
    dsu = DisjointSet.create(width, height)

    edges: List[Tuple[Coords, Coords, Direction]] = []
    for y in range(height):
        for x in range(width):
            for (nx, ny), direction in neighbors(x, y, width, height):
                if direction in ("E", "S"):  # Avoid duplicate edges
                    edges.append(((x, y), (nx, ny), direction))

    random.shuffle(edges)

    for a, b, direction in edges:
        if dsu.union(a, b):
            carve_passage(maze, a, b, direction)

    return maze


# Rendering -----------------------------------------------------------------

def maze_to_ascii(maze: List[List[Dict[Direction, bool]]]) -> str:
    """Render the maze into an ASCII string."""
    height = len(maze)
    width = len(maze[0]) if height else 0
    horizontal_wall = "█"
    space = "  "

    lines: List[str] = []
    # Top boundary
    lines.append(horizontal_wall * (width * 2 + 1))

    for y in range(height):
        top = [horizontal_wall]
        middle = [horizontal_wall]
        for x in range(width):
            cell = maze[y][x]
            # Top wall
            top.append(horizontal_wall if cell["N"] else space)
            top.append(horizontal_wall)

            # Left wall and cell interior
            middle.append(space)
            middle.append(horizontal_wall if cell["E"] else space)
        lines.append("".join(top))
        lines.append("".join(middle))

    lines.append(horizontal_wall * (width * 2 + 1))
    return "\n".join(lines)


if __name__ == "__main__":
    WIDTH = HEIGHT = 30
    random.seed(42)

    print("Depth-First Search maze (30x30):")
    dfs_maze = generate_maze_dfs(WIDTH, HEIGHT)
    print(maze_to_ascii(dfs_maze))

    print("\nKruskal's algorithm maze (30x30):")
    kruskal_maze = generate_maze_kruskal(WIDTH, HEIGHT)
    print(maze_to_ascii(kruskal_maze))
