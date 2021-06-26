# %%
import json
from configs.api_configs import create_client_object
from recordclass import recordclass
from precetile_management_class import PercentileMenagmant
import time
from datetime import datetime

configs_path = './configs/init_configs.json'

with open(configs_path, encoding='utf-8', errors='ignore') as json_file:
    initConfigs = json.load(json_file, object_hook=lambda d: recordclass('X', d.keys())(*d.values()))

client = create_client_object(keys_path=initConfigs.keys_path,
                              configs_name=initConfigs.configs_name,
                              is_demo=initConfigs.is_demo)

pm = PercentileMenagmant()
start_time = time.time()
times_stop = []
while True:
    try:
        current_time = time.time()
        initConfigs = pm.get_initConfigs(configs_path)

        if (current_time - start_time > 60) or (current_time - start_time < 1):
            print(f"current_time - start_time = {current_time - start_time}")
            start_time = current_time
            klines = pm.get_historical_klines(client=client,
                                              symbol=initConfigs.symbol,
                                              interval=client.KLINE_INTERVAL_1MINUTE,
                                              start_str=f"{initConfigs.probability_hours_back} hours ago UTC")

            klines_last_n_minutes = klines[::-1][0:initConfigs.minutes_interval]
            last_mean = pm.get_historical_trades_minute_interval_mean(klines=klines_last_n_minutes)

        current_median = pm.get_historical_trades_mean(client,
                                                       symbol=initConfigs.symbol,
                                                       limit=initConfigs.last_historical_trades_number)
        movement_ration = round(1 - last_mean / current_median, 3)

        probability, percentile = pm.calculate_probability_and_percentile(
            klines=klines,
            current_median=current_median,
            prob_lower=initConfigs.prob_lower,
            prob_upper=initConfigs.prob_upper)

        initConfigs.probability = probability
        current_switch = int((percentile > initConfigs.min_percentile_to_stop_trading) and (
                movement_ration > initConfigs.movement_ration_lower_bound))

        if initConfigs.buy_switch != current_switch:
            print(f'initConfigs.buy_switch {initConfigs.buy_switch}, current_switch = {current_switch}')
            initConfigs.buy_switch = current_switch
            pm.save_initConfigs(configs_path=configs_path, initConfigs=initConfigs)

        pm.print_summary_and(initConfigs=initConfigs,
                             klines=klines,
                             current_median=current_median,
                             percentile=percentile,
                             movement_ration=movement_ration)

        if movement_ration <= -0.01:
            times_stop.append((False, movement_ration, datetime.now().strftime('%d - %H:%M:%S')))
            print(times_stop)
        time.sleep(10)

    except:
        # if failed, set the lower probability
        initConfigs.probability = initConfigs.prob_lower
        with open(configs_path, 'w') as outfile:
            json.dump(json.loads(json.dumps(initConfigs.__dict__)), outfile)

        print(f'something went wrong, placed probability to sell = {initConfigs.prob_lower}')
        time.sleep(2)
#
# %%
