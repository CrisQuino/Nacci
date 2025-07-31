# data_loader.py

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

def load_ohlc_data(symbol, days=180):
    """
    Carga datos OHLC diarios desde MetaTrader 5.

    Parámetros:
        symbol (str): el símbolo del activo, ej. 'EURUSD'
        days (int): cantidad de días hacia atrás desde hoy

    Retorna:
        DataFrame: con columnas ['Open', 'High', 'Low', 'Close']
    """
    if not mt5.initialize():
        raise RuntimeError("MT5 no se pudo iniciar. Verifica que esté abierto y configurado.")

    utc_to = datetime.now()
    utc_from = utc_to - timedelta(days=days)

    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_D1, utc_from, utc_to)
    if rates is None or len(rates) == 0:
        mt5.shutdown()
        raise ValueError(f"No se pudieron obtener datos para {symbol}.")

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    df = df[['open', 'high', 'low', 'close']]
    df.columns = ['Open', 'High', 'Low', 'Close']

    mt5.shutdown()
    return df
