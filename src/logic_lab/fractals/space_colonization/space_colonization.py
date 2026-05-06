from dataclasses import dataclass
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass
class Node:
    x: float
    y: float
    parent: "Node" = None
    children: list = None
    reached: bool = False

    def __post_init__(self):
        if self.children is None:
            self.children = []

    def distance_to(self, attractor):
        dx = self.x - attractor.x
        dy = self.y - attractor.y
        return np.sqrt(dx * dx + dy * dy)


class SpaceColonization:
    def __init__(self, width=800, height=800, kill_distance=40, max_distance=100):
        self.width = width
        self.height = height
        self.kill_distance = kill_distance
        self.max_distance = max_distance

        self.root = Node(width / 2, height - 50)
        self.nodes = [self.root]
        self.attractors = self._generate_attractors()

    def _generate_attractors(self):
        """Generate random attractor points"""
        attractors = []
        for _ in range(300):
            x = np.random.uniform(50, self.width - 50)
            y = np.random.uniform(50, self.height - 100)
            attractors.append(Node(x, y))
        return attractors

    def update(self):
        """Grow tree towards attractors"""
        if not self.attractors:
            return

        closest_node = None
        closest_attractor = None
        closest_dist = float("inf")

        for attractor in self.attractors:
            for node in self.nodes:
                dist = node.distance_to(attractor)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_node = node
                    closest_attractor = attractor

        if closest_dist < self.kill_distance:
            self.attractors.remove(closest_attractor)
        elif closest_dist < self.max_distance:
            dx = closest_attractor.x - closest_node.x
            dy = closest_attractor.y - closest_node.y
            length = np.sqrt(dx * dx + dy * dy)

            if length > 0:
                dx = (dx / length) * 4
                dy = (dy / length) * 4

                new_node = Node(closest_node.x + dx, closest_node.y + dy, parent=closest_node)
                closest_node.children.append(new_node)
                self.nodes.append(new_node)

    def draw(self):
        py5.background(255)

        py5.stroke(0)
        py5.stroke_weight(1.5)
        for node in self.nodes:
            if node.parent:
                py5.line(node.x, node.y, node.parent.x, node.parent.y)

        py5.no_stroke()
        py5.fill(255, 150, 0, 100)
        for attractor in self.attractors:
            py5.circle(attractor.x, attractor.y, 3)


def setup():
    py5.size(800, 800)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    global colonization
    colonization = SpaceColonization(py5.width, py5.height, kill_distance=30)


def draw():
    for _ in range(3):
        colonization.update()

    colonization.draw()

    py5.fill(0)
    py5.text_align(py5.LEFT)
    py5.text(
        f"Nodes: {len(colonization.nodes)} | Attractors: {len(colonization.attractors)}",
        10,
        20,
    )


def key_pressed():
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "space_colonization_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
