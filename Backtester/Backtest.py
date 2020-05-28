import pandas as pd
import numpy as np
from Backtester.DataApi import DataApi
from Backtester.AnalyticToolBox import show_converage,return_analysis
import datetime
import logging


class Backtest:
    def __init__(self, initial_capital=1):
        self.__capital = initial_capital
        self.__assets = []

    @property
    def assets(self):
        return self.__assets

    @assets.setter
    def assets(self, symbol):
        self.__assets.append(symbol)

    # initialzed the data such as clean up or data conversion
    def initialize(self):
        pass

    # handle how to deal with input data
    def handle_data(self, data):
        pass

    def analyze(self):
        pass

    def __initialtracking(self, data):
        # initialized
        if self.__assets[0] == 'all':
            stock_ids = data.get_stock_ids()
            self.position = pd.DataFrame(np.zeros((len(stock_ids), 1)), index=stock_ids, columns=['position'])
            self.histposition = pd.DataFrame(np.zeros((len(stock_ids), 1)), index=stock_ids, columns=['initial'])
            self.cum_returns = pd.DataFrame(np.ones((len(stock_ids), 1)), index=stock_ids, columns=['initial'])
            self.port_retuns_details = pd.DataFrame([], index=stock_ids)
            self.port_return = pd.Series()
            self.port_return['basic'] = 1
            self.netvalue = pd.Series()
            self.netvalue['basic'] = self.__capital
        else:
            pass

    def __calPL(self, data):

        # hold asset
        longPos = np.squeeze(self.position.values == 1)

        # short asset
        shortPos = np.squeeze(self.position.values == -1)

        newpl = self.cum_returns.iloc[:, -1].values.copy()
        update_rts = np.zeros((len(newpl),))

        # calculate long position
        if data.check_data(self.rundate):
            rts = data.get_returns(self.rundate)
            newpl[longPos] = np.maximum(newpl[longPos] * (1 + rts.values[longPos]), 0)
            update_rts[longPos] = rts.values[longPos]
            # calculate short position
            newpl[shortPos] = np.maximum(newpl[shortPos] * (1 - rts.values[shortPos]), 0)
            update_rts[shortPos] = rts.values[shortPos]

        initalvalue = self.cum_returns.iloc[:, 0].values.sum()
        currvalue = (self.__capital / initalvalue) * newpl.sum()
        self.netvalue[self.rundate.strftime('%Y%m%d')] = currvalue
        update_rts = update_rts + 1
        self.port_return[self.rundate.strftime('%Y%m%d')] = (self.__capital / initalvalue) * update_rts.sum()

        # add pl to total
        self.cum_returns[self.rundate.strftime('%Y%m%d')] = newpl
        self.port_retuns_details[self.rundate.strftime('%Y%m%d')] = update_rts

    def run(self, startdate=None, enddate=None, dates=None, datasource=None):
        if not datasource:
            data = DataApi()
        else:
            data = datasource

        self.rundate = dates[0]
        self.initialize()
        self.__initialtracking(data)

        try:
            # trigger strategy
            #while self.rundate <= enddate:
            for date in dates:
                self.rundate = date
                self.handle_data(data)
                logging.info('Finish Date ' + self.rundate.strftime('%Y-%m-%d'))
                self.__calPL(data)
                self.histposition[self.rundate.strftime('%Y%m%d')] = self.position.values
                self.rundate += datetime.timedelta(1)
            # analysis performance
            # show_converage(self.histposition)
            return_analysis(data, self.port_return)


        except Exception as e:
            logging.error('Error at %s', 'division', exc_info=e)
