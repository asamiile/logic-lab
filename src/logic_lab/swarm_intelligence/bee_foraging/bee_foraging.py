"""Bee Foraging Algorithm - Artificial Bee Colony (ABC) inspired swarm intelligence.

This module implements a simulation of bee colony behavior with three bee phases:
- Scout bees: explore the search space randomly
- Employed bees: exploit discovered food sources locally
- Onlooker bees: make decisions based on waggle dance information
"""

import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import py5


@dataclass
class FoodSite:
    """Represents a food source location and its characteristics."""

    x: float
    y: float
    nectar: float = 0.0  # Nectar richness [0, 1]
    trial_count: int = 0  # Unsuccessful trials without improvement
    best_nectar: float = 0.0  # Best nectar value found at this site

    def __post_init__(self):
        """Initialize best_nectar with current nectar value."""
        self.best_nectar = self.nectar


@dataclass
class Bee:
    """Represents an individual bee in the colony."""

    x: float
    y: float
    phase: str = "scout"  # "scout", "employed", "onlooker"
    site_index: int = -1  # Index of assigned food source (-1 for scout)
    energy: float = 1.0  # Energy level [0, 1]

    def __post_init__(self):
        """Validate phase value."""
        if self.phase not in ("scout", "employed", "onlooker"):
            raise ValueError(f"Invalid phase: {self.phase}")


