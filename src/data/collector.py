"""
File: src/
"""
import yfinance as yf
from typing_extensions import TypedDict

from datetime import datetime, timezone, timedelta

import sys
import os

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceEntry(TypedDict):
    id: str
    price: float
    time: datetime
    change_percent: float
    change: float

class DataCollector:
    def __init__(self, tickers_file: str = "tickers.txt"):
        self.tickers = self.read_tickers(tickers_file)
        self.yf = yf.Tickers(self.tickers)
        
    def read_tickers(self, tickers_file: str):
        """
        Reads from the tickers.txt file to create the yf.Tickers object
        """
        with open(tickers_file, 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    
    def run(self) -> None:
        """
        Runs the main loop to collect data
        """
        try:
            self.yf.live(message_handler=self.handle_message)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt; exiting program now...")
            
        
    def handle_message(self, message: str) -> None:
        """
        Handles a message from yf.Tickers.live. They come in the format:
        {
            id (str):               The ticker symbol
            price (float):          The price in $
            time (str):             The time in milliseconds (should convert to a %Y-%M-%d %H:%M:%S)
            change_percent (float): The change percent from the start of the day
            change (float):         The absolute change from the start of the day
        }
        """
        db_entry = PriceEntry(
            id=message["id"],
            price=message["price"],
            time=self._convert_str_to_datetime(message["time"]),
            change=message["change"],
            pct_change=message["change_percent"]
        )
        
        self.store_in_db(db_entry)
        
    def _convert_str_to_datetime(self, datetime_str):
        """Converts time in milliseconds (str) to %Y-%m-%d %H:%M:%S in PST"""
        pst = timezone(timedelta(hours=-8))
        return datetime.fromtimestamp(int(datetime_str)/1000, tz=pst).strftime("%Y-%m-%d %H:%M:%S")
        
    
    def store_in_db(self, entry: PriceEntry) -> None:
        """
        Stores the entry into a PostgreSQL server.
        """
        pass