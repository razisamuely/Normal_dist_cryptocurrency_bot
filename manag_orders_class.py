from binance.exceptions import BinanceAPIException
from recordclass import recordclass
from requests.exceptions import Timeout
import json
import time


class ManagOrders(object):
    def get_open_orders(self, client, symbol: str, timeout: int):
        while True:
            try:
                open_orders = client.get_open_orders(symbol=symbol,
                                                     # requests_params={'timeout': timeout}
                                                     )
                number_of_open_orders = len(open_orders)
                break
            except Timeout as e:
                print(e)
                time.sleep(1)
                timeout = timeout + 5

        return open_orders, number_of_open_orders

    def sell_buy_open(self, open_buy_and_sell):
        open_buy = [b for b in open_buy_and_sell if b['side'] == 'BUY']
        open_buy_order_number = len(open_buy)
        open_sell = [b for b in open_buy_and_sell if b['side'] == 'SELL']
        open_sell_number = len(open_sell)
        return open_buy, open_buy_order_number, open_sell, open_sell_number

    def place_order_switch(self, place_order: bool, manage_orders_path: str):
        switches = {'place_order': place_order}
        with open(manage_orders_path, 'w') as outfile:
            json.dump(switches, outfile)

    def get_filled_counter(self, counter_path: str):
        with open(counter_path, "r+") as f:
            filled_orders_counter = int(f.read())
        return filled_orders_counter

    def cancel_tail_of_open_buy_orders(self, client, tail_length: int, open_buy: list, symbol: str,
                                       number_of_open_orders: int):
        for tail in range(0, tail_length):
            tail_order_to_remove = open_buy[tail]
            tail_order_id_to_remove = tail_order_to_remove['orderId']
            try:
                client.cancel_order(symbol=symbol, orderId=tail_order_id_to_remove)
                print(
                    f"canceled orderId = {tail_order_id_to_remove} - reason: number of orders is {number_of_open_orders}")
            except BinanceAPIException as e:
                print('cancel_tail_of_open_buy_orders  ', e)

    def cancel_old_buy_order(self, client, symbol: str, open_buy: list, order_life_time: int):
        current_time = time.time()
        for open_order_i in open_buy:
            order_time_i = open_order_i['time'] / 1000
            current_time_order_time_diff = current_time - order_time_i

            if current_time_order_time_diff > order_life_time:
                order_id_i = open_order_i['orderId']

                try:
                    client.cancel_order(symbol=symbol, orderId=order_id_i)
                    print(f"canceled order id = {order_id_i} reason = - !old order! -, "
                          f"created before {round(current_time_order_time_diff)} seconds")


                except BinanceAPIException as e:
                    print('cancel_old_buy_order  ', e)

    def get_initConfigs(self, initConfigs_path: str):
        while True:
            try:
                with open(initConfigs_path, encoding='utf-8', errors='ignore') as json_file:
                    initConfigs = json.load(json_file, object_hook=lambda d: recordclass('X', d.keys())(*d.values()))
                    break
            except:
                time.sleep(0.01)
        return initConfigs

    def reset_counter(self, counter_path, new_counter_value):
        with open(counter_path, "r+") as f:
            counter = new_counter_value
            f.seek(0)
            f.write(str(counter))
            f.truncate()
            return counter
