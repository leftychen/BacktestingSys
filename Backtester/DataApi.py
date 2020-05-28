import datetime
import pandas as pd
import os
import numpy as np

class DataApi:
    def __init__(self):
        # load factors
        path = os.path.join(os.getcwd(), 'Data/FACTOR.csv')
        factors = pd.read_csv(path, index_col=0)
        self.factors = factors

        # load forward returns
        path = os.path.join(os.getcwd(), 'Data/FMRTN1W.csv')
        rt = pd.read_csv(path, index_col=0)
        self.returns = rt

        self.__Dates = [datetime.datetime.strptime(d, '%Y%m%d') for d in self.factors.columns.values]
        self.__Dates = np.intersect1d(self.Dates, [datetime.datetime.strptime(d, '%Y%m%d') for d in self.returns.columns.values])

    def get_factor(self, date: datetime.datetime):
        assert (isinstance(date, datetime.datetime))
        datestr = date.strftime('%Y%m%d')
        return self.factors[datestr]

    def get_returns(self, date: datetime.datetime):
        assert (isinstance(date, datetime.datetime))
        datestr = date.strftime('%Y%m%d')
        return self.returns[datestr]

    def get_stock_ids(self):
        return self.factors.index

    def check_data(self, date):
        if date in self.Dates:
            return True
        else:
            return False
    @property
    def Dates(self):
        return self.__Dates.copy()
