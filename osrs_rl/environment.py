import numpy as np

class OSRSEnvironment:
    def __init__(self, items_data):
        self.items_data = items_data
        self.current_step = 0
        self.inventory = []
        self.cash = 0

    def reset(self):
        self.current_step = 0
        self.inventory = []
        self.cash = 0
        return self._get_state()

    def step(self, action):
        item = self.items_data[self.current_step]
        if action == 0:
            if self.cash >= item['low_price']:
                self.inventory.append(item)
                self.cash -= item['low_price']
        elif action == 1:
            if item in self.inventory:
                self.inventory.remove(item)
                self.cash += item['high_price']

        self.current_step += 1
        done = self.current_step >= len(self.items_data)
        reward = self._calculate_reward()
        next_state = self._get_state()

        return next_state, reward, done, {}

    def _get_state(self):
        state = [
            self.cash,
            len(self.inventory),
            self.items_data[self.current_step]['high_price'],
            self.items_data[self.current_step]['low_price'],
            self.items_data[self.current_step]['avg_price_5m'],
            self.items_data[self.current_step]['potential_profit'],
            self.items_data[self.current_step]['price_fluctuation'],
            self.items_data[self.current_step]['buy_limit'],
            self.items_data[self.current_step]['roi']
        ]
        return np.array(state)

    def _calculate_reward(self):
        reward = 0
        for item in self.inventory:
            reward += item['potential_profit']
        reward += self.cash
        return reward