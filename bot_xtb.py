from flask import Flask, request, jsonify
from API import XTB  # Usamos la clase XTB personalizada
import json

app = Flask(__name__)

# === 🔒 CREDENCIALES XTB ===
XTB_USER = "50736161"
XTB_PASS = "19734826N"

# === 📡 INICIAR CLIENTE DE XTB ===
client = XTB(XTB_USER, XTB_PASS)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        print("🔔 Señal recibida:", data)

        action = data.get("action")  # "buy" o "sell"
        sl = float(data.get("sl", 0))
        tp = float(data.get("tp", 0))
        trail = float(data.get("trail", 0))

        if action in ["buy", "sell"]:
            ejecutar_orden(action, sl, tp, trail)
        else:
            print("⚠️ Acción no reconocida:", action)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error en webhook:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test_xtb', methods=['GET'])
def test_xtb():
    try:
        balance = float(client.get_Balance())
        return jsonify({"status": "ok", "msg": "✅ Conectado correctamente a XTB", "balance": balance})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})

def ejecutar_orden(tipo, sl, tp, trail):
    try:
        symbol = "GOLD"
        riesgo_pct = 1.0
        capital = float(client.get_Balance())
        riesgo = capital * (riesgo_pct / 100)

        precio_actual = float(client.get_Symbol(symbol)["ask"])
        distancia_sl = abs(precio_actual - sl)
        valor_pip = 1
        lotaje = round(riesgo / (distancia_sl * valor_pip), 2)

        cmd = 0 if tipo == "buy" else 1

        print(f"📊 Capital: {capital} | Riesgo: {riesgo} | SL distancia: {distancia_sl} | Lotaje: {lotaje}")

        ok, order_id = client.make_Trade(
            symbol=symbol,
            cmd=cmd,
            transaction_type=0,
            volume=lotaje,
            sl=sl,
            tp=tp,
            comment="Bot Oro CFD"
        )

        if ok:
            print(f"✅ Orden enviada correctamente. ID: {order_id}")
        else:
            print("❌ Error al enviar la orden")

    except Exception as e:
        print("❌ Error al ejecutar orden:", e)

# === INICIAR SERVIDOR ===
if __name__ == '__main__':
    app.run(port=5000)
