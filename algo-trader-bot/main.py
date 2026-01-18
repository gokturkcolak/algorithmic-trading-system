import ccxt
import pandas as pd
import time
from datetime import datetime
import config
from strategy import MLStrategy
from execution import BinanceExecutor

def initialize_exchange():
    exchange = ccxt.binance({
        'apiKey': config.API_KEY,
        'secret': config.SECRET_KEY,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
            'adjustForTimeDifference': True
        }
    })
    
    if config.TESTNET:
        exchange.set_sandbox_mode(True)
    
    exchange.load_markets()
    return exchange

def fetch_live_data(exchange, limit=1000):
    """
    Fetches the last 1000 candles to feed the ML model.
    """
    print("   📡 Fetching new data...")
    ohlcv = exchange.fetch_ohlcv(config.SYMBOL, config.TIMEFRAME, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('datetime', inplace=True)
    
    # Ensure numeric
    cols = ['open', 'high', 'low', 'close', 'volume']
    df[cols] = df[cols].apply(pd.to_numeric, axis=1)
    
    return df

def run_bot():
    print(f"🤖 ACTIVATING ALGO-TRADER ({config.SYMBOL})")
    print(f"   Mode: {'TESTNET' if config.TESTNET else 'LIVE'}")
    
    # 1. Initialize Components
    exchange = initialize_exchange()
    executor = BinanceExecutor(exchange)
    strategy = MLStrategy(model_path='model.json')
    
    print("✅ System Online. Starting Loop...")
    
    # 2. Infinite Loop
    while True:
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Analysis Tick...")
            
            # A. Fetch Data
            df = fetch_live_data(exchange)
            
            # B. Ask Strategy for Decision
            # We pass the full dataframe. The strategy handles feature calc inside.
            signal = strategy.check_signal(df)
            print(f"   🔮 Signal: {signal}")
            
            # C. Execute if needed
            if signal == "BUY":
                executor.place_buy_order()
            elif signal == "SELL":
                executor.place_sell_order()
            else:
                print("   💤 Holding Position...")

            # D. Wait for next candle
            # For 1h candles, checking every 60 seconds is fine.
            print("   ⏳ Waiting 60 seconds...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n🛑 Bot Stopped by User.")
            break
        except Exception as e:
            print(f"❌ CRITICAL LOOP ERROR: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()