# config.py

# 🔐 OpenAI API Key
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 📈 Lista de activos a evaluar semanalmente
ACTIVE_LIST = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "XAUUSD",
    "SPX500",
    "BTCUSD"
]

# ⏱️ Intervalo de análisis en minutos
INTERVAL_MINUTES = 30

# 💵 Configuración de riesgo
RISK_PER_TRADE = 0.02  # 2% del balance
LOT_SIZE = 100000      # Tamaño estándar de lote para FX
MAX_SL_PIPS = 50       # Máximo SL en pips para calcular lote

# 🧠 Configuración del optimizador
TP_SL_RANGE = [1.5, 2.0, 2.5, 3.0]
BE_THRESHOLDS = [0.4, 0.5, 0.6]
TS_MARGINS = [0.1, 0.15, 0.2, 0.25]

# 🕐 Historial para backtest (en días)
BACKTEST_DAYS = 120
