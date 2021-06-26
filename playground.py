import json
import time
from recordclass import recordclass
import numpy as np
from configs.api_configs import create_client_object
import pandas as pd

configs_path = './configs/init_configs.json'

with open(configs_path, encoding='utf-8', errors='ignore') as json_file:
    initConfigs = json.load(json_file, object_hook=lambda d: recordclass('X', d.keys())(*d.values()))

client = create_client_object(keys_path=initConfigs.keys_path,
                              configs_name=initConfigs.configs_name,
                              is_demo=initConfigs.is_demo)

# %%
client.get_open_orders()
# %%
b = client.get_account()['balances']
pd.DataFrame([[i for i in b if i['asset'] == 'BNB'][0], [i for i in b if i['asset'] == 'USDT'][0]])
# %%
for i in client.get_open_orders():
    print(f"price = {i['price']} ", f"status = {i['status']}", f"side = {i['side']} origQty ={i['origQty']}")
# %%
client.get_ticker(symbol='BNBUSDT')

# %%
order = client.order_limit_sell(
    symbol=initConfigs.symbol,
    quantity=,
    price=129)
# %%
order
# %%
client.cancel_order(orderId=1408072306, symbol=initConfigs.symbol)

# %%
client.order_limit_buy(
            symbol='BNBUSDT',
            quantity='0.15',
            price='354.11')

client
# %%
info = client.get_symbol_info('BNBUSDT')
print(info['filters'][2]['minQty'])

# %% 190.62334924
# minute_average_list = [(float(i[2]) + float(i[3])) / 2 for i in klines]
# minute_average_list

# %%
from datetime import datetime

i = client.get_historical_klines(symbol=initConfigs.symbol,
                                 interval=client.KLINE_INTERVAL_1MINUTE,
                                 start_str=f"10 min ago UTC")
print(len(i))

# %%
minutes_interval = 10
tt = 0
while True:
    kl = client.get_historical_klines(symbol=initConfigs.symbol,
                                      interval=client.KLINE_INTERVAL_1MINUTE,
                                      start_str=f"{minutes_interval} min ago UTC")
    minute_average_list = [(float(i[2]) + float(i[3])) / 2 for i in kl]
    if len(kl) < minutes_interval:
        time.sleep(1)
        print('taking sleep')

    else:
        print(len(kl))

# %%
kl = client.get_historical_klines(symbol=initConfigs.symbol,
                                  interval=client.KLINE_INTERVAL_1MINUTE,
                                  start_str=f"{minutes_interval} min ago UTC")
minute_average_list = [(float(i[2]) + float(i[3])) / 2 for i in kl]
# %%
p_list = []
l = minute_average_list
# l = 1,2,3,4,5,6,7,8,9
for p, c in zip(l[1:], l[0:minutes_interval - 1]):
    p_list.append((f'{p / c - 1:.3%}', c))

p_list

# %%
kl = client.get_historical_klines(symbol=initConfigs.symbol,
                                  interval=client.KLINE_INTERVAL_1MINUTE,
                                  start_str=f"{minutes_interval} min ago UTC")
minute_average_list = [(float(i[2]) + float(i[3])) / 2 for i in kl]


# %%
def get_historical_trades_mean(client, symbol: str, limit: int):
    last_trades = client.get_historical_trades(symbol=symbol, limit=limit)
    last_trades_prices = [float(p['price']) for p in last_trades]
    current_median = np.median(last_trades_prices)
    return current_median


def get_historical_trades_minute_interval_mean(client, symbol: str, minutes_interval: int):
    kl = client.get_historical_klines(symbol=symbol,
                                      interval=client.KLINE_INTERVAL_1MINUTE,
                                      start_str=f"{minutes_interval} min ago UTC")
    last_mean = [(float(i[2]) + float(i[3])) / 2 for i in kl]
    last_mean = np.mean(last_mean)
    return last_mean


import time
from datetime import datetime

minutes_interval = 10
round_time = 10
c = round(60 / round_time)
start_time = time.time()
# last_mean = False
while True:
    current_time = time.time()
    current_median = get_historical_trades_mean(client, symbol=initConfigs.symbol, limit=500)
    current_median_btc = get_historical_trades_mean(client, symbol='BTCUSDT', limit=500)
    print(f"time = {datetime.now().strftime('%d - %H:%M:%S')}")
    print(f'current_median = {current_median}')
    # print(f'current_median_btc = {current_median_btc}')
    if current_time - start_time > 60:
        last_mean = get_historical_trades_minute_interval_mean(client=client,
                                                               symbol=initConfigs.symbol,
                                                               minutes_interval=initConfigs.minutes_interval)

        last_mean_btc = get_historical_trades_minute_interval_mean(client=client,
                                                                   symbol='BTCUSDT',
                                                                   minutes_interval=initConfigs.minutes_interval)
        print(f'last_mean = {last_mean}')
    if last_mean:
        print(f'ratio {1 - last_mean / current_median :.3%}\n')
    # print(f'ratio {1 - last_mean_btc / current_median_btc :.3%} btc\n')

    time.sleep(round_time)

# %%
# %%
import time

from binance import ThreadedWebsocketManager
# %%
from binance.streams import ThreadedWebsocketManager
from recordclass import recordclass

from configs.api_configs import create_client_object
from get_real_time_data import GetRealTimeData
import json

# get initiation configs
configs_path = './configs/init_configs.json'

with open(configs_path, encoding='utf-8', errors='ignore') as json_file:
    initConfigs = json.load(json_file, object_hook=lambda d: recordclass('X', d.keys())(*d.values()))



api_key = 'CC7L3iSbyKzxJ95VfdW6HosTLE8wNf3OkHSHZ6y0uHjaRO8oK1CZCHuqzm9jnh7F'
api_secret = 'VirT3I8cY1FhVn3zURVYDc89RBvJulgDDEzmJcCKR3tKxjfqirZJLDe4ngN93sU4'

def main():

    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    twm.start()

    grtd = GetRealTimeData(save_data_path=initConfigs.save_real_time_data_path)

    # Clean or create path which we interest save data to
    grtd.clean_or_create_file_if_exist()

    twm.start_aggtrade_socket(callback=grtd._get_streaming_and_save_data_message, symbol=initConfigs.symbol)

    twm.join()


if __name__ == "__main__":
   main()