import gymnasium as gym
import numpy as np
from ray.rllib.env.multi_agent_env import MultiAgentEnv
from gymnasium import spaces

class KubernetesScalingEnv(MultiAgentEnv):
    """Multi-Agent Kubernetes Scaling Environment for RLlib"""

    def __init__(self, config=None):
        super().__init__()

        # Max number of pods allowed in the cluster
        self.max_pods = config.get("max_pods", 4) if config else 4  

        # Observation space: Simulated metrics (CPU, Memory, Network, Requests, Load)
        self.observation_space = spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32)

        # Action space: 0 = scale down, 1 = maintain, 2 = scale up
        self.action_space = spaces.Discrete(3)

        # Initial pod count
        self.current_pods = 1
        self.time_step = 0
        self.max_steps = 100  # Max steps per episode

    def reset(self, *, seed=None, options=None):
        """Resets the environment state"""
        super().reset(seed=seed)
        
        self.current_pods = 1  # Reset pods to minimum
        self.time_step = 0  # Reset step counter
        
        obs = {"agent_0": np.random.rand(5)}  # Random initial observation
        info = {}

        return obs, info

    def step(self, action_dict):
        """Executes an action and returns the next state, reward, and done signal"""

        action = action_dict.get("agent_0", 1)  # Default to maintain if action is missing
        reward = 0

        # Scale up/down logic
        if action == 0 and self.current_pods > 1:
            self.current_pods -= 1  # Scale down
            reward = 1  # Reward for reducing resources
        elif action == 2 and self.current_pods < self.max_pods:
            self.current_pods += 1  # Scale up
            reward = -1  # Penalize resource overuse

        # Simulate new observations
        obs = {"agent_0": np.random.rand(5)}

        # Update step count and check if episode should end
        self.time_step += 1
        done = {"agent_0": self.time_step >= self.max_steps, "__all__": self.time_step >= self.max_steps}

        # Empty info dictionary (can be used for debugging metrics)
        info = {}

        return obs, {"agent_0": reward}, done, info
