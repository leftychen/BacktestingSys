import pandas as pd
import datetime
import numpy as np
import  matplotlib.pyplot as plt


def show_converage(hists_positions):
    stock_ids = []
    stock_cnt = []
    dates = []
    cols = hists_positions.columns.values
    for col in cols:
        if str.lower(col) == 'initial':
            continue
        datadate = datetime.datetime.strptime(col, '%Y%m%d')
        pos = hists_positions[col]
        ids = pos.index[np.squeeze(pos.values != 0)]

        if len(stock_ids) == 0:
            stock_ids = ids
            stock_cnt.append(len(stock_ids))
            dates.append(datadate)
        else:
            stock_ids = stock_ids.append(ids[~ ids.isin(stock_ids)])
            stock_cnt.append(len(stock_ids))
            dates.append(datadate)
    coverages = pd.DataFrame(stock_cnt, index=dates, columns=['Coverage'])
    #moveavg = coverages.Coverage.rolling(window=365).mean()
    moveavg = coverages.Coverage.rolling(window=52).mean()
    fig, ax = plt.subplots()
    ax.bar(dates, coverages.Coverage.values, label='Stock Coverage Count', width=6, color='springgreen')
    ax.plot(coverages.index, moveavg, label='12 months moving average')
    ax.set_ylabel('# Stocks')
    ax.set_title('Coverage of Portfolio')
    ax.legend()
    fig.tight_layout()
    plt.show()
    return coverages


def return_analysis(data, cum_return):
    dates = data.Dates
    quant_rets_array = [np.ones((1,5))]
    for date in dates:
        factors = data.get_factor(date)
        # clean up data
        select_factors = factors.dropna()
        # sort factors
        sort_factors = select_factors.sort_values()
        # quantile factors
        quantiles = pd.qcut(sort_factors, 5, labels=range(1,6))
        quantiles.name = 'quantiles'
        sort_factors = pd.DataFrame(sort_factors).join(quantiles)
        rts = data.get_returns(date)
        rts = rts + 1
        sort_factors = sort_factors.join(rts, rsuffix='_returns')
        a = sort_factors.groupby('quantiles').count()
        b = sort_factors.groupby('quantiles').sum()
        ret = b.iloc[:,-1] / a.iloc[:,-1].values
        quant_rets_array.append(ret.values)
    quant_rets_array = np.squeeze(quant_rets_array)
    dates_str = [p.strftime('%Y%m%d') for p in dates]
    dates_str.insert(0, 'basic')
    report = pd.DataFrame(np.vstack(quant_rets_array), index=dates_str, columns=['quantile1_rt','quantile2_rt','quantile3_rt','quantile4_rt','quantile5_rt'])
    report['L/S_rt'] = cum_return.values
    # annualized return

    report.to_csv('./weekly_return_analysis.csv', index_label='Dates')

