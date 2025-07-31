# 🤖 AI Trading Bot – ChatGPT + Optimización + MT5

Este proyecto implementa un bot de trading autónomo que:

- ✅ Evalúa múltiples activos semanalmente (EURUSD, GBPUSD, USDJPY, etc.)
- 🧠 Optimiza los parámetros de la estrategia (TP/SL, Break-even, Trailing)
- 📡 Consulta a ChatGPT si hay señales de entrada válidas
- 📈 Ejecuta operaciones automáticamente en MetaTrader 5
- 🔁 Gestiona las operaciones activas con break-even y trailing
- 🚫 No necesita GUI ni interacción humana para correr

---

## 📦 Requisitos

- Python 3.10+
- Docker (opcional)
- Una instancia de MetaTrader 5 **abierta en otro equipo o VPS**
- Clave de API de OpenAI

---

## 🛠 Instalación

```bash
git clone https://github.com/tu_usuario/trading-bot-ai.git
cd trading-bot-ai
pip install -r requirements.txt
