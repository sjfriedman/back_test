from datetime import datetime, date
from yahoo_fin import stock_info as si
import day_cache as cache
import matplotlib.pyplot as plt
import pandas as pd


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


def single_stock_compare_sp500(ticker, s_date = '1985-01-01', e_date = str(date.today())):
    # sets sp_data to all S&P data
    sp_data = cache.get('sp', 'market')
    if sp_data is None:
        sp_data = si.get_data('^GSPC')
        cache.set('sp', 'market', sp_data)

    # Gets S&P data for datetime and increment
    sp_data = sp_data.loc[datetime.strptime(s_date, '%Y-%m-%d') : datetime.strptime(e_date, '%Y-%m-%d')]
    sp_data['cum_percent_change'] = ((sp_data['close'])).pct_change().cumsum()
    sp_data = sp_data.fillna(0)

    # Gets stock data
    stock_data = si.get_data(ticker, start_date = datetime.strptime(s_date, '%Y-%m-%d'), end_date = datetime.strptime(e_date, '%Y-%m-%d'))
    stock_data['cum_percent_change'] = (stock_data['close']).pct_change().cumsum()
    stock_data = stock_data.fillna(0)

    # Plots data points
    plt.plot(sp_data.index,sp_data['cum_percent_change'], label = 'S&P')
    plt.plot(stock_data.index, stock_data['cum_percent_change'], label = 'ticker'.upper())
    plt.title("S&P GAIN: " + str(round((100 * (sp_data['close'].iloc[-1] - sp_data['close'].iloc[0]) / sp_data['close'].iloc[0]), 2)) + "% | " + ticker.upper() + " GAIN: " + str(round((100 * (stock_data['close'].iloc[-1] - stock_data['close'].iloc[0]) / stock_data['close'].iloc[0]), 2)) + "%")
    plt.xlabel('Date')
    plt.ylabel('Percent Change')
    plt.legend()
    plt.show()



if __name__ == "__main__":
    print(single_stock_compare_sp500('aapl', '2022-01-04', '2022-10-05'))
    # print(single_stock_compare_sp500('aapl'))
