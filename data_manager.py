# data_manager.py

import sqlite3

class DataManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        self.connect()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT
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
        self.disconnect()

    def insert_item(self, item_id, item_name, item_description):
        self.connect()
        self.cursor.execute("""
            INSERT OR REPLACE INTO items (id, name, description)
            VALUES (?, ?, ?)
        """, (item_id, item_name, item_description))
        self.conn.commit()
        self.disconnect()

    def insert_price(self, item_id, timestamp, price, volume):
        self.connect()
        self.cursor.execute("""
            INSERT INTO prices (item_id, timestamp, price, volume)
            VALUES (?, ?, ?, ?)
        """, (item_id, timestamp, price, volume))
        self.conn.commit()
        self.disconnect()

    def get_item(self, item_id):
        self.connect()
        self.cursor.execute("""
            SELECT * FROM items WHERE id = ?
        """, (item_id,))
        item = self.cursor.fetchone()
        self.disconnect()
        return item

    def get_prices(self, item_id):
        self.connect()
        self.cursor.execute("""
            SELECT * FROM prices WHERE item_id = ?
        """, (item_id,))
        prices = self.cursor.fetchall()
        self.disconnect()
        return prices