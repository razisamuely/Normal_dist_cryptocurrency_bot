import time
from datetime import datetime
import numpy as np
from recordclass import recordclass
from scipy import stats
from binance.exceptions import BinanceAPIException
import json


class PercentileMenagmant(object):

    def get_historical_klines(slef, client, symbol: str, interval, start_str: str):
        cnt = 0
        while True:
            try:
                klines = client.get_historical_klines(symbol=symbol,
                                                      interval=interval,
                                                      start_str=start_str)

                break
            except BinanceAPIException as e:
                print(e)

            except:
                cnt += 1
                if cnt == 10:
                    print('Didnt pulled klines')

            time.sleep(1)

        if 'klines' in locals():
            return klines

    def calculate_median_min_max(slef, minute_average_list_np: list):
        median = np.median(minute_average_list_np)
        max_price = max(minute_average_list_np)
        min_price = min(minute_average_list_np)
        return median, max_price, min_price

    def convert_klines_to_minute_average_list(slef, klines: list):
        minute_average_list = [(float(i[2]) + float(i[3])) / 2 for i in klines]
        minute_average_list_np = np.array(minute_average_list)
        return minute_average_list_np

    def print_summary_and(self, initConfigs: dict, klines: list, current_median: float, percentile: float,
                          movement_ration: float):

        minute_average_list_np = self.convert_klines_to_minute_average_list(klines=klines)
        median, max_price, min_price = self.calculate_median_min_max(minute_average_list_np=minute_average_list_np)

        print(f'\n\n- - - = - = - - -\n'
              f'buy_switch  = {initConfigs.buy_switch:.4f}\n'
              f'max_price  = {max_price:.4f}\n'
              f'min_price  = {min_price:.4f}\n'
              f'median price  = {median:.4f}\n'
              f'last_price = {current_median}\n'
              f'prob_lower = {initConfigs.prob_lower:.10f},\n'
              f'prob_upper = {initConfigs.prob_upper:.10f}\n'
              f'current_probability = {initConfigs.probability:.10f} \n'
              f'percentile = {percentile:.3f},\n'
              f"movement_ration = {movement_ration:.3%}\n"
              f"time = {datetime.now().strftime('%d - %H:%M:%S')}\n"
              f"- - - = - = - - -")

    def get_historical_trades_mean(self, client, symbol: str, limit: int):
        last_trades = client.get_historical_trades(symbol=symbol, limit=limit)
        last_trades_prices = [float(p['price']) for p in last_trades]
        current_median = np.median(last_trades_prices)
        return current_median

    def get_historical_trades_minute_interval_mean(self, klines: str):
        last_mean = [(float(i[2]) + float(i[3])) / 2 for i in klines]
        last_mean = np.mean(last_mean)
        return last_mean

    def calculate_probability_and_percentile(self, klines: list, current_median: float, prob_lower: float,
                                             prob_upper: float):
        minute_average_list_np = self.convert_klines_to_minute_average_list(klines=klines)
        percentile = 1 - stats.percentileofscore(minute_average_list_np, current_median) / 100
        prob_diff = prob_upper - prob_lower
        probability = prob_diff * percentile + prob_lower

        return probability, percentile

    def save_initConfigs(self, configs_path: str, initConfigs):
        with open(configs_path, 'w') as outfile:
            json.dump(json.loads(json.dumps(initConfigs.__dict__)), outfile)

    def get_initConfigs(self, configs_path: str):
        with open(configs_path, encoding='utf-8', errors='ignore') as json_file:
            initConfigs = json.load(json_file, object_hook=lambda d: recordclass('X', d.keys())(*d.values()))

        return initConfigs
