from datetime import datetime, date
from functools import reduce
from yahoo_fin import stock_info as si
import day_cache as cache
import matplotlib.pyplot as plt
import pandas as pd


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


def single_stock_compare_sp500(ticker, s_date = None, e_date = str(date.today())):
    # sets sp_data to all S&P data
    sp_data = cache.get('sp', 'market')
    if sp_data is not None:
        sp_data = si.get_data('^GSPC')
        cache.set('sp', 'market', sp_data)

    if not s_date:
        s_date = str(sp_data.index[0].date())


    # Gets stock data
    stock_data = si.get_data(ticker, start_date = datetime.strptime(s_date, '%Y-%m-%d'), end_date = datetime.strptime(e_date, '%Y-%m-%d'))
    stock_data['cum_percent_change'] = (stock_data['close'] - stock_data['close'].iloc[0]) / stock_data['close'].iloc[0]
    stock_data = stock_data.fillna(0)

    # Makes sure to get S&P data for same dates as stock
    s_date = str(stock_data.index[0].date())

    # Gets S&P data for datetime and increment
    sp_data = sp_data.loc[datetime.strptime(s_date, '%Y-%m-%d') : datetime.strptime(e_date, '%Y-%m-%d')]
    sp_data['cum_percent_change'] = (sp_data['close'] - sp_data['close'].iloc[0]) / sp_data['close'].iloc[0]
    sp_data = sp_data.fillna(0)

    # calculates total percent change of S&P and Stock
    sp_net = (100 * (sp_data['close'].iloc[-1] - sp_data['close'].iloc[0]) / sp_data['close'].iloc[0])
    stock_net = (100 * (stock_data['close'].iloc[-1] - stock_data['close'].iloc[0]) / stock_data['close'].iloc[0])

    # Plots data points
    plt.plot(sp_data.index,100 * sp_data['cum_percent_change'], label = 'S&P')
    plt.plot(stock_data.index, 100 * stock_data['cum_percent_change'], label = 'ticker'.upper())
    plt.title("S&P GAIN: " + str(round(sp_net, 2)) + "% | " + ticker.upper() + " GAIN: " + str(round(stock_net, 2)) + "%")
    plt.text(sp_data.loc[sp_data.index == sp_data.index.max()].index, 100 * sp_data.loc[sp_data.index == sp_data.index.max()]['cum_percent_change'], '({}, {})'.format(sp_data.loc[sp_data.index == sp_data.index.max()].index.date[0], round(100 * sp_data.loc[sp_data.index == sp_data.index.max()]['cum_percent_change'].values[0],2)))
    plt.text(stock_data.loc[stock_data.index == stock_data.index.max()].index, 100 * stock_data.loc[stock_data.index == stock_data.index.max()]['cum_percent_change'], '({}, {})'.format(stock_data.loc[stock_data.index == stock_data.index.max()].index.date[0], round(100 * stock_data.loc[stock_data.index == stock_data.index.max()]['cum_percent_change'].values[0],2)))
    plt.xlabel('Date')
    plt.ylabel('Percent Change')
    plt.legend()
    plt.show()

def multi_stock_compare_sp500(tickers, s_date, e_date = str(date.today())):
    # sets sp_data to all S&P data
    sp_data = cache.get('sp', 'market')
    if sp_data is None:
        sp_data = si.get_data('^GSPC')
        cache.set('sp', 'market', sp_data)

    if not s_date:
        s_date = str(sp_data.index[0].date())

    # Gets stock data
    all_stock = pd.DataFrame()
    for ticker in tickers:
        stock_data = si.get_data(ticker, start_date = datetime.strptime(s_date, '%Y-%m-%d'), end_date = datetime.strptime(e_date, '%Y-%m-%d'))
        stock_data['cum_percent_change'] = (stock_data['close'] - stock_data['close'].iloc[0]) / stock_data['close'].iloc[0]
        all_stock = all_stock.append(stock_data)
    grouped = all_stock.groupby(all_stock.index)['cum_percent_change'].mean()
    grouped = grouped.fillna(0)

    # Gets S&P data for datetime and increment
    sp_data = sp_data.loc[datetime.strptime(s_date, '%Y-%m-%d') : datetime.strptime(e_date, '%Y-%m-%d')]
    sp_data['cum_percent_change'] = (sp_data['close'] - sp_data['close'].iloc[0]) / sp_data['close'].iloc[0]

    sp_net = (100 * (sp_data['close'].iloc[-1] - sp_data['close'].iloc[0]) / sp_data['close'].iloc[0])
    stocks_net = 100 * reduce(lambda y, z: y + z, (map(lambda x: (all_stock.loc[(all_stock.index == all_stock.index.max()) & (all_stock['ticker'] == x.upper())]['close'].values[0] - all_stock.loc[(all_stock.index == all_stock.index.min()) & (all_stock['ticker'] == x.upper())]['close'].values[0]) / all_stock.loc[(all_stock.index == all_stock.index.min()) & (all_stock['ticker'] == x.upper())]['close'].values[0], tickers))) / len(tickers)

    plt.plot(sp_data.index,100 * sp_data['cum_percent_change'], label = 'S&P')
    plt.plot(grouped.index, 100 * grouped.values, label = 'TICKERS')
    plt.text(sp_data.loc[sp_data.index == sp_data.index.max()].index, 100 * sp_data.loc[sp_data.index == sp_data.index.max()]['cum_percent_change'], '({}, {})'.format(sp_data.loc[sp_data.index == sp_data.index.max()].index.date[0], round(100 * sp_data.loc[sp_data.index == sp_data.index.max()]['cum_percent_change'].values[0],2)))
    plt.text(grouped.loc[grouped.index == grouped.index.max()].index, 100 * grouped.loc[grouped.index == grouped.index.max()].values, '({}, {})'.format(grouped.loc[grouped.index == grouped.index.max()].index.date[0], round(100 * grouped.loc[grouped.index == grouped.index.max()].values[0],2)))
    plt.title("S&P GAIN: " + str(round(sp_net, 2)) + "% | TICKERS GAIN: " + str(round(stocks_net, 2)) + "%")
    plt.xlabel('Date')
    plt.ylabel('Percent Change')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    single_stock_compare_sp500('aapl', '2022-01-04', '2022-10-6')
    single_stock_compare_sp500('aapl')
    multi_stock_compare_sp500(['aapl', 'msft', 'tsla', 'abnb'], '2022-01-04', '2022-10-06')


#
