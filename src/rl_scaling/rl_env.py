import gymnasium as gym
import numpy as np
from ray.rllib.env.multi_agent_env import MultiAgentEnv
from gymnasium import spaces

class KubernetesScalingEnv(MultiAgentEnv):
    def __init__(self, config):
        self.max_pods = config.get("max_pods", 10)
        self.observation_space = spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32)
        self.action_space = spaces.Discrete(3)  # 0: Scale Down, 1: Scale Up, 2: Do Nothing
        self.current_pods = 1
        self.episode_length = 50  # Max steps per episode
        self.steps = 0  # Step counter

    def reset(self, *, seed=None, options=None):
        """Resets the environment and returns the initial observation."""
        self.current_pods = 1
        self.steps = 0
        obs = {"agent_0": np.random.rand(5)}
        infos = {"agent_0": {}}
        return obs, infos

    def step(self, action_dict):
        """Performs an action and updates the environment state."""
        action = action_dict["agent_0"]
        reward = 0

        # Perform Scaling Action
        if action == 0 and self.current_pods > 1:  # Scale Down
            self.current_pods -= 1
            reward = 2  # Encourage cost savings
        elif action == 1 and self.current_pods < self.max_pods:  # Scale Up
            self.current_pods += 1
            reward = -1  # Penalize cost increase

        # Simulated CPU Utilization
        cpu_utilization = np.random.uniform(0.2, 0.9)
        if cpu_utilization > 0.8:
            reward -= 2  # Penalize high CPU load

        # Update Environment
        obs = {"agent_0": np.random.rand(5)}
        rewards = {"agent_0": reward}

        self.steps += 1
        terminateds = {"agent_0": self.steps >= self.episode_length, "__all__": self.steps >= self.episode_length}
        truncateds = {"agent_0": False, "__all__": False}  # No early truncation
        infos = {"agent_0": {}}

        return obs, rewards, terminateds, truncateds, infos
