import requests
import time
from data_manager import DataManager


class OSRSScraper:
    def __init__(self, config):
        self.config = config
        self.api_url_latest = "https://prices.runescape.wiki/api/v1/osrs/latest"
        self.api_url_5m = "https://prices.runescape.wiki/api/v1/osrs/5m"
        self.data_manager = DataManager("osrs_data.db")
        self.data_manager.create_tables()
        self.item_mapping = self.fetch_item_mapping()

    def fetch_data(self, api_url, max_retries=3, retry_delay=5):
        retries = 0
        while retries < max_retries:
            try:
                print(f"Fetching data from {api_url}...")
                response = requests.get(api_url)
                response.raise_for_status()
                print(f"Data fetched successfully from {api_url}.")
                return response.json()['data']
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data from {api_url}: {e}")
                retries += 1
                if retries < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
            except (KeyError, ValueError) as e:
                print(f"Error parsing data from {api_url}: {e}")
                return None
        print(f"Max retries exceeded for {api_url}. Returning None.")
        return None

    def fetch_item_mapping(self):
        mapping_url = "https://prices.runescape.wiki/api/v1/osrs/mapping"
        try:
            print("Fetching item mapping...")
            response = requests.get(mapping_url)
            response.raise_for_status()
            mapping_data = response.json()
            print("Item mapping fetched successfully.")
            return {item['id']: item for item in mapping_data}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching item mapping: {e}")
            return {}

    def scrape_data(self):
        print("Scraping data...")
        data_latest = self.fetch_data(self.api_url_latest)
        data_5m = self.fetch_data(self.api_url_5m)
        items_data = []

        if data_latest is None or data_5m is None:
            print("Error fetching data from the API. Fetching data from the database.")
            items_data = self.data_manager.get_all_items()
        else:
            item_ids = set(data_latest.keys()) | set(data_5m.keys())  # Union of item IDs from both datasets

            for item_id in item_ids:
                item_data_latest = data_latest.get(item_id, {})
                item_data_5m = data_5m.get(item_id, {})

                item_mapping = self.item_mapping.get(int(item_id), {})
                high_price = item_data_latest.get('high', 0)
                low_price = item_data_latest.get('low', 0)
                average_price_5m = item_data_5m.get('avgHighPrice', 0)
                average_high_price = item_data_5m.get('avgHighPrice', 0)
                average_low_price = item_data_5m.get('avgLowPrice', 0)
                high_price_volume = item_data_5m.get('highPriceVolume', 0)
                low_price_volume = item_data_5m.get('lowPriceVolume', 0)

                high_price = int(average_high_price * 0.99) if average_high_price else 0
                low_price = int(average_low_price * 0.99) if average_low_price else 0
                average_price_5m = int(average_price_5m) if average_price_5m else 0

                if high_price > 0 and low_price > 0:
                    potential_profit = high_price * 0.99 - low_price
                    profit_margin = (potential_profit / low_price) * 100

                    if average_price_5m > 0:
                        fluctuation = abs(high_price - average_price_5m) / average_price_5m
                        roi = potential_profit / average_price_5m

                        item_name = item_mapping.get('name', "Unknown Item")
                        buy_limit = item_mapping.get('limit', 0)
                        item_data = {
                            "Item ID": item_id,
                            "Item Name": item_name,
                            "high_price": high_price,
                            "high_volume": high_price_volume,
                            "low_price": low_price,
                            "low_volume": low_price_volume,
                            "avg_price_5m": average_price_5m,
                            "potential_profit": potential_profit,
                            "price_fluctuation": fluctuation * 100,
                            "buy_limit": buy_limit,
                            "roi": roi
                        }
                        items_data.append(item_data)
                        self.save_item_data(item_data)

        print("Scraping completed.")
        return items_data
    def save_item_data(self, item_data):
        try:
            item_id = item_data["Item ID"]
            timestamp = int(time.time())
            price = item_data["high_price"]
            volume = item_data["high_volume"]

            self.data_manager.insert_item(item_data)
            self.data_manager.insert_price(item_id, timestamp, price, volume)
            print(f"Item data saved successfully. Item ID: {item_id}")
        except KeyError as e:
            print(f"Error saving item data: Missing key - {e}")
        except Exception as e:
            print(f"Error saving item data: {e}")