from kivy.properties import StringProperty, BooleanProperty
from kivy.core.clipboard import Clipboard
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.scrollview import ScrollView
from kivy.app import App
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from threading import Thread
import os
import pickle
from sklearn.ensemble import RandomForestRegressor
from OSRSScraper import OSRSScraper
from utils import generate_item_suggestions, prepare_training_data, format_suggestions, train_model
from config import Config
from osrs_rl.agent import OSRSAgent
from osrs_rl.environment import OSRSEnvironment
from osrs_rl.trainer import OSRSTrainer
from feature_engineer import FeatureEngineer

class OSRSGrandExchangeApp(App):
    suggestions_text = StringProperty("")
    use_rl = BooleanProperty(False)

    def build(self):
        self.title = "OSRS Grand Exchange Helper"
        layout = BoxLayout(orientation="vertical", spacing=10, padding=20)
        layout.bind(size=self._update_layout)

        header = self.create_header()
        layout.add_widget(header)

        input_layout = self.create_input_layout()
        layout.add_widget(input_layout)

        rl_layout = self.create_rl_layout()
        layout.add_widget(rl_layout)

        button_layout = self.create_button_layout()
        layout.add_widget(button_layout)

        scroll_view = self.create_scroll_view()
        layout.add_widget(scroll_view)

        self.root = layout
        return layout

    def create_header(self):
        header = Label(text="OSRS Grand Exchange Helper", size_hint=(1, None), height=50, font_size=24, bold=True, color=get_color_from_hex("#FFFFFF"))
        header.bind(size=self._update_widget_size)
        return header

    def create_input_layout(self):
        input_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, None), height=40)
        self.starting_gold_input = TextInput(text="100000000", multiline=False, size_hint=(0.7, None), height=40, background_color=get_color_from_hex("#FFFFFF"), foreground_color=get_color_from_hex("#000000"))
        input_layout.add_widget(Label(text="Starting Gold:", size_hint=(0.3, None), height=40, color=get_color_from_hex("#FFFFFF")))
        input_layout.add_widget(self.starting_gold_input)
        return input_layout

    def create_rl_layout(self):
        rl_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, None), height=40)
        self.use_rl_switch = Switch(active=self.use_rl, size_hint=(0.3, None), height=40)
        self.use_rl_switch.bind(active=self.on_use_rl_switch)
        rl_layout.add_widget(Label(text="Use RL:", size_hint=(0.3, None), height=40, color=get_color_from_hex("#FFFFFF")))
        rl_layout.add_widget(self.use_rl_switch)
        return rl_layout

    def create_button_layout(self):
        button_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, None), height=50)
        self.fetch_button = Button(text="Fetch Prices and Generate Suggestions", size_hint=(0.7, None), height=50, background_color=get_color_from_hex("#4CAF50"), color=get_color_from_hex("#FFFFFF"), bold=True)
        self.fetch_button.bind(on_press=self.fetch_prices_and_generate_suggestions)
        self.train_button = Button(text="Train Model", size_hint=(0.3, None), height=50, background_color=get_color_from_hex("#2196F3"), color=get_color_from_hex("#FFFFFF"), bold=True)
        self.train_button.bind(on_press=self.train_model)
        self.copy_button = Button(text="Copy to Clipboard", size_hint=(0.3, None), height=50, background_color=get_color_from_hex("#FFC107"), color=get_color_from_hex("#FFFFFF"), bold=True)
        self.copy_button.bind(on_press=self.copy_to_clipboard)
        button_layout.add_widget(self.fetch_button)
        button_layout.add_widget(self.train_button)
        button_layout.add_widget(self.copy_button)
        return button_layout

    def create_scroll_view(self):
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_layout = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter("height"))

        self.suggestions_label = Label(text="Item Suggestions:", size_hint_y=None, height=400, color=get_color_from_hex("#FFFFFF"), text_size=(Window.width - 40, None), halign="left", valign="top")
        scroll_layout.add_widget(self.suggestions_label)

        scroll_view.add_widget(scroll_layout)
        return scroll_view

    def on_use_rl_switch(self, instance, value):
        self.use_rl = value

    def fetch_prices_and_generate_suggestions(self, instance):
        self.fetch_button.disabled = True
        starting_gold = self.validate_starting_gold()
        if starting_gold is not None:
            thread = Thread(target=self.fetch_prices_and_generate_suggestions_thread, args=(starting_gold,))
            thread.start()
        else:
            self.suggestions_text = "Invalid starting gold value. Please enter a valid integer."
            self.fetch_button.disabled = False

    def fetch_prices_and_generate_suggestions_thread(self, starting_gold):
        try:
            scraper = OSRSScraper(Config)
            items_data = scraper.scrape_data()
            if items_data is not None and len(items_data) > 0:
                model_file = "model.pkl"
                if os.path.exists(model_file):
                    with open(model_file, "rb") as file:
                        model = pickle.load(file)
                else:
                    model = RandomForestRegressor(n_estimators=100, random_state=42)

                suggestions = generate_item_suggestions(items_data, starting_gold, model)

                if suggestions:
                    self.suggestions_text = f"Item Suggestions:\n{format_suggestions(suggestions)}"
                else:
                    self.suggestions_text = "No item suggestions found."
            else:
                self.suggestions_text = "Error fetching item prices or item mapping."
        except Exception as e:
            print(f"Error in fetch_prices_and_generate_suggestions_thread: {e}")
            self.suggestions_text = "An error occurred while generating suggestions."
        finally:
            self.fetch_button.disabled = False

    def train_model_thread(self):
        try:
            scraper = OSRSScraper(Config)
            items_data = scraper.scrape_data()
            if items_data is not None and len(items_data) > 0:
                model = train_model(items_data)
                self.suggestions_text = "Model training completed."
            else:
                self.suggestions_text = "Error fetching item prices or item mapping."
        except Exception as e:
            print(f"Error in train_model_thread: {e}")
            self.suggestions_text = "An error occurred while training the model."
        finally:
            self.train_button.disabled = False

    def train_model(self, instance):
        self.train_button.disabled = True
        thread = Thread(target=self.train_model_thread)
        thread.start()

    def copy_to_clipboard(self, instance):
        text_to_copy = f"Item Suggestions:\n{self.suggestions_text}"
        Clipboard.copy(text_to_copy)

    def validate_starting_gold(self):
        try:
            starting_gold = int(self.starting_gold_input.text)
            if starting_gold > 0:
                return starting_gold
            else:
                return None
        except ValueError:
            return None

    def _update_layout(self, instance, size):
        instance.padding = (20, 20, 20, 20)

    def _update_widget_size(self, instance, size):
        instance.size_hint_y = None
        instance.height = size[1]

    def on_suggestions_text(self, instance, value):
        self.suggestions_label.text = value
        self.suggestions_label.texture_update()
        self.suggestions_label.height = self.suggestions_label.texture_size[1]