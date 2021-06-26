import time
import json

from recordclass import recordclass


class UserDefinedDecorators(object):

    def __init__(self, retries_cuonter: int):
        self.retries_cuonter = retries_cuonter

    def retry_function(self, function):
        '''
        Retry decorator, before using init UserDefinedDecorators with number of retries
        :param function: Some function
        :return:
        '''

        def wrapper(*args, **kwargs):
            retries_cuonter = self.retries_cuonter
            while retries_cuonter > 0:
                try:
                    func_response = function(*args, **kwargs)
                    break  # <- breaks the while loop if success
                except:
                    retries_cuonter -= 1
                    print(retries_cuonter)
                    func_response = None
            return func_response

        return wrapper


class ConfigsTools(object):
    ud = UserDefinedDecorators(retries_cuonter=10)

    @ud.retry_function
    def get_initConfigs(self, initConfigs_path: str):
        with open(initConfigs_path, encoding='utf-8', errors='ignore') as json_file:
            initConfigs = json.load(json_file, object_hook=lambda d: recordclass('X', d.keys())(*d.values()))
        return initConfigs

    @ud.retry_function
    def save_initConfigs(self, configs_path: str, initConfigs):

        while True:
            try:
                with open(configs_path, 'w') as outfile:
                    json.dump(json.loads(json.dumps(initConfigs.__dict__)), outfile)
                    break
            except:
                time.sleep(0.01)
        return initConfigs


# %%
ConfigsTools().get_initConfigs('')
