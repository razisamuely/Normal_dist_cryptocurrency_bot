import pandas  as pd
from binance.client import Client


def create_client_object(configs_name, keys_path, is_demo: bool = True, return_keys: bool = False):
    keys = pd.read_csv(keys_path)
    api_key = keys[keys['owner'] == configs_name]['public'].values[0]
    api_secret = keys[keys['owner'] == configs_name]['secret'].values[0]
    client = Client(api_key, api_secret)
    if is_demo:
        client.API_URL = 'https://testnet.binance.vision/api'
    if not return_keys:
        return client
    else:
        return client, api_key, api_secret
