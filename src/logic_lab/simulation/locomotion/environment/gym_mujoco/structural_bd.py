"""
Behavioral Descriptors for locomotion controllers.

Since the robot body is fixed, behavioral descriptors are based on
controller behavior patterns (how it moves, not what shape it is).
"""

import os
import sys

import numpy as np

# Import from me_neat library
_parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
_lib_dir = os.path.join(_parent_dir, "shared", "libs")
if _lib_dir not in sys.path:
    sys.path.insert(0, _lib_dir)

from me_neat import LinerBehavioralDescriptor


class ForwardSpeed(LinerBehavioralDescriptor):
    """Behavioral descriptor: average forward velocity during episode."""

    def evaluate(self, behavior_data):
        """
        Args:
            behavior_data: dict with 'forward_speed' key (float)

        Returns:
            grid index for this behavior
        """
        forward_speed = behavior_data.get("forward_speed", 0.0)
        # Clamp to value range
        forward_speed = np.clip(forward_speed, self.value_range[0], self.value_range[1])
        index = self.get_index(forward_speed)
        return index


class LateralStability(LinerBehavioralDescriptor):
    """Behavioral descriptor: lateral movement symmetry (0 = perfectly straight, 1 = very unstable)."""

    def evaluate(self, behavior_data):
        """
        Args:
            behavior_data: dict with 'lateral_stability' key (0-1)

        Returns:
            grid index for this behavior
        """
        stability = behavior_data.get("lateral_stability", 0.5)
        stability = np.clip(stability, self.value_range[0], self.value_range[1])
        index = self.get_index(stability)
        return index


class BodyTilt(LinerBehavioralDescriptor):
    """Behavioral descriptor: average body pitch (forward tilt)."""

    def evaluate(self, behavior_data):
        """
        Args:
            behavior_data: dict with 'body_tilt' key (radians)

        Returns:
            grid index for this behavior
        """
        body_tilt = behavior_data.get("body_tilt", 0.0)
        body_tilt = np.clip(body_tilt, self.value_range[0], self.value_range[1])
        index = self.get_index(body_tilt)
        return index


class JointActivity(LinerBehavioralDescriptor):
    """Behavioral descriptor: average joint activity (how much joints are moving)."""

    def evaluate(self, behavior_data):
        """
        Args:
            behavior_data: dict with 'joint_activity' key (0-1)

        Returns:
            grid index for this behavior
        """
        activity = behavior_data.get("joint_activity", 0.5)
        activity = np.clip(activity, self.value_range[0], self.value_range[1])
        index = self.get_index(activity)
        return index


class StepFrequency(LinerBehavioralDescriptor):
    """Behavioral descriptor: locomotion cadence (steps per second)."""

    def evaluate(self, behavior_data):
        """
        Args:
            behavior_data: dict with 'step_frequency' key (Hz)

        Returns:
            grid index for this behavior
        """
        frequency = behavior_data.get("step_frequency", 1.0)
        frequency = np.clip(frequency, self.value_range[0], self.value_range[1])
        index = self.get_index(frequency)
        return index
