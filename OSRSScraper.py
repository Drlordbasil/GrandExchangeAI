# OSRSScraper.py

import requests
from datetime import datetime, timedelta
from data_manager import DataManager

class OSRSScraper:
    def __init__(self, config):
        self.config = config
        self.api_url_latest = "https://prices.runescape.wiki/api/v1/osrs/latest"
        self.api_url_5m = "https://prices.runescape.wiki/api/v1/osrs/5m"
        self.data_manager = DataManager("osrs_data.db")
        self.data_manager.create_tables()
        self.item_names = self.fetch_item_names()
        self.buy_limits = self.fetch_buy_limits()

    def fetch_data(self, api_url):
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            return response.json()['data']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {api_url}: {e}")
            return None

    def fetch_item_names(self):
        mapping_url = "https://prices.runescape.wiki/api/v1/osrs/mapping"
        try:
            response = requests.get(mapping_url)
            response.raise_for_status()
            mapping_data = response.json()
            for item in mapping_data:
                self.data_manager.insert_item(item['id'], item['name'], item.get('description', ''))
            return {str(item['id']): item['name'] for item in mapping_data}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching item names: {e}")
            return {}

    def fetch_buy_limits(self):
        buy_limits_url = "https://prices.runescape.wiki/api/v1/osrs/mapping"
        try:
            response = requests.get(buy_limits_url)
            response.raise_for_status()
            buy_limits_data = response.json()
            return {str(item['id']): item.get('limit', 0) for item in buy_limits_data}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching buy limits: {e}")
            return {}

    def scrape_data(self):
        data_latest = self.fetch_data(self.api_url_latest)
        data_5m = self.fetch_data(self.api_url_5m)
        items_data = []

        if data_latest and data_5m:
            for item_id, item_data_latest in data_latest.items():
                if item_id in data_5m:
                    item_data_5m = data_5m[item_id]
                    high_price = item_data_latest.get('high', 0)
                    low_price = item_data_latest.get('low', 0)
                    average_price_5m = item_data_5m.get('avgHighPrice', 0)
                    average_high_price = item_data_5m.get('avgHighPrice', 0)
                    average_low_price = item_data_5m.get('avgLowPrice', 0)
                    high_price_volume = item_data_5m.get('highPriceVolume', 0)
                    low_price_volume = item_data_5m.get('lowPriceVolume', 0)
                    buy_volume = low_price_volume
                    sell_volume = high_price_volume

                    high_price = average_high_price - average_high_price * 0.01 if average_high_price else 0
                    low_price = int(average_low_price * 0.99) if average_low_price else 0
                    average_price_5m = int(average_price_5m) if average_price_5m else 0

                    if high_price > 0 and low_price > 0:
                        potential_profit = high_price - low_price
                        profit_margin = (potential_profit / low_price) * 100

                        if average_price_5m > 0:
                            fluctuation = abs(high_price - average_price_5m) / average_price_5m
                            roi = potential_profit / average_price_5m

                            if (
                                profit_margin >= self.config.MIN_PROFIT
                                and fluctuation >= self.config.MIN_FLUCTUATION
                                and roi >= self.config.MIN_ROI
                                and sell_volume >= self.config.MIN_SELL_VOLUME
                                and buy_volume >= self.config.MIN_BUY_VOLUME
                            ):
                                item_name = self.item_names.get(item_id, "Unknown Item")
                                buy_limit = self.buy_limits.get(item_id, 0)
                                item_data = {
                                    "Item ID": item_id,
                                    "Item Name": item_name,
                                    "High (Sell)": high_price,
                                    "High Volume": high_price_volume,
                                    "Low (Buy)": low_price,
                                    "Low Volume": low_price_volume,
                                    "5-Minute Average High Price": average_price_5m,
                                    "ROI": roi,
                                    "Potential Profit": potential_profit,
                                    "Price Fluctuation": fluctuation * 100,
                                    "Buy Limit": buy_limit,
                                }
                                items_data.append(item_data)
        return items_data