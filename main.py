# main.py

import schedule
import time
from datetime import datetime
from optimization import optimize_parameters_for_asset
from evaluate_assets import evaluate_all_assets
from chatgpt_client import check_entry_signal
from mt5_executor import open_trade, manage_open_positions
from config import ACTIVE_LIST, INTERVAL_MINUTES

# Variable global con activo y parámetros óptimos semanales
current_week_config = {
    "symbol": None,
    "params": {}
}

def initialize_week():
    print(f"[{datetime.now()}] ⏳ Evaluando mejores activos...")
    best_asset = evaluate_all_assets(ACTIVE_LIST)
    print(f"[{datetime.now()}] ✅ Activo seleccionado: {best_asset}")
    print(f"[{datetime.now()}] 🧠 Optimizando parámetros para {best_asset}...")
    optimal_params = optimize_parameters_for_asset(best_asset)
    print(f"[{datetime.now()}] 🎯 Parámetros óptimos: {optimal_params}")
    current_week_config["symbol"] = best_asset
    current_week_config["params"] = optimal_params

def periodic_check():
    symbol = current_week_config["symbol"]
    params = current_week_config["params"]
    if not symbol or not params:
        print(f"[{datetime.now()}] ⚠️ Activo o parámetros no definidos.")
        return

    print(f"[{datetime.now()}] 📡 Consultando ChatGPT para {symbol}...")
    entry = check_entry_signal(symbol)
    if entry and entry["valid"]:
        print(f"[{datetime.now()}] 📥 Entrada válida detectada. Ejecutando trade.")
        open_trade(symbol, entry["entry_price"], entry["sl_price"], entry["tp_price"], params)

    manage_open_positions(symbol, params)

if __name__ == "__main__":
    initialize_week()
    schedule.every().monday.at("06:00").do(initialize_week)
    schedule.every(INTERVAL_MINUTES).minutes.do(periodic_check)

    print(f"[{datetime.now()}] 🚀 Bot iniciado. Monitoreando cada {INTERVAL_MINUTES} minutos.")
    while True:
        schedule.run_pending()
        time.sleep(1)
