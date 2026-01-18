import config
import math
import csv
import os
from datetime import datetime

class BinanceExecutor:
    def __init__(self, exchange):
        self.exchange = exchange
        self.symbol = config.SYMBOL

    def get_balance(self, asset):
        """
        Returns the 'free' balance of an asset (e.g., 'USDT' or 'ETH')
        """
        try:
            # Force a reload of markets/balances to get fresh data
            self.exchange.load_markets()
            balance = self.exchange.fetch_balance()
            return float(balance[asset]['free'])
        except Exception as e:
            print(f"   ❌ Error fetching balance: {e}")
            return 0.0

    def log_trade(self, action, amount, price):
        """
        Saves trade details to 'trade_log.csv' so you can analyze performance later.
        """
        filename = 'trade_log.csv'
        file_exists = os.path.isfile(filename)
        
        try:
            with open(filename, 'a', newline='') as f:
                writer = csv.writer(f)
                
                # Write Header if this is a new file
                if not file_exists:
                    writer.writerow(['Timestamp', 'Action', 'Amount', 'Price', 'Total_Value_USDT'])
                
                # Write Trade Data
                total_value = amount * price
                writer.writerow([datetime.now(), action, amount, price, total_value])
                print(f"   📝 Trade logged to {filename}")
        except Exception as e:
            print(f"   ⚠️ Failed to log trade to CSV: {e}")

    def place_buy_order(self):
        """
        Buys ETH with ALL available USDT.
        """
        try:
            # 1. How much money do we have?
            usdt_balance = self.get_balance('USDT')
            
            if usdt_balance < 15: # Binance min trade is usually $10, we use $15 to be safe
                print(f"   ⚠️ Balance ({usdt_balance:.2f} USDT) too low to buy.")
                return None

            # 2. Calculate Amount (Price / Balance)
            ticker = self.exchange.fetch_ticker(self.symbol)
            current_price = ticker['last']
            
            # Buy 98% of balance (saving 2% for fees/slippage buffer)
            amount_to_spend = usdt_balance * 0.98
            amount_to_buy = amount_to_spend / current_price
            
            # 3. Precision Handling
            # Binance rejects orders like "0.123456789 ETH". We must chop decimals.
            # For ETH/USDT, usually 4 decimals.
            amount_to_buy = self.round_down(amount_to_buy, 4)
            
            # 4. Execute Market Order
            print(f"   🚀 PLACING BUY ORDER: {amount_to_buy:.4f} ETH at ~${current_price}")
            order = self.exchange.create_market_buy_order(self.symbol, amount_to_buy)
            print("   ✅ BUY Order Success!")
            
            # 5. Log the Trade
            self.log_trade('BUY', amount_to_buy, current_price)
            
            return order

        except Exception as e:
            print(f"   ❌ BUY Failed: {e}")
            return None

    def place_sell_order(self):
        """
        Sells ALL ETH for USDT.
        """
        try:
            # 1. How much ETH do we have?
            eth_balance = self.get_balance('ETH')
            
            if eth_balance < 0.005: # Minimal amount check (dust)
                print(f"   ⚠️ ETH Balance ({eth_balance:.4f}) too low to sell.")
                return None

            # 2. Fetch Price (Needed for logging)
            ticker = self.exchange.fetch_ticker(self.symbol)
            current_price = ticker['last']

            # 3. Precision Handling
            amount_to_sell = self.round_down(eth_balance, 4)

            # 4. Execute Market Order
            print(f"   📉 PLACING SELL ORDER: {amount_to_sell:.4f} ETH at ~${current_price}")
            order = self.exchange.create_market_sell_order(self.symbol, amount_to_sell)
            print("   ✅ SELL Order Success!")

            # 5. Log the Trade
            self.log_trade('SELL', amount_to_sell, current_price)

            return order

        except Exception as e:
            print(f"   ❌ SELL Failed: {e}")
            return None
            
    def round_down(self, n, decimals=0):
        multiplier = 10 ** decimals
        return math.floor(n * multiplier) / multiplier