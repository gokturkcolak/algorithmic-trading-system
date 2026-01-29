import ccxt
import pandas as pd
import time
from datetime import datetime
import config
from strategy import MLStrategy

# -----------------------------------------------------------------------------
# 1. INITIALIZATION (Driven by config.py)
# -----------------------------------------------------------------------------
# Initialize Exchange using keys from config.py
exchange = ccxt.binance({
    'apiKey': config.API_KEY,
    'secret': config.SECRET_KEY,
    'enableRateLimit': True,
})

# Automatically switch modes based on config.py
if config.TESTNET:
    exchange.set_sandbox_mode(True) 
    # Note: ccxt handles the base URL for testnet automatically when sandbox is True

strategy = MLStrategy()

print(f"🚀 Bot initialized for {config.SYMBOL} on {config.TIMEFRAME}.")
print(f"🔧 Mode: {'⚠️ TESTNET' if config.TESTNET else '🚨 LIVE (REAL MONEY)'}")

# -----------------------------------------------------------------------------
# 2. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def fetch_data(symbol, timeframe, limit):
    try:
        # Uses the LIMIT from config.py
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"❌ Data Error: {e}")
        return None

def execute_trade(signal, current_price):
    try:
        balance = exchange.fetch_balance()
        usdt_free = balance['USDT']['free']
        eth_free = balance['ETH']['free']

        if signal == "BUY":
            # Uses a safe 20% position size
            amount_to_spend = usdt_free * 0.20
            
            if amount_to_spend < 10:
                print(f"⚠️ Balance too low to buy ({usdt_free:.2f} USDT).")
                return

            amount_coin = amount_to_spend / current_price
            print(f"💸 BUYING {amount_coin:.4f} ETH at {current_price}...")
            exchange.create_market_buy_order(config.SYMBOL, amount_coin)
            print("✅ BUY ORDER SENT")

        elif signal == "SELL":
            # Sell 100% of the coin
            value_of_coin = eth_free * current_price
            if value_of_coin < 10:
                print(f"⚠️ Not enough ETH to sell ({eth_free:.4f} ETH).")
                return

            print(f"💰 SELLING {eth_free:.4f} ETH at {current_price}...")
            exchange.create_market_sell_order(config.SYMBOL, eth_free)
            print("✅ SELL ORDER SENT")

    except Exception as e:
        print(f"❌ TRADE FAILED: {e}")

# -----------------------------------------------------------------------------
# 3. MAIN LOOP
# -----------------------------------------------------------------------------
def run_bot():
    print(f"⏳ Loop started. Checking every 60 seconds...")
    
    while True:
        try:
            # Uses settings from config.py
            df = fetch_data(config.SYMBOL, config.TIMEFRAME, config.LIMIT)
            
            if df is not None:
                # 1. Analyze
                signal = strategy.check_signal(df)
                
                # 2. Get Status
                bal = exchange.fetch_balance()
                usdt_total = bal['USDT']['total']
                current_price = df['close'].iloc[-1]
                now = datetime.now().strftime('%H:%M:%S')
                
                # 3. Print Clean Status
                print(f"\n⏰ {now} | Price: {current_price:.2f} | 💰 Equity: {usdt_total:.2f} USDT")
                print(f"🧠 Signal: {signal}")
                
                # 4. Act
                if signal in ["BUY", "SELL"]:
                    execute_trade(signal, current_price)
                else:
                    print("✋ HOLDING")
            
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()