# osrs_rl/environment.py

class OSRSEnvironment:
    def __init__(self, config):
        self.config = config
        self.current_state = None
        self.current_item = None
        self.current_price = None
        self.current_volume = None
        self.current_profit = None
        self.total_profit = 0
        self.total_transactions = 0

    def reset(self):
        self.current_state = None
        self.current_item = None
        self.current_price = None
        self.current_volume = None
        self.current_profit = None
        self.total_profit = 0
        self.total_transactions = 0

    def step(self, action):
        # Perform the action and update the state
        if action == "buy":
            if self.current_item is not None and self.current_price is not None and self.current_volume is not None:
                transaction_cost = self.current_price * self.current_volume
                self.total_profit -= transaction_cost
                self.total_transactions += 1
                self.current_state = "holding"
            else:
                # Invalid action, no item or price available for buying
                self.current_state = "idle"
        elif action == "sell":
            if self.current_item is not None and self.current_price is not None and self.current_volume is not None:
                transaction_profit = self.current_price * self.current_volume
                self.total_profit += transaction_profit
                self.total_transactions += 1
                self.current_state = "idle"
            else:
                # Invalid action, no item or price available for selling
                self.current_state = "holding"
        else:
            # Invalid action
            self.current_state = self.current_state

        # Calculate the reward based on the action and state transition
        reward = 0
        if action == "buy" and self.current_state == "holding":
            reward = -1  # Negative reward for buying
        elif action == "sell" and self.current_state == "idle":
            reward = 1  # Positive reward for selling

        # Determine if the episode is done
        done = self.total_transactions >= self.config.MAX_TRANSACTIONS

        # Create an info dictionary for additional information
        info = {
            "total_profit": self.total_profit,
            "total_transactions": self.total_transactions
        }

        # Return the next_state, reward, done, and info
        return self.current_state, reward, done, info

    def render(self):
        # Provide a visualization of the environment
        print(f"Current State: {self.current_state}")
        print(f"Current Item: {self.current_item}")
        print(f"Current Price: {self.current_price}")
        print(f"Current Volume: {self.current_volume}")
        print(f"Current Profit: {self.current_profit}")
        print(f"Total Profit: {self.total_profit}")
        print(f"Total Transactions: {self.total_transactions}")
        print("---")