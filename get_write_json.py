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

# Create "Binance" client object
client, api_key, api_secret = create_client_object(keys_path=initConfigs.keys_path,
                                                   configs_name=initConfigs.configs_name,
                                                   is_demo=initConfigs.is_demo,
                                                   return_keys=True)



twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
twm.start()

# Initiate GetRealTimeData class
grtd = GetRealTimeData(save_data_path=initConfigs.save_real_time_data_path)
# Clean or create path which we interest save data to
grtd.clean_or_create_file_if_exist()

twm.start_aggtrade_socket(callback=grtd._get_streaming_and_save_data_message, symbol=initConfigs.symbol)

twm.join()
