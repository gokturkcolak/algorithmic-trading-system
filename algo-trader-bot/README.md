# 🤖 Algorithmic Trading Bot

A professional-grade algorithmic trading bot powered by Machine Learning (XGBoost) and technical analysis. This bot automates trading on Binance by fetching live market data, analyzing trends using a pre-trained ML model, and executing trades based on confidence probabilities.

## 🚀 Features

- **ML-Powered**: Uses an XGBoost classifier to predict market movements.
- **Technical Analysis**: Integrates RSI, MACD, and ATR indicators for robust feature engineering.
- **Automated Execution**: Connects via `ccxt` to Binance for seamless order placement.
- **Risk Management**: Configurable confidence thresholds for entering and exiting positions.
- **Testnet Support**: Safely test strategies with fake money before going live.

## 🛠️ Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd algo-trader-bot
   ```

2. **Install Dependencies**
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   Create a `.env` file in the root directory and add your Binance API credentials:
   ```env
   # For Live Trading
   BINANCE_API_KEY=your_api_key
   BINANCE_SECRET_KEY=your_secret_key

   # For Testnet (Optional)
   BINANCE_TESTNET_API_KEY=your_testnet_api_key
   BINANCE_TESTNET_SECRET_KEY=your_testnet_secret_key
   ```

## ⚙️ Configuration

You can customize the bot's behavior in `config.py`:

- **`TESTNET`**: Set to `True` for simulation, `False` for real trading.
- **`SYMBOL`**: Trading pair (e.g., `'ETH/USDT'`).
- **`TIMEFRAME`**: Candle interval (e.g., `'1h'`).
- **`THRESHOLD_BUY` / `THRESHOLD_SELL`**: Confidence levels to trigger trades.

## 🏃 Usage

Run the bot with the following command:

```bash
python main.py
```

The bot will:
1. Initialize the connection to Binance.
2. Load the pre-trained `model.json`.
3. Enter an infinite loop to fetch data and check signals every 60 seconds.

## 🧠 How It Works

1. **Data Ingestion**: Fetches the last 1000 candles of OHLCV data from Binance.
2. **Feature Engineering**: Calculates Log Returns, RSI (14), MACD (12, 26, 9), and ATR (14).
3. **Prediction**: The XGBoost model analyzes the latest candle features to predict the probability of an upward trend.
4. **Execution Logic**:
   - **BUY**: If Model Confidence > `THRESHOLD_BUY` (Default: 0.30) AND currently holding Cash.
   - **SELL**: If Model Confidence < `THRESHOLD_SELL` (Default: 0.25) AND currently holding a Position.
   - **HOLD**: Maintained otherwise.

## ⚠️ Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.
