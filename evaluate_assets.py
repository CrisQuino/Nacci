# evaluate_assets.py

from optimization import optimize_parameters_for_asset
from config import ACTIVE_LIST
from data_loader import load_ohlc_data
import pandas as pd

def evaluate_all_assets(assets):
    """
    Evalúa varios activos y selecciona el mejor basado en score compuesto.

    Retorna:
        str: símbolo del activo óptimo
    """
    evaluations = []

    for symbol in assets:
        print(f"📊 Evaluando {symbol}...")
        try:
            data = load_ohlc_data(symbol)
            result = optimize_parameters_for_asset(symbol, ohlc_data=data)

            evaluations.append({
                "symbol": symbol,
                "expectancy": result["expectancy"],
                "sharpe_like": result["sharpe_like"],
                "score": result["expectancy"] * result["sharpe_like"]
            })
        except Exception as e:
            print(f"⚠️ Fallo al evaluar {symbol}: {e}")

    df = pd.DataFrame(evaluations)
    if df.empty:
        raise ValueError("No se pudo optimizar ningún activo.")
    
    df_sorted = df.sort_values(by="score", ascending=False).reset_index(drop=True)
    print(df_sorted[["symbol", "expectancy", "sharpe_like", "score"]])
    return df_sorted.iloc[0]["symbol"]
