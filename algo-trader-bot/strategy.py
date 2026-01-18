import pandas as pd
import pandas_ta as ta
from xgboost import XGBClassifier
import numpy as np
import os  # <--- New import for file paths

class MLStrategy:
    def __init__(self, model_path='model.json'):
        # 1. ROBUST PATH HANDLING
        # Find the folder where THIS script (strategy.py) lives
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Combine it with the model name to get the absolute path
        full_path = os.path.join(script_dir, model_path)
        
        print(f"   📂 Loading Model from: {full_path}")

        # 2. Load the trained model
        self.model = XGBClassifier()
        self.model.load_model(full_path)
        
        # Hyperparameters (Matching your Winning Backtest)
        self.THRESHOLD_BUY = 0.30
        self.THRESHOLD_SELL = 0.25
        
        # State
        self.position = 0 # 0 = Cash, 1 = Long

    def prepare_features(self, df):
        """
        CONVERT RAW DATA -> ML FEATURES
        """
        df = df.copy()
        
        # 1. Log Returns
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # 2. Indicators
        df.ta.rsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.atr(length=14, append=True)
        
        # 3. Drop NaNs
        df.dropna(inplace=True)
        
        return df

    def check_signal(self, df):
        """
        INPUT: 1000 candles of Data
        OUTPUT: 'BUY', 'SELL', or 'HOLD'
        """
        # 1. Calculate Features
        df_processed = self.prepare_features(df)
        
        # 2. Select the EXACT columns the model was trained on
        feature_cols = ['log_returns', 'RSI_14', 'MACDh_12_26_9', 'ATRr_14']
        
        # 3. Get the latest row (The candle that just closed)
        latest_data = df_processed.iloc[[-1]][feature_cols]
        
        # 4. Predict Probability
        prob = self.model.predict_proba(latest_data)[:, 1][0]
        print(f"   📊 Model Confidence: {prob:.4f}")

        # 5. Hysteresis Logic
        signal = "HOLD"
        
        if self.position == 0:
            if prob > self.THRESHOLD_BUY:
                signal = "BUY"
                self.position = 1
        
        elif self.position == 1:
            if prob < self.THRESHOLD_SELL:
                signal = "SELL"
                self.position = 0
                
        return signal