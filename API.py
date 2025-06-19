# API.py
import websocket, json
from datetime import datetime, timedelta

class XTB:
    __version__ = "1.0"

    def __init__(self, ID, PSW):
        self.ID = ID
        self.PSW = PSW
        self.ws = None
        self.exec_start = self.get_time()
        self.connect()
        self.login()

    def connect(self):
        try:
            self.ws = websocket.create_connection("wss://xapi.xtb.com/demo")
            return True
        except Exception as e:
            print("❌ Error conectando websocket:", e)
            raise Exception("❌ WebSocket no está conectado.")

    def disconnect(self):
        try:
            self.ws.close()
            return True
        except:
            return False

    def send(self, msg):
        if not self.ws:
            raise Exception("❌ WebSocket no está conectado.")
        self.is_on()
        self.ws.send(msg)
        return self.ws.recv()

    def login(self):
        login = {
            "command": "login",
            "arguments": {
                "userId": self.ID,
                "password": self.PSW
            }
        }
        login_json = json.dumps(login)
        result = self.send(login_json)
        result = json.loads(result)
        return str(result["status"]) == "True"

    def logout(self):
        logout = { "command": "logout" }
        result = self.send(json.dumps(logout))
        result = json.loads(result)
        self.disconnect()
        return str(result["status"]) == "True"

    def get_ServerTime(self):
        request = { "command": "getServerTime" }
        result = self.send(json.dumps(request))
        return json.loads(result)["returnData"]["time"]

    def get_Balance(self):
        request = { "command": "getMarginLevel" }
        result = self.send(json.dumps(request))
        return json.loads(result)["returnData"]["balance"]

    def get_Symbol(self, symbol):
        request = {
            "command": "getSymbol",
            "arguments": { "symbol": symbol }
        }
        result = self.send(json.dumps(request))
        return json.loads(result)["returnData"]

    def get_Candles(self, period, symbol, qty_candles=1):
        period_map = {
            "M1": 1, "M5": 5, "M15": 15, "M30": 30,
            "H1": 60, "H4": 240, "D1": 1440,
            "W1": 10080, "MN1": 43200
        }
        base_period = period_map.get(period, 1)
        minutes = base_period * qty_candles * 2
        start = self.get_ServerTime() - self.to_milliseconds(minutes=minutes)

        request = {
            "command": "getChartLastRequest",
            "arguments": {
                "info": {
                    "period": base_period,
                    "start": start,
                    "symbol": symbol
                }
            }
        }

        result = self.send(json.dumps(request))
        data = json.loads(result)
        rates = data["returnData"]["rateInfos"]
        candles = [{"datetime": r["ctmString"], "open": r["open"], "close": r["close"],
                    "high": r["high"], "low": r["low"]} for r in rates]
        return [{"qty_candles": len(rates), "digits": data["returnData"]["digits"]}] + candles

    def make_Trade(self, symbol, cmd, transaction_type, volume, comment="", order=0, sl=0, tp=0, days=0, hours=0, minutes=0):
        price_data = self.get_Candles("M1", symbol, qty_candles=1)
        price = price_data[1]["open"] + price_data[1]["close"]
        delay = self.to_milliseconds(days, hours, minutes)
        expiration = self.get_ServerTime() + (delay or self.to_milliseconds(minutes=1))

        TRADE_TRANS_INFO = {
            "cmd": cmd,
            "customComment": comment,
            "expiration": expiration,
            "offset": -1,
            "order": order,
            "price": price,
            "sl": sl,
            "symbol": symbol,
            "tp": tp,
            "type": transaction_type,
            "volume": volume
        }

        trade = {
            "command": "tradeTransaction",
            "arguments": { "tradeTransInfo": TRADE_TRANS_INFO }
        }
        result = self.send(json.dumps(trade))
        parsed = json.loads(result)
        if parsed["status"]:
            return True, parsed["returnData"]["order"]
        return False, 0

    def is_on(self):
        delta = (self.get_time() - self.exec_start).total_seconds()
        if delta >= 8:
            self.connect()
        self.exec_start = self.get_time()

    def get_time(self):
        now = datetime.today().strftime('%m/%d/%Y %H:%M:%S%f')
        return datetime.strptime(now, '%m/%d/%Y %H:%M:%S%f')

    def to_milliseconds(self, days=0, hours=0, minutes=0):
        return (days*86400000) + (hours*3600000) + (minutes*60000)
