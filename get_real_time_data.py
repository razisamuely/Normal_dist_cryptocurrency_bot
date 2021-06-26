import json
import os
import time


class GetRealTimeData(object):
    def __init__(self, save_data_path: str):
        self._counter = 0
        self._save_data_path = save_data_path

    def clean_or_create_file_if_exist(self):
        if os.path.exists(self._save_data_path):
            files = os.listdir(self._save_data_path)
            for f in files:
                os.remove(self._save_data_path + f)
        else:
            os.makedirs(self._save_data_path)

    def _get_streaming_and_save_data_message(self, msg: json):
        self._counter += 1

        trade = {
            "id": msg['a'],
            "price": msg['p'],
            "qty": msg['q'],
            "time": msg['T'],
            "isBuyerMaker": msg['m']
        }
        print('counter = ', self._counter, "trade['price'] = ", trade['price'])

        # Append last trade to tradesList
        with open(f'{self._save_data_path}/{self._counter}.txt', 'w') as outfile:
            json.dump(trade, outfile)




