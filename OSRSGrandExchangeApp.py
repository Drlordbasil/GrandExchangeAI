import os
import pickle
from threading import Thread
from kivy.app import App
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from OSRSScraper import OSRSScraper
from utils import generate_item_suggestions, train_model, format_suggestions, save_model, load_model
from config import Config
from kivy.clock import Clock

class OSRSGrandExchangeApp(App):
    suggestions_text = StringProperty("")
    use_rl = BooleanProperty(False)

    def build(self):
        print("Building the app layout...")
        self.title = "OSRS Grand Exchange Helper"
        layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(20))
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

        self.progress_bar = ProgressBar(size_hint=(1, None), height=dp(10))
        layout.add_widget(self.progress_bar)

        self.root = layout
        return layout

    def create_header(self):
        print("Creating the app header...")
        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(60), padding=dp(10))
        app_icon = Label(text="[GE AI]", markup=True, font_size=dp(36))
        app_title = Label(text="OSRS Grand Exchange Helper", font_size=dp(24), bold=True, color=get_color_from_hex("#FFFFFF"))
        header.add_widget(app_icon)
        header.add_widget(app_title)
        return header

    def create_input_layout(self):
        print("Creating the input layout...")
        input_layout = BoxLayout(orientation="vertical", spacing=dp(5), size_hint=(1, None), height=dp(80))
        input_label = Label(text="Starting Gold:", size_hint=(1, None), height=dp(20), color=get_color_from_hex("#FFFFFF"))
        self.starting_gold_input = TextInput(text="100000000", multiline=False, size_hint=(1, None), height=dp(40), background_color=get_color_from_hex("#FFFFFF"), foreground_color=get_color_from_hex("#000000"), padding=[dp(10), dp(10), dp(10), dp(10)])
        self.starting_gold_error = Label(text="", size_hint=(1, None), height=dp(20), color=get_color_from_hex("#FF0000"))
        input_layout.add_widget(input_label)
        input_layout.add_widget(self.starting_gold_input)
        input_layout.add_widget(self.starting_gold_error)
        return input_layout

    def create_rl_layout(self):
        print("Creating the RL layout...")
        rl_layout = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(1, None), height=dp(40))
        rl_label = Label(text="Use Reinforcement Learning:", size_hint=(0.7, None), height=dp(40), color=get_color_from_hex("#FFFFFF"))
        self.use_rl_switch = Switch(active=self.use_rl, size_hint=(0.3, None), height=dp(40))
        self.use_rl_switch.bind(active=self.on_use_rl_switch)
        rl_layout.add_widget(rl_label)
        rl_layout.add_widget(self.use_rl_switch)
        return rl_layout

    def create_button_layout(self):
        print("Creating the button layout...")
        button_layout = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(1, None), height=dp(60))
        self.fetch_button = Button(text="[icon]Fetch Prices", size_hint=(0.5, None), height=dp(60), background_color=get_color_from_hex("#4CAF50"), color=get_color_from_hex("#FFFFFF"), bold=True)
        self.fetch_button.bind(on_press=self.fetch_prices_and_generate_suggestions)
        self.train_button = Button(text="[icon]Train Model", size_hint=(0.5, None), height=dp(60), background_color=get_color_from_hex("#2196F3"), color=get_color_from_hex("#FFFFFF"), bold=True)
        self.train_button.bind(on_press=self.train_model)
        button_layout.add_widget(self.fetch_button)
        button_layout.add_widget(self.train_button)
        return button_layout

    def create_scroll_view(self):
        print("Creating the scroll view...")
        scroll_view = ScrollView(size_hint=(1, 1), bar_width=dp(10), bar_color=get_color_from_hex("#FFFFFF"), bar_inactive_color=get_color_from_hex("#FFFFFF"))
        scroll_layout = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter("height"))

        suggestions_title = Label(text="Item Suggestions:", size_hint=(1, None), height=dp(40), color=get_color_from_hex("#FFFFFF"), font_size=dp(20), bold=True)
        self.suggestions_label = Label(text="", size_hint_y=None, color=get_color_from_hex("#FFFFFF"), font_name="RobotoMono-Regular", font_size=dp(14), padding=[dp(10), dp(10), dp(10), dp(10)])
        self.suggestions_label.bind(texture_size=self._update_suggestions_label_height)

        scroll_layout.add_widget(suggestions_title)
        scroll_layout.add_widget(self.suggestions_label)

        scroll_view.add_widget(scroll_layout)
        return scroll_view

    def on_use_rl_switch(self, instance, value):
        print(f"RL switch toggled: {value}")
        self.use_rl = value

    def fetch_prices_and_generate_suggestions(self, instance):
        print("Fetch Prices button clicked.")
        self.fetch_button.disabled = True
        self.train_button.disabled = True
        self.progress_bar.value = 0
        starting_gold = self.validate_starting_gold()
        if starting_gold is not None:
            print(f"Starting gold: {starting_gold}")
            thread = Thread(target=self.fetch_prices_and_generate_suggestions_thread, args=(starting_gold,))
            thread.start()
        else:
            print("Invalid starting gold value.")
            self.starting_gold_error.text = "Invalid starting gold value. Please enter a valid integer."
            self.fetch_button.disabled = False
            self.train_button.disabled = False
    def fetch_prices_and_generate_suggestions_thread(self, starting_gold):
        try:
            print("Fetching item prices...")
            scraper = OSRSScraper(Config)
            try:
                items_data = scraper.scrape_data()
                self.progress_bar.value = 50
            except Exception as e:
                print(f"Error fetching item data: {e}")
                self.show_error_popup("An error occurred while fetching item data.")
                return

            if items_data is not None and len(items_data) > 0:
                print("Generating item suggestions...")
                model_file = "model.pkl"
                if os.path.exists(model_file):
                    model = load_model(model_file)
                    if model is None:
                        print("Failed to load the model. Using default suggestions.")
                else:
                    print("Model file not found. Using default suggestions.")
                    model = None

                suggestions = generate_item_suggestions(items_data, starting_gold, model)
                self.progress_bar.value = 80

                if suggestions:
                    print("Item suggestions generated.")
                    self.suggestions_text = f"Item Suggestions:\n{format_suggestions(suggestions)}"
                    if model is not None:
                        save_model(model, model_file)
                else:
                    print("No item suggestions found.")
                    self.suggestions_text = "No item suggestions found. Please check the input data and model."
            else:
                print("Error fetching item prices or item mapping.")
                self.suggestions_text = "Error fetching item prices or item mapping."
        except Exception as e:
            print(f"Error in fetch_prices_and_generate_suggestions_thread: {e}")
            self.show_error_popup("An error occurred while generating suggestions.")
        finally:
            self.progress_bar.value = 100
            self.fetch_button.disabled = False
            self.train_button.disabled = False
    def train_model(self, instance):
        print("Train Model button clicked.")
        self.fetch_button.disabled = True
        self.train_button.disabled = True
        self.progress_bar.value = 0
        thread = Thread(target=self.train_model_thread)
        thread.start()

    def train_model_thread(self):
        try:
            print("Fetching item data for training...")
            scraper = OSRSScraper(Config)
            try:
                items_data = scraper.scrape_data()
                self.progress_bar.value = 50
            except Exception as e:
                print(f"Error fetching item data: {e}")
                self.show_error_popup("An error occurred while fetching item data.")
                return

            if items_data is not None and len(items_data) > 0:
                print("Training the model...")
                model_file = "model.pkl"
                if self.use_rl:
                    # Train the reinforcement learning model
                    from osrs_rl.trainer import OSRSTrainer
                    trainer = OSRSTrainer(items_data)
                    trainer.train()
                    model = trainer.agent
                else:
                    # Train the normal model
                    model = train_model(items_data, epochs=20)

                self.progress_bar.value = 80
                with open(model_file, "wb") as file:
                    pickle.dump(model, file)
                print("Model training completed.")
                self.suggestions_text = "Model training completed. The trained model has been saved."
            else:
                print("Error fetching item prices or item mapping.")
                self.suggestions_text = "Error fetching item prices or item mapping. Please check the data source."
        except Exception as e:
            print(f"Error in train_model_thread: {e}")
            self.show_error_popup("An error occurred while training the model.")
        finally:
            self.progress_bar.value = 100
            self.fetch_button.disabled = False
            self.train_button.disabled = False

    def validate_starting_gold(self):
        print("Validating starting gold input...")
        try:
            starting_gold = int(self.starting_gold_input.text)
            if starting_gold > 0:
                self.starting_gold_error.text = ""
                return starting_gold
            else:
                self.starting_gold_error.text = "Starting gold must be a positive integer."
                return None
        except ValueError:
            self.starting_gold_error.text = "Invalid starting gold value. Please enter a valid integer."
            return None

    def show_error_popup(self, message):
        def show_popup(_):
            error_popup = Popup(title="Error", size_hint=(0.8, 0.4))
            error_label = Label(text=message)
            error_popup.add_widget(error_label)
            error_popup.open()

        Clock.schedule_once(show_popup, 0)

    def _update_layout(self, instance, size):
        print("Updating layout size...")
        instance.padding = (dp(20), dp(20), dp(20), dp(20))

    def _update_suggestions_label_height(self, instance, texture_size):
        print("Updating suggestions label height...")
        instance.height = texture_size[1] + dp(20)

    def on_suggestions_text(self, instance, value):
        print("Updating suggestions text...")
        self.suggestions_label.text = value