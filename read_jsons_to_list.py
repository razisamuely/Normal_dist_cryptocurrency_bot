# %%
import time
import json
from utils.calculate_buy_sell import calculateBuySell
from configs.api_configs import create_client_object
import gc
from recordclass import recordclass
from place_buy_order_class import PlaceBuyOrder
from typing import List
from datetime import datetime

configs_path = './configs/init_configs.json'

with open(configs_path, encoding='utf-8', errors='ignore') as json_file:
    initConfigs = json.load(json_file, object_hook=lambda d: recordclass('X', d.keys())(*d.values()))

tradesList = initConfigs.tradesList
place_order = initConfigs.place_order

client = create_client_object(keys_path=initConfigs.keys_path,
                              configs_name=initConfigs.configs_name,
                              is_demo=initConfigs.is_demo)

bpo = PlaceBuyOrder(symbol=initConfigs.symbol)

# 1 delete historical data
bpo.clean_or_create_file_if_exist(directory=initConfigs.data_for_research_path)
bpo.clean_or_create_file_if_exist(directory=initConfigs.order_tracking_path)

while initConfigs.read_json_to_list_switch:

    initConfigs = bpo.load_json(path=configs_path, sleep=0.01)

    files = bpo.get_and_sort_real_time_files_names(initConfigs.save_real_time_data_path)
    if len(files):

        tradesList: List[dict] = bpo.read_append_remove_file(tradesList=tradesList,
                                                             save_real_time_data_path=initConfigs.save_real_time_data_path,
                                                             files=files)

        tradesList = bpo.cut_under_window_time_quotes(tradesList=tradesList,
                                                      order_time_window=initConfigs.order_time_window)

        calculate_buy_sell = calculateBuySell(json_list=tradesList,
                                              q_w_w=initConfigs.q_w_w,
                                              t_w_w=initConfigs.t_w_w,
                                              sale_ratio=initConfigs.sale_ratio,
                                              prob=initConfigs.probability,
                                              )

        tradesList[-1]['buy']: dict = calculate_buy_sell.buy
        tradesList[-1]['sell']: dict = calculate_buy_sell.sell

        bpo.save_data_for_investigation(tradesList=tradesList,
                                        path=initConfigs.data_for_research_path,
                                        switch=initConfigs.save_data_for_investigation_switch)
        switch = bpo.get_order_witch(manage_orders_path=initConfigs.manage_orders_path)

        place_order = switch['place_order']

        # switch = bpo.get_order_witch(manage_orders_path=initConfigs.manage_orders_path)

        # place_order = switch['place_order']
        last_data_point = tradesList[-1]

        bpo.print_status_message(last_data_point=last_data_point, place_order=place_order)

        if (place_order) and (initConfigs.buy_switch) > 0:
            place_order = False
            buy_price = round(last_data_point['buy'], initConfigs.place_order_decimal_points)
            order = bpo.buy(client=client,initConfigs=initConfigs, buy_price=buy_price, last_data_point=last_data_point)
            if order:
                bpo.write_order_tracking(order=order, last_data_point=last_data_point,
                                         order_tracking_path=initConfigs.order_tracking_path)

                print(f"\n-- MASSAGE = Order placed, taking {initConfigs.buy_sleep_time} secondes of zzZZ - "
                      f"order price = {buy_price}, order id = {order['orderId']}, "
                      f"time = {datetime.now().strftime('%d - %H:%M:%S')} --\n")

                time.sleep(initConfigs.buy_sleep_time)
                place_order = False

        else:
            gc.collect()
            time.sleep(0.5)
