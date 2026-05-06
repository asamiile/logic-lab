import gymnasium
import numpy as np


def _make_gymnasium_env(env_id: str, seed: int = 0) -> gymnasium.Env:
    """Create a gymnasium environment with specified seed."""
    env = gymnasium.make(env_id)
    env.reset(seed=seed)
    return env


class LocomotionControllerEvaluator:
    """Evaluate NEAT controllers on fixed robot body."""

    def __init__(self, env_id: str, num_eval: int = 1):
        """
        Args:
            env_id: gymnasium environment ID (e.g., 'Walker2d-v5')
            num_eval: number of independent episode evaluations per genome
        """
        self.env_id = env_id
        self.num_eval = num_eval

    def evaluate_controller(self, key, controller, generation):
        """
        Evaluate a NEAT controller on the environment.

        Args:
            key: unique genome ID (unused, required by parallel evaluator interface)
            controller: NEAT FeedForwardNetwork (has activate() method)
            generation: current generation number (unused, required by interface)

        Returns:
            dict with 'fitness' key containing mean episode reward
        """
        env = _make_gymnasium_env(self.env_id)

        episode_scores = []

        for eval_num in range(self.num_eval):
            obs, _ = env.reset()
            total_reward = 0.0
            steps = 0

            for step in range(1000):  # max episode length
                # NEAT network outputs are in [0, 1] (sigmoid)
                # Scale to [-1, 1] for continuous control
                action = np.array(controller.activate(obs)) * 2 - 1
                obs, reward, terminated, truncated, info = env.step(action)
                total_reward += reward
                steps += 1

                if terminated or truncated:
                    break

            episode_scores.append(total_reward)

        env.close()

        return {"fitness": float(np.mean(episode_scores))}


class LocomotionControllerEvaluatorNS:
    """Evaluate locomotion controllers with behavioral descriptor for novelty search."""

    def __init__(self, env_id: str, num_eval: int = 1):
        """
        Args:
            env_id: gymnasium environment ID (e.g., 'Walker2d-v5')
            num_eval: number of independent episode evaluations per genome
        """
        self.env_id = env_id
        self.num_eval = num_eval

    def evaluate_controller(self, key, controller, generation):
        """
        Evaluate a NEAT controller and compute behavioral descriptor.

        Args:
            key: unique genome ID (unused, required by parallel evaluator interface)
            controller: NEAT FeedForwardNetwork (has activate() method)
            generation: current generation number (unused, required by interface)

        Returns:
            dict with 'score' and 'data' keys for novelty search
        """
        env = _make_gymnasium_env(self.env_id)

        episode_scores = []
        all_obs_data = []
        all_act_data = []

        for eval_num in range(self.num_eval):
            obs, _ = env.reset()
            total_reward = 0.0
            obs_trajectory = []
            act_trajectory = []

            for step in range(1000):  # max episode length
                obs_trajectory.append(obs.copy())
                action = np.array(controller.activate(obs)) * 2 - 1
                act_trajectory.append(action.copy())
                obs, reward, terminated, truncated, info = env.step(action)
                total_reward += reward

                if terminated or truncated:
                    break

            episode_scores.append(total_reward)
            all_obs_data.extend(obs_trajectory)
            all_act_data.extend(act_trajectory)

        env.close()

        # Calculate behavioral descriptor from trajectory statistics
        obs_array = np.array(all_obs_data)
        act_array = np.array(all_act_data)

        # Covariance-based behavioral descriptor
        bd = self._calc_covariance_bd(obs_array, act_array)

        # Ensure score is Python float for neat-python type checking
        mean_score = float(np.mean(episode_scores))

        return {"score": mean_score, "data": bd}

    def _calc_covariance_bd(self, obs_array, act_array):
        """
        Calculate behavioral descriptor from observation and action trajectories.

        Descriptor is flattened covariance matrix of obs and act data.
        Dimension: obs_dim*(obs_dim+1)/2 + act_dim*(act_dim+1)/2

        Args:
            obs_array: (timesteps, obs_dim) array of observations
            act_array: (timesteps, act_dim) array of actions

        Returns:
            numpy array: flattened upper triangle of concatenated covariance matrix
        """
        if len(obs_array) < 2 or len(act_array) < 2:
            # Fallback if trajectory is too short
            obs_dim = obs_array.shape[1] if len(obs_array.shape) > 1 else 1
            act_dim = act_array.shape[1] if len(act_array.shape) > 1 else 1
            bd_size = obs_dim * (obs_dim + 1) // 2 + act_dim * (act_dim + 1) // 2
            return np.zeros(bd_size)

        # Stack obs and act data
        combined = np.hstack([obs_array, act_array])

        # Calculate covariance matrix
        try:
            cov_matrix = np.cov(combined.T)
        except:
            # Fallback on covariance calculation error
            obs_dim = obs_array.shape[1]
            act_dim = act_array.shape[1]
            bd_size = obs_dim * (obs_dim + 1) // 2 + act_dim * (act_dim + 1) // 2
            return np.zeros(bd_size)

        # Handle 1D case (single variable)
        if cov_matrix.ndim == 0:
            cov_matrix = np.array([[cov_matrix]])

        # Extract upper triangle (including diagonal)
        obs_dim = obs_array.shape[1]
        act_dim = act_array.shape[1]
        total_dim = obs_dim + act_dim

        # Get indices of upper triangle
        upper_tri_indices = np.triu_indices(total_dim)
        bd = cov_matrix[upper_tri_indices]

        # Replace any NaN or inf with 0
        bd = np.nan_to_num(bd, nan=0.0, posinf=0.0, neginf=0.0)

        # Keep as numpy array for distance metric calculations
        return bd


