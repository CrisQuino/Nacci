# optimization.py

import numpy as np
import pandas as pd
from backtest_engine import run_strategy_backtest

def optimize_parameters_for_asset(symbol, ohlc_data=None):
    """
    Ejecuta una optimización para encontrar la mejor combinación de parámetros
    para un activo usando datos OHLC y devolviendo el mejor set basado en
    Sharpe-like y Expectancy.

    Parámetros:
        symbol (str): nombre del activo (ej. 'EURUSD')
        ohlc_data (pd.DataFrame): opcional, si ya tienes los datos cargados

    Retorna:
        dict: parámetros óptimos {'tp_sl': float, 'be_threshold': float, 'ts_margin': float}
    """
    # Si no se proveen datos, deberías cargarlos aquí desde tu fuente (ej. MT5, Yahoo, etc.)
    if ohlc_data is None:
        ohlc_data = load_ohlc_data(symbol)

    tp_sl_range = [1.5, 2.0, 2.5, 3.0]
    be_thresholds = [0.4, 0.5, 0.6]
    ts_margins = [0.1, 0.15, 0.2, 0.25]

    best_score = -np.inf
    best_params = {}

    for tp_sl in tp_sl_range:
        for be in be_thresholds:
            for ts in ts_margins:
                results = run_strategy_backtest(
                    ohlc_data=ohlc_data,
                    tp_sl_ratio=tp_sl,
                    be_threshold=be,
                    ts_margin=ts
                )

                expectancy = results["expectancy"]
                max_dd = abs(results["max_drawdown_pct"])
                sharpe_like = expectancy / max_dd if max_dd > 0 else 0
                score = expectancy * sharpe_like  # ponderación compuesta

                if score > best_score:
                    best_score = score
                    best_params = {
                        "tp_sl": tp_sl,
                        "be_threshold": be,
                        "ts_margin": ts,
                        "expectancy": round(expectancy, 2),
                        "sharpe_like": round(sharpe_like, 2)
                    }

    return best_params

def load_ohlc_data(symbol):
    """
    Placeholder para cargar datos OHLC reales.
    En producción, puedes conectar a MT5, Binance, Yahoo, etc.
    """
    raise NotImplementedError("Falta implementar carga de datos OHLC para " + symbol)
