import gymnasium


def make_gymnasium_env(env_id: str, seed: int = 0) -> gymnasium.Env:
    """Create a gymnasium environment with specified seed."""
    env = gymnasium.make(env_id)
    env.reset(seed=seed)
    return env


def get_env_dims(env_id: str) -> tuple:
    """Get observation and action dimensions for an environment."""
    env = make_gymnasium_env(env_id)
    obs_dim = env.observation_space.shape[0]
    act_dim = env.action_space.shape[0]
    env.close()
    return (obs_dim, act_dim)
