# main.py

from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from OSRSGrandExchangeApp import OSRSGrandExchangeApp
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--window-size", nargs=2, type=int, default=[800, 600], help="Window size (width height)")
    parser.add_argument("--background-color", type=str, default="#1E1E1E", help="Background color (hex)")
    args = parser.parse_args()

    Window.clearcolor = get_color_from_hex(args.background_color)
    Window.size = (args.window_size[0], args.window_size[1])
    OSRSGrandExchangeApp().run()