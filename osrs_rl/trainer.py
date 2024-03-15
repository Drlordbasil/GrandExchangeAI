import numpy as np
from osrs_rl.agent import OSRSAgent
from osrs_rl.environment import OSRSEnvironment

class OSRSTrainer:
    def __init__(self, items_data):
        self.items_data = items_data
        self.state_size = 9
        self.action_size = 2
        self.agent = OSRSAgent(self.state_size, self.action_size)
        self.env = OSRSEnvironment(self.items_data)
        self.batch_size = 128
        self.episodes = 1000

    def train(self):
        for e in range(self.episodes):
            state = self.env.reset()
            state = np.reshape(state, [1, self.state_size])
            done = False
            while not done:
                action = self.agent.act(state)
                next_state, reward, done, _ = self.env.step(action)
                next_state = np.reshape(next_state, [1, self.state_size])
                self.agent.remember(state, action, reward, next_state, done)
                state = next_state
                if done:
                    print(f"Episode: {e + 1}/{self.episodes}, Profit: {self.env.cash}")
                    break
            if len(self.agent.memory) > self.batch_size:
                self.agent.replay(self.batch_size)
        self.agent.save("osrs_rl_model.h5")

    def evaluate(self):
        self.agent.load("osrs_rl_model.h5")
        state = self.env.reset()
        state = np.reshape(state, [1, self.state_size])
        done = False
        while not done:
            action = self.agent.act(state)
            next_state, _, done, _ = self.env.step(action)
            state = np.reshape(next_state, [1, self.state_size])
        print(f"Final Profit: {self.env.cash}")