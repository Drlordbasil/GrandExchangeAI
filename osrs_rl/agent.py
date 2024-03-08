# osrs_rl/agent.py

import numpy as np

class OSRSAgent:
    def __init__(self, config):
        self.config = config
        self.q_table = np.zeros((config.NUM_STATES, config.NUM_ACTIONS))
        self.epsilon = config.EPSILON
        self.alpha = config.ALPHA
        self.gamma = config.GAMMA

    def choose_action(self, state):
        if np.random.uniform(0, 1) < self.epsilon:
            # Explore: choose a random action
            action = np.random.choice(self.config.NUM_ACTIONS)
        else:
            # Exploit: choose the action with the highest Q-value for the current state
            action = np.argmax(self.q_table[state])
        return action

    def update_q_table(self, state, action, reward, next_state):
        old_value = self.q_table[state, action]
        next_max = np.max(self.q_table[next_state])
        
        new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_max)
        self.q_table[state, action] = new_value

    def train(self, env, num_episodes):
        for episode in range(num_episodes):
            state = env.reset()
            done = False
            while not done:
                action = self.choose_action(state)
                next_state, reward, done, _ = env.step(action)
                self.update_q_table(state, action, reward, next_state)
                state = next_state
                
    def predict(self, state):
        return np.argmax(self.q_table[state])