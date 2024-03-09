
# main.py

from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from OSRSGrandExchangeApp import OSRSGrandExchangeApp
import argparse
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def update_rl_parameters(agent, new_params):
    agent.epsilon = new_params.get('epsilon', agent.epsilon)
    agent.alpha = new_params.get('alpha', agent.alpha)
    agent.gamma = new_params.get('gamma', agent.gamma)
    logging.info('Updated RL parameters.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--window-size", nargs=2, type=int, default=[800, 600], help="Window size (width height)")
    parser.add_argument("--background-color", type=str, default="#1E1E1E", help="Background color (hex)")
    args = parser.parse_args()

    Window.clearcolor = get_color_from_hex(args.background_color)
    Window.size = (args.window_size[0], args.window_size[1])

    try:
        app = OSRSGrandExchangeApp()
        app.run()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)

