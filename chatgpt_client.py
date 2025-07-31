# chatgpt_client.py

import openai
import MetaTrader5 as mt5
from datetime import datetime
import os
import openai

# Lee la clave desde la variable de entorno (Railway o local)
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    print("❌ ERROR: OPENAI_API_KEY no detectada en el entorno.")
else:
    print("✅ OpenAI API Key detectada correctamente.")



def build_prompt(symbol):
    """
    Crea el prompt para ChatGPT con análisis técnico + contexto macroeconómico.
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
Eres un experto en trading profesional y análisis macroeconómico.

Analiza el activo: {symbol}.
Aquí están las últimas 20 velas diarias con datos OHLC:

{ohlc}

Evalúa si hay oportunidad de entrada basada en esta estrategia:

1. Fractal confirmado (patrón técnico de cambio de dirección)
2. Retroceso al nivel del 38.2 % de Fibonacci
3. Ruptura del nivel del impulso anterior

Además, considera **el contexto macroeconómico actual global** (tasas, inflación, noticias clave, eventos de alto impacto) y cómo podría influir en este activo. Solo si todos los criterios convergen, da una señal de entrada.

Responde solo en JSON si hay entrada:

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
                {"role": "system", "content": "Eres un analista técnico y macroeconómico profesional."},
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
