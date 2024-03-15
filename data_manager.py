import sqlite3

class DataManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Connected to the database: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")

    def disconnect(self):
        if self.conn:
            try:
                self.conn.close()
                print("Disconnected from the database.")
            except sqlite3.Error as e:
                print(f"Error disconnecting from the database: {e}")

    def create_tables(self):
        try:
            self.connect()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    high_price REAL,
                    high_volume INTEGER,
                    low_price REAL,
                    low_volume INTEGER,
                    avg_price_5m REAL,
                    potential_profit REAL,
                    price_fluctuation REAL,
                    buy_limit INTEGER,
                    roi REAL
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS prices (
                    id INTEGER PRIMARY KEY,
                    item_id INTEGER,
                    timestamp TEXT,
                    price REAL,
                    volume INTEGER,
                    FOREIGN KEY (item_id) REFERENCES items (id)
                )
            """)
            self.conn.commit()
            print("Tables created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
        finally:
            self.disconnect()

    def insert_item(self, item_data):
        try:
            self.connect()
            self.cursor.execute("""
                INSERT OR REPLACE INTO items (
                    id, name, high_price, high_volume, low_price, low_volume,
                    avg_price_5m, potential_profit, price_fluctuation, buy_limit, roi
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_data["Item ID"],
                item_data["Item Name"],
                item_data.get("high_price", 0),
                item_data.get("high_volume", 0),
                item_data.get("low_price", 0),
                item_data.get("low_volume", 0),
                item_data.get("avg_price_5m", 0),
                item_data.get("potential_profit", 0),
                item_data.get("price_fluctuation", 0),
                item_data.get("buy_limit", 0),
                item_data.get("roi", 0)
            ))
            self.conn.commit()
            print(f"Item inserted/updated successfully. Item ID: {item_data['Item ID']}")
        except sqlite3.Error as e:
            print(f"Error inserting/updating item: {e}")
        finally:
            self.disconnect()

    def insert_price(self, item_id, timestamp, price, volume):
        try:
            self.connect()
            self.cursor.execute("""
                INSERT INTO prices (item_id, timestamp, price, volume)
                VALUES (?, ?, ?, ?)
            """, (item_id, timestamp, price, volume))
            self.conn.commit()
            print(f"Price inserted successfully. Item ID: {item_id}")
        except sqlite3.Error as e:
            print(f"Error inserting price: {e}")
        finally:
            self.disconnect()

    def get_all_items(self):
        try:
            self.connect()
            self.cursor.execute("""
                SELECT * FROM items
            """)
            items = self.cursor.fetchall()
            print("All items retrieved successfully.")
            return items
        except sqlite3.Error as e:
            print(f"Error retrieving all items: {e}")
            return []
        finally:
            self.disconnect()

    def get_prices(self, item_id):
        try:
            self.connect()
            self.cursor.execute("""
                SELECT * FROM prices WHERE item_id = ?
            """, (item_id,))
            prices = self.cursor.fetchall()
            print(f"Prices retrieved successfully. Item ID: {item_id}")
            return prices
        except sqlite3.Error as e:
            print(f"Error retrieving prices: {e}")
            return []
        finally:
            self.disconnect()