from dataclasses import dataclass
from pathlib import Path

physarum: "Physarum | None" = None

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass
class Agent:
    x: float
    y: float
    vx: float
    vy: float
    pheromone_level: float = 1.0


class PhysarumNetwork:
    def __init__(self, width=800, height=800, num_agents=500, num_attractors=5):
        self.width = width
        self.height = height
        self.num_agents = num_agents
        self.num_attractors = num_attractors

        self.agents = self._create_agents()
        self.attractors = self._create_attractors()

        self.pheromone = np.zeros((height, width))
        self.deposit_rate = 1.0
        self.decay_rate = 0.95

    def _create_agents(self):
        agents = []
        for _ in range(self.num_agents):
            x = np.random.uniform(0, self.width)
            y = np.random.uniform(0, self.height)
            angle = np.random.uniform(0, 2 * np.pi)
            vx = np.cos(angle) * 2
            vy = np.sin(angle) * 2
            agents.append(Agent(x, y, vx, vy))
        return agents

    def _create_attractors(self):
        attractors = []
        for _ in range(self.num_attractors):
            x = np.random.uniform(100, self.width - 100)
            y = np.random.uniform(100, self.height - 100)
            attractors.append((x, y))
        return attractors

    def sense_pheromone(self, x, y, offset_angle=0.5):
        """Sense pheromone in front of agent"""
        sense_dist = 10
        angle = np.arctan2(y, x) + offset_angle

        sx = x + np.cos(angle) * sense_dist
        sy = y + np.sin(angle) * sense_dist

        sx = int(np.clip(sx, 0, self.width - 1))
        sy = int(np.clip(sy, 0, self.height - 1))

        return self.pheromone[sy, sx]

    def update(self):
        """Update agent positions and pheromones"""
        self.pheromone *= self.decay_rate

        for agent in self.agents:
            closest_attractor = None
            closest_dist = float("inf")

            for ax, ay in self.attractors:
                dist = np.sqrt((agent.x - ax) ** 2 + (agent.y - ay) ** 2)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_attractor = (ax, ay)

            if closest_attractor:
                ax, ay = closest_attractor
                dx = ax - agent.x
                dy = ay - agent.y
                length = np.sqrt(dx * dx + dy * dy)
                if length > 0:
                    agent.vx = (dx / length) * 2 + np.random.normal(0, 0.5)
                    agent.vy = (dy / length) * 2 + np.random.normal(0, 0.5)

            agent.x += agent.vx
            agent.y += agent.vy

            agent.x = (agent.x) % self.width
            agent.y = (agent.y) % self.height

            ix = int(np.clip(agent.x, 0, self.width - 1))
            iy = int(np.clip(agent.y, 0, self.height - 1))

            self.pheromone[iy, ix] = min(255, self.pheromone[iy, ix] + self.deposit_rate)

    def draw(self):
        py5.background(10)

        for y in range(0, self.height, 2):
            for x in range(0, self.width, 2):
                intensity = int(self.pheromone[y, x])
                py5.stroke(100 + intensity // 2)
                py5.point(x, y)

        for ax, ay in self.attractors:
            py5.fill(255, 150, 0)
            py5.no_stroke()
            py5.circle(ax, ay, 8)

        py5.fill(255)
        py5.text_align(py5.LEFT)
        py5.text_size(10)
        py5.text(f"Agents: {len(self.agents)}", 10, 20)


def setup() -> None:
    py5.size(800, 800)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    global physarum
    physarum = PhysarumNetwork(py5.width, py5.height, num_agents=400, num_attractors=4)


def draw() -> None:
    for _ in range(3):
        physarum.update()

    physarum.draw()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "physarum_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
