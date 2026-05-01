from pathlib import Path
import math

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

creature: "Creature"
food: "Food"


class Sensor:
    def __init__(self, v: py5.Py5Vector) -> None:
        self.v = py5.Py5Vector(v.x, v.y)
        self.value = 0

    def sense(self, position: py5.Py5Vector, food: "Food") -> None:
        # Find the endpoint of the sensor
        end_x = position.x + self.v.x
        end_y = position.y + self.v.y

        # Distance from sensor endpoint to food center
        d = math.sqrt((end_x - food.position.x) ** 2 +
                      (end_y - food.position.y) ** 2)

        # If within food radius, activate the sensor
        if d < food.r:
            # Map distance: 0 (at center) -> 1, food.r (at edge) -> 0
            self.value = 1 - (d / food.r)
        else:
            self.value = 0


class Creature:
    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.position = py5.Py5Vector(x, y)
        self.r = 16
        self.sensors = []

        # Create 15 sensors arranged in a circle
        total_sensors = 15
        for i in range(total_sensors):
            angle = (i / total_sensors) * 2 * math.pi
            vx = math.cos(angle) * self.r * 2
            vy = math.sin(angle) * self.r * 2
            self.sensors.append(Sensor(py5.Py5Vector(vx, vy)))

    def sense(self, food: "Food") -> None:
        for sensor in self.sensors:
            sensor.sense(self.position, food)

    def show(self) -> None:
        py5.push()
        py5.translate(self.position.x, self.position.y)

        # Draw sensors
        for sensor in self.sensors:
            py5.stroke(0)
            py5.line(0, 0, sensor.v.x, sensor.v.y)

            # Light up sensor if detecting food
            if sensor.value > 0:
                py5.fill(255, int(sensor.value * 255))
                py5.stroke(0, 100)
                py5.circle(sensor.v.x, sensor.v.y, 8)

        # Draw creature body
        py5.no_stroke()
        py5.fill(0)
        py5.circle(0, 0, self.r * 2)

        py5.pop()


class Food:
    def __init__(self) -> None:
        self.position = py5.Py5Vector(py5.width / 2, py5.height / 2)
        self.r = 32

    def show(self) -> None:
        py5.no_stroke()
        py5.fill(0, 100)
        py5.circle(self.position.x, self.position.y, self.r * 2)


def setup() -> None:
    global creature, food
    py5.size(640, 240)
    creature = Creature()
    food = Food()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global creature

    py5.background(255)

    # Creature follows mouse
    creature.position.x = py5.mouse_x
    creature.position.y = py5.mouse_y

    food.show()
    creature.sense(food)
    creature.show()

    # Display instructions
    py5.fill(0)
    py5.text_size(12)
    py5.text("Move mouse to position creature", 10, py5.height - 10)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "creature_sensors_####.png"))


py5.run_sketch()