class BeeColony:
    """Main bee colony simulation class with swarm intelligence behavior."""

    def __init__(
        self,
        hive_x: float = 500,
        hive_y: float = 500,
        num_bees: int = 30,
        num_scouts: int = 5,
        trial_limit: int = 100,
        step_size: float = 5.0,
        discovery_radius: float = 50.0,
        search_radius: float = 50.0,
        canvas_width: float = 1024,
        canvas_height: float = 768,
    ):
        """Initialize the bee colony.

        Args:
            hive_x: X coordinate of the hive
            hive_y: Y coordinate of the hive
            num_bees: Total number of bees
            num_scouts: Number of scout bees
            trial_limit: Max unsuccessful trials before abandoning site
            step_size: Distance scouts move per frame
            discovery_radius: Radius to discover food sources
            search_radius: Radius for employed bees to search around site
            canvas_width: Width of the canvas for boundary checking
            canvas_height: Height of the canvas for boundary checking
        """
        self.hive_x = hive_x
        self.hive_y = hive_y
        self.num_bees = num_bees
        self.num_scouts = num_scouts
        self.num_employed = (num_bees - num_scouts) // 2
        self.num_onlookers = num_bees - num_scouts - self.num_employed
        self.trial_limit = trial_limit
        self.step_size = step_size
        self.discovery_radius = discovery_radius
        self.search_radius = search_radius
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self.bees: list[Bee] = []
        self.sites: list[FoodSite] = []
        self.debug_mode = False
        self.paused = False
        self.frame_count = 0

        self._init_bees()
        self._init_sites()

    def _init_bees(self) -> None:
        """Initialize bee population."""
        self.bees = []

        # Scout bees
        for _ in range(self.num_scouts):
            self.bees.append(
                Bee(
                    x=self.hive_x + random.uniform(-20, 20),
                    y=self.hive_y + random.uniform(-20, 20),
                    phase="scout",
                    site_index=-1,
                )
            )

        # Employed bees
        for _ in range(self.num_employed):
            self.bees.append(
                Bee(
                    x=self.hive_x + random.uniform(-20, 20),
                    y=self.hive_y + random.uniform(-20, 20),
                    phase="employed",
                    site_index=-1,
                )
            )

        # Onlooker bees
        for _ in range(self.num_onlookers):
            self.bees.append(
                Bee(
                    x=self.hive_x + random.uniform(-20, 20),
                    y=self.hive_y + random.uniform(-20, 20),
                    phase="onlooker",
                    site_index=-1,
                )
            )

    def _init_sites(self) -> None:
        """Initialize food sources."""
        self.sites = []
        # Create initial food sources distributed across search space
        num_initial_sites = max(2, self.num_employed // 3)
        for _ in range(num_initial_sites):
            self.sites.append(
                FoodSite(
                    x=random.uniform(50, self.canvas_width - 50),
                    y=random.uniform(50, self.canvas_height - 50),
                    nectar=random.uniform(0.3, 1.0),
                )
            )

    def reset(self) -> None:
        """Reset the colony to initial state."""
        self._init_bees()
        self._init_sites()
        self.frame_count = 0

    def _calculate_nectar_at_location(self, x: float, y: float) -> float:
        """Calculate nectar value at a given location (fitness function).

        Uses a simple Gaussian-like multi-peak landscape.
        """
        # Create artificial peaks across the canvas
        peaks = [
            (150, 150, 0.8),
            (self.canvas_width - 150, 150, 0.9),
            (150, self.canvas_height - 150, 0.85),
            (self.canvas_width - 150, self.canvas_height - 150, 0.95),
            (self.canvas_width / 2, self.canvas_height / 2, 0.7),
        ]

        max_nectar = 0.1  # Base nectar value
        for peak_x, peak_y, peak_value in peaks:
            dist = math.sqrt((x - peak_x) ** 2 + (y - peak_y) ** 2)
            nectar_from_peak = peak_value * math.exp(-(dist**2) / 10000)
            max_nectar = max(max_nectar, nectar_from_peak)

        return max_nectar

    def _find_nearby_site(self, x: float, y: float) -> int | None:
        """Find a food site within discovery radius.

        Args:
            x: X coordinate to search from
            y: Y coordinate to search from

        Returns:
            Index of discovered site, or None if no site nearby
        """
        for i, site in enumerate(self.sites):
            dist = math.sqrt((site.x - x) ** 2 + (site.y - y) ** 2)
            if dist < self.discovery_radius:
                return i
        return None

    def _update_scout_phase(self) -> None:
        """Update scout bees - random walk exploration."""
        for bee in self.bees:
            if bee.phase != "scout":
                continue

            # Random walk
            angle = random.uniform(0, 2 * math.pi)
            bee.x += self.step_size * math.cos(angle)
            bee.y += self.step_size * math.sin(angle)

            # Wrap around canvas
            bee.x = bee.x % self.canvas_width
            bee.y = bee.y % self.canvas_height

            # Try to discover food source
            site_idx = self._find_nearby_site(bee.x, bee.y)
            if site_idx is not None:
                # Switch to employed bee
                bee.phase = "employed"
                bee.site_index = site_idx
            else:
                # Check if we should create new site
                if random.random() < 0.01:  # Low probability of remembering location
                    nectar = self._calculate_nectar_at_location(bee.x, bee.y)
                    if nectar > 0.3:
                        self.sites.append(FoodSite(x=bee.x, y=bee.y, nectar=nectar))
                        bee.phase = "employed"
                        bee.site_index = len(self.sites) - 1

    def _update_employed_phase(self) -> None:
        """Update employed bees - local exploitation of food sources."""
        for bee in self.bees:
            if bee.phase != "employed" or bee.site_index < 0:
                continue

            if bee.site_index >= len(self.sites):
                bee.phase = "scout"
                bee.site_index = -1
                continue

            site = self.sites[bee.site_index]

            # Local search around food site
            neighbor_x = site.x + random.uniform(-self.search_radius, self.search_radius)
            neighbor_y = site.y + random.uniform(-self.search_radius, self.search_radius)

            # Clamp to canvas
            neighbor_x = max(0, min(neighbor_x, self.canvas_width))
            neighbor_y = max(0, min(neighbor_y, self.canvas_height))

            # Evaluate neighborhood
            nectar = self._calculate_nectar_at_location(neighbor_x, neighbor_y)

            if nectar > site.best_nectar:
                # Better site found
                site.x = neighbor_x
                site.y = neighbor_y
                site.nectar = nectar
                site.best_nectar = nectar
                site.trial_count = 0
            else:
                site.trial_count += 1

            # If limit exceeded, abandon site
            if site.trial_count > self.trial_limit:
                bee.phase = "scout"
                bee.site_index = -1

    def _calculate_selection_probability(self) -> list[float]:
        """Calculate probability of each site being selected by onlooker.

        Higher nectar sites have higher probability.
        """
        if not self.sites:
            return []

        # Normalize nectar values to [0, 1]
        max_nectar = max((s.nectar for s in self.sites), default=1.0)
        if max_nectar <= 0:
            max_nectar = 1.0

        probabilities = [s.nectar / max_nectar for s in self.sites]
        total = sum(probabilities)

        if total > 0:
            probabilities = [p / total for p in probabilities]
        else:
            probabilities = [1.0 / len(self.sites)] * len(self.sites)

        return probabilities

    def _update_onlooker_phase(self) -> None:
        """Update onlooker bees - waggle dance based decision making."""
        if not self.sites:
            return

        probabilities = self._calculate_selection_probability()

        for bee in self.bees:
            if bee.phase != "onlooker":
                continue

            # Decide on site based on nectar probabilities
            if random.random() < 0.3:  # 30% chance to engage with waggle dance
                site_idx = random.choices(range(len(self.sites)), weights=probabilities)[0]
                bee.phase = "employed"
                bee.site_index = site_idx
            else:
                # Continue as onlooker or become scout
                if random.random() < 0.05:
                    bee.phase = "scout"
                    bee.site_index = -1

    def _phase_transitions(self) -> None:
        """Handle phase transitions and bee assignments."""
        # Transition back from employed to onlooker with low probability
        for bee in self.bees:
            if bee.phase == "employed" and random.random() < 0.02:
                bee.phase = "onlooker"
                bee.site_index = -1

    def update(self) -> None:
        """Update colony state for one frame."""
        if self.paused:
            return

        self.frame_count += 1

        # Remove exhausted sites
        self.sites = [s for s in self.sites if s.trial_count <= self.trial_limit * 2]

        self._update_scout_phase()
        self._update_employed_phase()
        self._update_onlooker_phase()
        self._phase_transitions()

    def render(self) -> None:
        """Render the colony visualization."""
        # Background
        py5.background(255)

        # Draw hive
        py5.fill(0)
        py5.stroke_weight(0)
        py5.circle(self.hive_x, self.hive_y, 10)

        # Draw food sites
        for site in self.sites:
            # Color based on nectar level (yellow to gold)
            hue = 45  # Yellow range
            saturation = 100
            brightness = 50 + int(50 * site.nectar)
            py5.color_mode(py5.HSB)
            py5.fill(hue, saturation, brightness)
            py5.color_mode(py5.RGB)
            py5.stroke_weight(2)
            py5.stroke(200, 180, 0)
            py5.circle(site.x, site.y, 8 + int(5 * site.nectar))

            # Draw trial count if debug mode
            if self.debug_mode:
                py5.fill(0)
                py5.text_size(10)
                py5.text(str(site.trial_count), site.x + 5, site.y - 5)

        # Draw bees
        for bee in self.bees:
            # Color by phase
            if bee.phase == "scout":
                py5.fill(255, 100, 100)  # Red
            elif bee.phase == "employed":
                py5.fill(100, 150, 255)  # Blue
            else:  # onlooker
                py5.fill(100, 255, 100)  # Green

            py5.stroke_weight(0)
            py5.circle(bee.x, bee.y, 3)

        # Draw status text
        py5.fill(0)
        py5.text_size(12)
        status = f"Bees: {len(self.bees)} | Sites: {len(self.sites)} | Frame: {self.frame_count}"
        if self.paused:
            status += " | PAUSED"
        if self.debug_mode:
            status += " | DEBUG"
        py5.text(status, 10, 20)

        # Draw phase distribution
        scout_count = sum(1 for b in self.bees if b.phase == "scout")
        employed_count = sum(1 for b in self.bees if b.phase == "employed")
        onlooker_count = sum(1 for b in self.bees if b.phase == "onlooker")
        py5.text(
            f"Scout: {scout_count} | Employed: {employed_count} | Onlooker: {onlooker_count}",
            10,
            35,
        )

    def toggle_debug(self) -> None:
        """Toggle debug mode."""
        self.debug_mode = not self.debug_mode

    def toggle_pause(self) -> None:
        """Toggle pause/resume."""
        self.paused = not self.paused


# Global colony instance
colony: BeeColony | None = None
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def setup() -> None:
    """Initialize the py5 sketch."""
    global colony
    py5.size(1000, 1000)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    colony = BeeColony()


def draw() -> None:
    """Main draw loop."""
    if colony is None:
        return

    colony.update()
    colony.render()


def key_pressed() -> None:
    """Handle keyboard input."""
    if colony is None:
        return

    key = py5.key
    if key == "r":
        colony.reset()
    elif key == "s":
        # Take screenshot
        filename = SCREENSHOT_DIR / f"bee_colony_{colony.frame_count:06d}.png"
        py5.save(str(filename))
        print(f"Screenshot saved: {filename}")
    elif key == "d":
        colony.toggle_debug()
    elif key == " ":
        colony.toggle_pause()


if __name__ == "__main__":
    py5.run_sketch(setup=setup, draw=draw, key_pressed=key_pressed)
