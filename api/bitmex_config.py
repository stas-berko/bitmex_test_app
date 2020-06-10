import bitmex
import bravado


class Bitmex:
    def __init__(self, account):
        self.conn = bitmex.bitmex(test=True, api_key=account.api_key, api_secret=account.api_secret)

    def create_order(self, orderType, symbol, orderQty, side):
        try:
            if res := self.conn.Order.Order_new(symbol=symbol, side=side, orderQty=orderQty, ordType=orderType).result():
                order, response = res
                return {"order_id": order["orderID"],
                        "price": order["price"],
                        "side": order["side"][0],
                        "symbol": order["symbol"],
                        "timestamp": order["timestamp"],
                        "volume": order["orderQty"],
                        }
        except bravado.exception.HTTPBadRequest as err:
            return None
