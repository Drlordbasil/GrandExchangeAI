# config.py

class Config:
    MIN_PROFIT = 3  # minimum profit margin in percentage
    MIN_FLUCTUATION = 0     # minimum fluctuation in percentage
    MIN_ROI = 0  #
    MIN_SELL_VOLUME = 100
    MIN_BUY_VOLUME = 100        
    MAX_TRANSACTIONS = 500  # maximum number of transactions per episode
    NUM_STATES = 2  # ROI, profit
    NUM_ACTIONS = 2 # buy, sell
    EPSILON = 0.3 # epsilon is the probability of choosing a random action
    ALPHA = 0.3 # alpha is a learning rate
    GAMMA = 0.9
    
