# mt5_executor.py

import MetaTrader5 as mt5
from datetime import datetime
from config import RISK_PER_TRADE, MAX_SL_PIPS, LOT_SIZE

def calculate_lot(entry, sl, balance, symbol):
    """
    Calcula el lotaje dinámico basado en el SL y el balance disponible.
    """
    risk_capital = balance * RISK_PER_TRADE
    sl_pips = abs(entry - sl)
    pip_value = 10  # Asumido por lote estándar
    if sl_pips == 0:
        sl_pips = 0.0001
    lots = round(risk_capital / (sl_pips * pip_value), 2)
    return max(lots, 0.01)

def open_trade(symbol, entry_price, sl_price, tp_price, params):
    """
    Abre una operación en MT5 con los parámetros óptimos y lotaje calculado.
    """
    if not mt5.initialize():
        raise Exception("No se pudo iniciar MetaTrader 5")

    acc_info = mt5.account_info()
    balance = acc_info.balance if acc_info else 1000
    direction = "buy" if entry_price < tp_price else "sell"
    lot = calculate_lot(entry_price, sl_price, balance, symbol)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if direction == "buy" else mt5.ORDER_TYPE_SELL,
        "price": mt5.symbol_info_tick(symbol).ask if direction == "buy" else mt5.symbol_info_tick(symbol).bid,
        "sl": sl_price,
        "tp": tp_price,
        "deviation": 20,
        "magic": 10001,
        "comment": "AutoTrade GPT",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Error al abrir trade: {result.retcode}")
    else:
        print(f"✅ Trade abierto en {symbol} - Lote: {lot} - {direction.upper()}")

    mt5.shutdown()

def manage_open_positions(symbol, params):
    """
    Aplica lógica de break-even y trailing stop a operaciones abiertas.
    """
    if not mt5.initialize():
        print("⚠️ No se pudo reconectar a MT5")
        return

    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        mt5.shutdown()
        return

    for pos in positions:
        ticket = pos.ticket
        entry = pos.price_open
        direction = "buy" if pos.type == mt5.ORDER_TYPE_BUY else "sell"
        current_price = mt5.symbol_info_tick(symbol).bid if direction == "sell" else mt5.symbol_info_tick(symbol).ask
        distance_to_tp = abs(pos.tp - entry)

        # Break-even: mover SL al entry si precio ha avanzado un % del camino
        be_level = entry + params["be_threshold"] * (pos.tp - entry) if direction == "buy" else entry - params["be_threshold"] * (entry - pos.tp)
        if (direction == "buy" and current_price >= be_level) or (direction == "sell" and current_price <= be_level):
            new_sl = entry

            # Trailing Stop
            if direction == "buy":
                trail_sl = current_price - params["ts_margin"] * distance_to_tp
                new_sl = max(new_sl, trail_sl)
            else:
                trail_sl = current_price + params["ts_margin"] * distance_to_tp
                new_sl = min(new_sl, trail_sl)

            # Enviar modificación
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": symbol,
                "position": ticket,
                "sl": round(new_sl, 5),
                "tp": pos.tp,
            }
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"🔁 SL actualizado para posición #{ticket}")
            else:
                print(f"⚠️ No se pudo actualizar SL: {result.retcode}")

    mt5.shutdown()