class LocomotionStructureEvaluator:
    """Evaluate locomotion controllers with structural behavior descriptors for MAP-Elites."""

    def __init__(self, env_id: str, bd_dictionary=None, num_eval: int = 1):
        """
        Args:
            env_id: gymnasium environment ID (e.g., 'Walker2d-v5')
            bd_dictionary: dict of behavioral descriptor objects for MAP-Elites grid computation
            num_eval: number of independent episode evaluations per genome
        """
        self.env_id = env_id
        self.bd_dictionary = bd_dictionary
        self.num_eval = num_eval

    def evaluate_controller(self, key, controller, generation):
        """
        Evaluate a NEAT controller and compute behavior descriptors for MAP-Elites.

        Args:
            key: unique genome ID (unused, required by parallel evaluator interface)
            controller: NEAT FeedForwardNetwork (has activate() method)
            generation: current generation number (unused, required by interface)

        Returns:
            dict with 'fitness' and 'behavior' keys for MAP-Elites
        """
        env = _make_gymnasium_env(self.env_id)

        episode_scores = []
        all_obs_data = []

        for eval_num in range(self.num_eval):
            obs, _ = env.reset()
            total_reward = 0.0
            obs_trajectory = []

            for step in range(1000):  # max episode length
                obs_trajectory.append(obs.copy())
                action = np.array(controller.activate(obs)) * 2 - 1
                obs, reward, terminated, truncated, info = env.step(action)
                total_reward += reward

                if terminated or truncated:
                    break

            episode_scores.append(total_reward)
            all_obs_data.extend(obs_trajectory)

        env.close()

        # Calculate behavior characteristics from observations
        obs_array = np.array(all_obs_data)
        behavior_dict = self._calc_behavior_characteristics(obs_array)

        # If BD dictionary provided, compute MAP-Elites grid indices
        if self.bd_dictionary is not None:
            bd_indices = {}
            for bd_name, bd_obj in self.bd_dictionary.items():
                bd_value = behavior_dict.get(bd_name, 0.0)
                bd_indices[bd_name] = bd_obj.get_index(bd_value)
            return {"fitness": float(np.mean(episode_scores)), "bd": bd_indices}
        else:
            return {"fitness": float(np.mean(episode_scores)), "behavior": behavior_dict}

    def _calc_behavior_characteristics(self, obs_array):
        """
        Calculate behavior characteristics from observation trajectory.

        Dispatches to environment-specific implementations based on env_id.

        Args:
            obs_array: (timesteps, obs_dim) array of observations

        Returns:
            dict with behavior characteristics
        """
        if "BipedalWalker" in self.env_id:
            return self._calc_behavior_characteristics_bipedal(obs_array)
        else:
            return self._calc_behavior_characteristics_walker2d(obs_array)

    def _calc_behavior_characteristics_walker2d(self, obs_array):
        """
        Calculate behavior characteristics for Walker2d-v5 (17-dim obs).

        Observations:
        - [0:2] - root position (x, y)
        - [2:4] - root velocity (vx, vy)
        - [4] - root angle (z-axis rotation)
        - [5] - root angular velocity
        - [6:14] - joint angles (8 joints)
        - [14:] - joint velocities (3 joints visible)
        """
        if len(obs_array) < 2:
            return {
                "forward_speed": 0.0,
                "lateral_stability": 0.5,
                "body_tilt": 0.0,
                "joint_activity": 0.0,
                "step_frequency": 0.0,
            }

        forward_speed = float(np.mean(obs_array[:, 2]))
        x_pos = obs_array[:, 0]
        x_displacement = x_pos[-1] - x_pos[0]
        y_pos = obs_array[:, 1]
        lateral_deviation = float(np.std(y_pos))
        lateral_stability = min(1.0, lateral_deviation / 0.5) if x_displacement > 0 else 0.5
        body_tilt = float(np.mean(obs_array[:, 4]))
        joint_angles = obs_array[:, 6:14]
        joint_angle_changes = np.abs(np.diff(joint_angles, axis=0))
        joint_activity = float(np.mean(joint_angle_changes))
        joint_activity = min(1.0, joint_activity / 0.5)

        if len(obs_array) > 50:
            joint_signal = obs_array[::5, 6]
            if len(joint_signal) > 10:
                mean_signal = joint_signal - np.mean(joint_signal)
                autocorr = np.correlate(mean_signal, mean_signal, mode="full")
                autocorr = autocorr[len(autocorr) // 2 :]
                peaks = []
                for i in range(1, len(autocorr) - 1):
                    if autocorr[i] > 0 and autocorr[i + 1] <= 0:
                        peaks.append(i)
                step_frequency = 30.0 / peaks[0] * 5 if len(peaks) > 0 and peaks[0] > 0 else 1.0
            else:
                step_frequency = 1.0
        else:
            step_frequency = 1.0

        forward_speed = float(np.clip(forward_speed, -2.0, 3.0))
        lateral_stability = float(np.clip(lateral_stability, 0.0, 1.0))
        body_tilt = float(np.clip(body_tilt, -np.pi / 2, np.pi / 2))
        joint_activity = float(np.clip(joint_activity, 0.0, 1.0))
        step_frequency = float(np.clip(step_frequency, 0.0, 5.0))

        return {
            "forward_speed": forward_speed,
            "lateral_stability": lateral_stability,
            "body_tilt": body_tilt,
            "joint_activity": joint_activity,
            "step_frequency": step_frequency,
        }

    def _calc_behavior_characteristics_bipedal(self, obs_array):
        """
        Calculate behavior characteristics for BipedalWalker-v3 (24-dim obs).

        Observations:
        - [0] - hull angle
        - [1] - hull angular velocity
        - [2] - horizontal velocity
        - [3] - vertical velocity
        - [4,6] - hip/knee joint 1 angles
        - [5,7] - hip/knee joint 1 speeds
        - [8] - leg 1 contact
        - [9,11] - hip/knee joint 2 angles
        - [10,12] - hip/knee joint 2 speeds
        - [13] - leg 2 contact
        - [14:24] - 10 lidar rangefinder readings
        """
        if len(obs_array) < 2:
            return {
                "forward_speed": 0.0,
                "lateral_stability": 0.5,
                "body_tilt": 0.0,
                "joint_activity": 0.0,
                "step_frequency": 0.0,
            }

        forward_speed = float(np.mean(obs_array[:, 2]))
        lateral_stability = 0.5 - float(np.std(obs_array[:, 1])) / 2.0
        lateral_stability = float(np.clip(lateral_stability, 0.0, 1.0))
        body_tilt = float(np.mean(obs_array[:, 0]))
        joint_angles = obs_array[:, [4, 6, 9, 11]]
        joint_angle_changes = np.abs(np.diff(joint_angles, axis=0))
        joint_activity = float(np.mean(joint_angle_changes))
        joint_activity = min(1.0, joint_activity / 0.5)

        if len(obs_array) > 50:
            joint_signal = obs_array[::5, 4]
            if len(joint_signal) > 10:
                mean_signal = joint_signal - np.mean(joint_signal)
                autocorr = np.correlate(mean_signal, mean_signal, mode="full")
                autocorr = autocorr[len(autocorr) // 2 :]
                peaks = []
                for i in range(1, len(autocorr) - 1):
                    if autocorr[i] > 0 and autocorr[i + 1] <= 0:
                        peaks.append(i)
                step_frequency = 30.0 / peaks[0] * 5 if len(peaks) > 0 and peaks[0] > 0 else 1.0
            else:
                step_frequency = 1.0
        else:
            step_frequency = 1.0

        forward_speed = float(np.clip(forward_speed, -2.0, 3.0))
        body_tilt = float(np.clip(body_tilt, -np.pi / 2, np.pi / 2))
        joint_activity = float(np.clip(joint_activity, 0.0, 1.0))
        step_frequency = float(np.clip(step_frequency, 0.0, 5.0))

        return {
            "forward_speed": forward_speed,
            "lateral_stability": lateral_stability,
            "body_tilt": body_tilt,
            "joint_activity": joint_activity,
            "step_frequency": step_frequency,
        }
