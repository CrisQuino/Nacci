# chatgpt_client.py

import openai
from config import OPENAI_API_KEY
import MetaTrader5 as mt5
from datetime import datetime, timedelta

openai.api_key = OPENAI_API_KEY

def build_prompt(symbol):
    """
    Crea el prompt para ChatGPT con el resumen técnico del activo actual.
    """
    if not mt5.initialize():
        raise Exception("MT5 no iniciado.")
    
    candles = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 20)
    mt5.shutdown()
    
    if candles is None or len(candles) < 10:
        return None

    ohlc = [
        {
            "open": round(candle['open'], 5),
            "high": round(candle['high'], 5),
            "low": round(candle['low'], 5),
            "close": round(candle['close'], 5)
        }
        for candle in candles
    ]

    prompt = f"""
Eres un experto en trading técnico.

Analiza el siguiente activo: {symbol}.
Aquí tienes las últimas 20 velas diarias con datos OHLC:

{ohlc}

Con base en la estrategia: fractal + retroceso del 38.2 % + rotura de nivel,
responde si existe una oportunidad de entrada. Si la hay, responde solo en JSON como:

{{
  "valid": true,
  "entry_price": 1.12345,
  "sl_price": 1.11800,
  "tp_price": 1.13200,
  "direction": "buy"
}}

Si no hay entrada, responde:

{{ "valid": false }}
"""
    return prompt

def check_entry_signal(symbol):
    """
    Envía el prompt a ChatGPT y evalúa si hay entrada válida.
    """
    prompt = build_prompt(symbol)
    if not prompt:
        print("⚠️ No se pudo construir el prompt.")
        return {"valid": False}

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en trading técnico."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        message = response["choices"][0]["message"]["content"]
        result = eval(message) if "valid" in message else {"valid": False}
        return result
    except Exception as e:
        print(f"❌ Error al consultar ChatGPT: {e}")
        return {"valid": False}
