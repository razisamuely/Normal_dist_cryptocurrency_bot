import pandas as pd
from typing import List
from scipy.stats import norm

class calculateBuySell(object):
    def __init__(self, json_list: List[dict], q_w_w: float, t_w_w: float, sale_ratio: float, prob: float):
        self.json_list = json_list
        self.df: pd = self.convert_json_list_to_pddf_sort_and_convert_to_float(self.json_list)
        self.price_weighted: float = self.quantity_position_wighted_sum(dfi=self.df, q_w_w=q_w_w, t_w_w=t_w_w)
        self.price_std: float = self.df['price'].std()
        self.buy: float = norm(self.price_weighted, self.price_std).ppf(prob)
        self.sell: float = self.buy * sale_ratio

    def convert_json_list_to_pddf_sort_and_convert_to_float(self, json_list: List[dict]):
        df = pd.DataFrame(json_list)
        df['qty'] = df['qty'].astype(float)
        df['price'] = df['price'].astype(float)
        df = df.sort_values(by='time')
        return df

    def quantity_position_wighted_sum(self, dfi: pd, q_w_w: float = 0, t_w_w: float = 1):
        if round(1 - q_w_w, 2) != round(t_w_w, 2):
            print(f' sum of q_aw_w + t_w_w is {q_w_w + t_w_w} != 1, make sure its sum up to 1')

        else:

            # sum quantity in time interval
            q_s = dfi['qty'].sum()

            # calculation on samples length and positions sum
            kl = dfi.shape[0]
            ari_sum = kl * (1 + kl) / 2

            # quantity weights
            q_w = dfi['qty'].values / q_s

            # time weights
            t_w = pd.Series(range(1, kl + 1)) / ari_sum

            # extract price values
            c_p = dfi['price'].values

            # apply additional weights to time and quantity
            final_weights = q_w_w * q_w + t_w_w * t_w

            # calculate weighted sum
            pqts = sum(c_p * final_weights)

        return pqts