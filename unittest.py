from Backtester.Backtest import Backtest,DataApi
import pandas as pd
import numpy as np
import datetime


def initialize(context):
    context.i = 0
    context.assets = 'all'


def handle_data(context, data):
    # check data
    if not data.check_data(context.rundate):
        return

    factors = data.get_factor(context.rundate)
    # clean up data
    select_factors = factors.dropna()
    # sort factors
    sort_factors = select_factors.sort_values()
    # quantile factors
    quantiles = pd.qcut(sort_factors, 5, labels=range(5))
    quantiles.name = 'quantiles'
    sort_factors = pd.DataFrame(sort_factors).join(quantiles)

    # last quantile
    last_quantile = sort_factors[sort_factors['quantiles'] == 0]
    # first quantile
    first_quantile = sort_factors[sort_factors['quantiles'] == 4]
    context.position.position = np.zeros((len(context.position.values), 1))
    # assign position to last quantile
    # reduce one position
    last_quantile_index = np.in1d(context.position.position.index.values, last_quantile.index.values)
    context.position.position[last_quantile_index] = np.maximum(-1, context.position.position[last_quantile_index] - 1)

    # assign position to first quantile
    # add one position
    first_quantile_index = np.in1d(context.position.position.index.values, first_quantile.index.values)
    context.position.position[first_quantile_index] = np.minimum(1, context.position.position[first_quantile_index] + 1)
    context.i += 1


if __name__ == '__main__':
    Backtest.handle_data = handle_data
    Backtest.initialize = initialize
    platform = Backtest()
    data = DataApi()
    dates = data.Dates
    platform.run(dates=dates)
