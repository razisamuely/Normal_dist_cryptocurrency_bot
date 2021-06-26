import json
import time
from binance.exceptions import BinanceOrderMinAmountException, BinanceAPIException
from recordclass import recordclass
from datetime import datetime


class ManageFilledOrders(object):
    def __init__(self, symbol):
        self.symbol = symbol

    def get_all_orders(self, client, symbol: str, sleep_time_seconds: int = 1):
        while True:
            try:
                all_orders = client.get_all_orders(symbol=symbol)
                break
            except:
                print(f"No response for 'get_all_orders' method, time = {datetime.now().strftime('%d - %H:%M:%S')}")
                time.sleep(sleep_time_seconds)
        return all_orders

    def load_buy_filled_order_properties(self, orderId, order_tracking_path: str, get_sleep_time: float = 0.01):
        orders_tracking_path = f'{order_tracking_path}/{orderId}.txt'
        with open(orders_tracking_path) as json_file:
            while True:
                try:
                    filled_order_i = json.load(json_file)
                    break
                except:
                    time.sleep(get_sleep_time)

        return filled_order_i

    def add_subtract_counter(self, counter_path, add_subtract):
        with open(counter_path, "r+") as f:
            counter = int(f.read()) + add_subtract
            f.seek(0)
            f.write(str(counter))
            f.truncate()
            return counter

    def get_all_buy_sell_orders(self, client, symbol):
        all_orders = client.get_all_orders(symbol=symbol)
        sell_orders = [o['orderId'] for o in all_orders if (o['status'] == 'FILLED') and (o['side'] == 'SELL')]
        buy_orders = [o['orderId'] for o in all_orders if (o['status'] == 'FILLED') and (o['side'] == 'BUY')]
        return all_orders, sell_orders, buy_orders

    def set_sell_order(self, client, quantity: float, sellPrice: float, symbol: str, number_of_attempts: int = 5,
                       reduce_quantity: float = 0.01, sell_decimal_points: int = 3):
        cn = 0
        b = False
        qn = quantity
        sellPrice = round(sellPrice, sell_decimal_points)
        while True:
            sell_order = False
            try:
                sell_order = client.order_limit_sell(
                    symbol=symbol,
                    quantity=qn,
                    price=sellPrice)
                break

            except BinanceAPIException as  e:
                if not b:
                    b = client.get_account()['balances']
                print(e)
                print(f"current sell quantity = {qn}, "
                      f"available sell quantity = {[i for i in b if i['asset'] == 'BNB'][0]['free']}")

                qn = round(qn - reduce_quantity, sell_decimal_points)
                cn += 1
                if cn == number_of_attempts:
                    print(f"try num ={cn}, first sell qnty ={quantity} last sell qnty ={qn}")
                    break

        return sell_order

    def update_initConfigs_transaction_counter(self, configs_path):
        with open(configs_path, encoding='utf-8', errors='ignore') as json_file:
            initConfigs = json.load(json_file, object_hook=lambda d: recordclass('X', d.keys())(*d.values()))

        initConfigs.transactions_counter += 1

        with open(configs_path, 'w') as outfile:
            json.dump(json.loads(json.dumps(initConfigs.__dict__)), outfile)

        return initConfigs.transactions_counter
