from flask import Flask, request
from API import XTB

app = Flask(__name__)

# Configura tus datos de XTB
xtb_user = "50736161"
xtb_pass = "19734826N"
symbol = "GOLD"
lotaje = 0.02

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Alerta recibida:", data)

    action = data.get("action")
    sl = float(data.get("sl", 0))
    tp = float(data.get("tp", 0))
    trail = float(data.get("trail", 0))

    bot = XTB(xtb_user, xtb_pass)

    if action == "buy":
        current_price = bot.get_symbol_price(symbol)
        sl_price = round(current_price - sl, 2)
        tp_price = round(current_price + tp, 2)
        status, order_id = bot.make_Trade(
            symbol=symbol,
            cmd=0,
            transaction_type=0,
            volume=lotaje,
            sl=sl_price,
            tp=tp_price,
            trailing_step=round(trail * 10),
            comment="Compra automática"
        )
        print("Compra ejecutada:", status, order_id)

    elif action == "sell":
        current_price = bot.get_symbol_price(symbol)
        sl_price = round(current_price + sl, 2)
        tp_price = round(current_price - tp, 2)
        status, order_id = bot.make_Trade(
            symbol=symbol,
            cmd=1,
            transaction_type=0,
            volume=lotaje,
            sl=sl_price,
            tp=tp_price,
            trailing_step=round(trail * 10),
            comment="Venta automática"
        )
        print("Venta ejecutada:", status, order_id)

    bot.logout()
    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)
