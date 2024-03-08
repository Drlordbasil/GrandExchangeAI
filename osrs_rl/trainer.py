# osrs_rl/trainer.py

class OSRSTrainer:
    def __init__(self, agent, environment):
        self.agent = agent
        self.environment = environment

    def train(self, num_episodes):
        for episode in range(num_episodes):
            state = self.environment.reset()
            done = False
            while not done:
                action = self.agent.choose_action(state)
                next_state, reward, done, info = self.environment.step(action)
                self.agent.update_q_table(state, action, reward, next_state)
                state = next_state
            print(f"Episode {episode + 1}: Total Profit = {info['total_profit']}, Total Transactions = {info['total_transactions']}")

    def evaluate(self, num_episodes):
        total_profit = 0
        total_transactions = 0
        for episode in range(num_episodes):
            state = self.environment.reset()
            done = False
            while not done:
                action = self.agent.predict(state)
                next_state, reward, done, info = self.environment.step(action)
                state = next_state
            total_profit += info['total_profit']
            total_transactions += info['total_transactions']
        average_profit = total_profit / num_episodes
        average_transactions = total_transactions / num_episodes
        print(f"Evaluation Results:")
        print(f"Average Profit per Episode: {average_profit}")
        print(f"Average Transactions per Episode: {average_transactions}")