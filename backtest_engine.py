# backtest_engine.py

import numpy as np
import pandas as pd

def run_strategy_backtest(ohlc_data, tp_sl_ratio, be_threshold, ts_margin):
    """
    Ejecuta un backtest de la estrategia para una combinación de parámetros.

    Parámetros:
        ohlc_data (DataFrame): con columnas ['Open', 'High', 'Low', 'Close']
        tp_sl_ratio (float): multiplicador TP/SL (ej. 3.0)
        be_threshold (float): % del camino al TP donde aplicar BE
        ts_margin (float): % del camino donde aplicar trailing

    Retorna:
        dict: métricas como expectancy y drawdown
    """
    balance = 500
    results = []
    initial_balance = balance
    trades = detect_fractal_entries(ohlc_data)

    for trade in trades:
        entry = trade["entry"]
        sl = trade["sl"]
        direction = trade["type"]
        tp = entry + tp_sl_ratio * (entry - sl) if direction == "buy" else entry - tp_sl_ratio * (sl - entry)
        be_level = entry + be_threshold * (tp - entry) if direction == "buy" else entry - be_threshold * (entry - tp)
        trail_active = False
        trail_stop = sl

        for i in range(trade["index"] + 1, min(trade["index"] + 20, len(ohlc_data))):
            row = ohlc_data.iloc[i]
            high = row["High"]
            low = row["Low"]

            if direction == "buy":
                if high >= tp:
                    pnl = (tp - entry) * 1000
                    balance += pnl
                    results.append(pnl)
                    break
                if high >= be_level and not trail_active:
                    trail_active = True
                if trail_active:
                    trail_stop = max(trail_stop, high - ts_margin * (tp - entry))
                if low <= trail_stop:
                    pnl = (trail_stop - entry) * 1000
                    balance += pnl
                    results.append(pnl)
                    break
                if low <= sl:
                    pnl = (sl - entry) * 1000
                    balance += pnl
                    results.append(pnl)
                    break
            else:  # sell
                if low <= tp:
                    pnl = (entry - tp) * 1000
                    balance += pnl
                    results.append(pnl)
                    break
                if low <= be_level and not trail_active:
                    trail_active = True
                if trail_active:
                    trail_stop = min(trail_stop, low + ts_margin * (entry - tp))
                if high >= trail_stop:
                    pnl = (entry - trail_stop) * 1000
                    balance += pnl
                    results.append(pnl)
                    break
                if high >= sl:
                    pnl = (entry - sl) * 1000
                    balance += pnl
                    results.append(pnl)
                    break

    if not results:
        return {"expectancy": 0.0, "max_drawdown_pct": 0.0}

    cumulative = np.cumsum(results)
    peak = np.maximum.accumulate(cumulative)
    drawdown = cumulative - peak
    max_drawdown = drawdown.min()
    max_drawdown_pct = abs(max_drawdown) / initial_balance * 100
    expectancy = np.mean(results)

    return {
        "expectancy": expectancy,
        "max_drawdown_pct": max_drawdown_pct
    }

def detect_fractal_entries(df):
    """
    Detecta puntos de entrada por fractales simples en los datos.
    """
    trades = []
    for i in range(2, len(df) - 2):
        high = df['High']
        low = df['Low']
        if low[i] < low[i-1] and low[i] < low[i+1] and low[i-1] < low[i-2] and low[i+1] < low[i+2]:
            entry = df['Close'][i+1]
            sl = low[i]
            trades.append({"index": i+1, "entry": entry, "sl": sl, "type": "buy"})
        elif high[i] > high[i-1] and high[i] > high[i+1] and high[i-1] > high[i-2] and high[i+1] > high[i+2]:
            entry = df['Close'][i+1]
            sl = high[i]
            trades.append({"index": i+1, "entry": entry, "sl": sl, "type": "sell"})
    return trades
