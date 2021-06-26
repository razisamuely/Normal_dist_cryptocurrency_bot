# %%
import json
import time
from configs.api_configs import create_client_object
import gc
from managed_filled_orders_class import ManageFilledOrders
from recordclass import recordclass
from datetime import datetime

configs_path = './configs/init_configs.json'

with open(configs_path, encoding='utf-8', errors='ignore') as json_file:
    initConfigs = json.load(json_file, object_hook=lambda d: recordclass('X', d.keys())(*d.values()))

client = create_client_object(keys_path=initConfigs.keys_path,
                              configs_name=initConfigs.configs_name,
                              is_demo=initConfigs.is_demo)

mfo = ManageFilledOrders(symbol=initConfigs.symbol)

all_orders, sell_orders, buy_orders = mfo.get_all_buy_sell_orders(client=client,
                                                                  symbol=initConfigs.symbol)

while True:
    all_orders = mfo.get_all_orders(client, symbol=initConfigs.symbol, sleep_time_seconds=1)

    for p, order in enumerate(all_orders):
        orderId = order['orderId']
        orderStatus = order['status']
        orderSide = order['side']

        if orderStatus == 'FILLED':
            sell_order = False
            if (orderSide == 'BUY') and (orderId not in buy_orders):
                buy_orders.append(orderId)
                filled_order_i = mfo.load_buy_filled_order_properties(orderId=orderId,
                                                                      order_tracking_path=initConfigs.order_tracking_path,
                                                                      get_sleep_time=0.01)

                sellPrice = round(filled_order_i['sell'], initConfigs.place_order_decimal_points)

                sell_order = mfo.set_sell_order(client=client,
                                                quantity=initConfigs.quantity,
                                                sellPrice=sellPrice,
                                                symbol=initConfigs.symbol,
                                                number_of_attempts=5,
                                                reduce_quantity=0.01,
                                                sell_decimal_points=3)



                if sell_order:
                    sell_order = False
                    counter = mfo.add_subtract_counter(counter_path=initConfigs.counter_path, add_subtract=1)
                    print(f"\nsell order set, sellPrice = {sellPrice}, time = {datetime.now().strftime('%d - %H:%M:%S')}")
                    print(f'sell orders pull = {counter}')

            if (orderSide == 'SELL') and (orderId not in sell_orders):
                sell_orders.append(orderId)
                counter = mfo.add_subtract_counter(counter_path=initConfigs.counter_path, add_subtract=-1)
                transactions_counter = mfo.update_initConfigs_transaction_counter(configs_path)
                print(f"\nsell order satisfied, Price = {order['price']}, time = {datetime.now().strftime('%d - %H:%M:%S')}")
                print(f'sell orders pull = {counter}, transactions_counter ={transactions_counter}')


    gc.collect()
    time.sleep(2)
#348 19 - 22:59:24