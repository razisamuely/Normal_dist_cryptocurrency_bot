import json
import os
import pickle
import time
from typing import List
from recordclass import recordclass
from binance.exceptions import BinanceAPIException
from configs.api_configs import create_client_object
from datetime import datetime


class PlaceBuyOrder(object):

    def __init__(self, symbol):
        self.symbol = symbol

    def clean_or_create_file_if_exist(self, directory):
        if os.path.exists(directory):
            files = os.listdir(directory)
            for f in files:
                os.remove(directory + f)
        else:
            os.makedirs(directory)

    def get_and_sort_real_time_files_names(self, save_real_time_data_path):
        files = os.listdir(save_real_time_data_path)[:]
        files = sorted(files, reverse=False)  # [2,3,4,1] -->> [1,2,3,4]
        return files

    def read_append_remove_file(self, tradesList, save_real_time_data_path, files):
        for f in files:
            path = save_real_time_data_path + f
            with open(path, encoding='utf-8', errors='ignore') as json_file:
                while True:
                    try:
                        data = json.load(json_file, strict=False)
                        break
                    except:
                        time.sleep(0.05)

            tradesList.append(data)
            os.remove(path)
        return tradesList

    def cut_under_window_time_quotes(self, tradesList, order_time_window):
        lastTradePointTime = tradesList[-1]['time']
        for i, trade_i in enumerate(tradesList):
            tradePointTime_i = trade_i["time"]
            secondsDiff = (lastTradePointTime - tradePointTime_i) / 1000
            if secondsDiff <= order_time_window:
                tradesList = tradesList[i + 1:]
                break

        return tradesList

    def get_order_witch(self, manage_orders_path: str):
        with open(manage_orders_path) as json_file:
            while True:
                try:
                    switch = json.load(json_file)
                    break
                except:
                    time.sleep(0.05)

            return switch

    def save_data_for_investigation(self, tradesList: List[dict], path: str = './data/data_for_research',
                                    switch: bool = False):
        data = tradesList[-1]
        if switch:
            with open(f'{path}/investigate_trade_list_{data["time"]}', 'wb') as fp:
                pickle.dump(tradesList, fp)

    def write_order_tracking(self, order: json, last_data_point, order_tracking_path: str):
        order_id = order['orderId']
        order_dict = {"orderId": order_id,
                      "transactTime": order['transactTime'],
                      "sell": last_data_point['sell'],
                      "status": order["status"]}

        orders_tracking_path = f'{order_tracking_path}/{order_id}.txt'
        with open(orders_tracking_path, 'w') as outfile:
            json.dump(order_dict, outfile)

    def load_json(self, path: str, sleep: float):
        with open(path) as json_file:
            while True:
                try:
                    with open(path, encoding='utf-8', errors='ignore') as json_file:
                        initConfigs = json.load(json_file,
                                                object_hook=lambda d: recordclass('X', d.keys())(*d.values()))
                    break
                except:
                    time.sleep(sleep)

        return initConfigs

    def buy(self, client, initConfigs: dict, buy_price: float, last_data_point: dict):
        cnt = 0
        order = False
        while True:
            try:
                order = client.order_limit_buy(
                    symbol=initConfigs.symbol,
                    quantity=initConfigs.quantity,
                    price=buy_price)
                break

            except BinanceAPIException as  e:
                initConfigs.quantity = round(initConfigs.quantity - 0.01,
                                             initConfigs.place_order_decimal_points)
                time.sleep(3)
                cnt += 1
                if cnt > 3:
                    print(e)
                    b = client.get_account()['balances']
                    print(f"\ncurrent quantity = {initConfigs.quantity}  ",
                          f"dolara = quantity * price ={float(last_data_point['price']) * initConfigs.quantity:.2f} "
                          f"available dolara = {[i for i in b if i['asset'] == 'USDT'][0]['free']}\n")
                    break
            except:
                print('something went wrong, reinit client, sleep = 3 ZZZzzz')
                client = create_client_object(keys_path=initConfigs.keys_path,
                                              configs_name=initConfigs.configs_name,
                                              is_demo=initConfigs.is_demo)
                time.sleep(3)
                cnt += 1
                if cnt > 3:
                    initConfigs.place_order = False
                    break
        return order

    def print_status_message(self, last_data_point, place_order):
        print(f"\nplace_order = {place_order} "
              f"current price ={float(last_data_point['price']):.2f}  "
              f"buy = {last_data_point['buy']:.2f}  "
              f"sell =  {last_data_point['sell']:.2f}  "
              f"time = {datetime.now().strftime('%d - %H:%M:%S')}\n")
