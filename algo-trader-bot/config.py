import os
from dotenv import load_dotenv

# Load secrets from .env file
load_dotenv()

# -----------------------------------------------------------------------------
# TOGGLES
# -----------------------------------------------------------------------------
# Set to True to trade with fake money. Set to False for REAL money.
TESTNET = True 

# Trading Settings
SYMBOL = 'ETH/USDT'
TIMEFRAME = '4h'
LIMIT = 1000

# Model Settings
THRESHOLD_BUY = 0.30
THRESHOLD_SELL = 0.15

# -----------------------------------------------------------------------------
# CREDENTIALS
# -----------------------------------------------------------------------------
if TESTNET:
    print("⚠️  RUNNING IN TESTNET MODE")
    API_KEY = os.getenv("BINANCE_TESTNET_API_KEY")
    SECRET_KEY = os.getenv("BINANCE_TESTNET_SECRET_KEY")
    BASE_URL = 'https://testnet.binance.vision/api' # Override for Testnet
else:
    print("🚨 RUNNING IN LIVE MODE (REAL MONEY)")
    API_KEY = os.getenv("BINANCE_API_KEY")
    SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
    BASE_URL = 'https://api.binance.com/api'