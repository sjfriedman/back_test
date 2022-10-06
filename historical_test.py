from datetime import datetime, date, timedelta
from functools import reduce
from yahoo_fin import stock_info as si
import day_cache as cache
import matplotlib.pyplot as plt
import pandas as pd


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


# df = ['ticker']['buy_date']['sell_date']['buy_sell_time']['pct_importance']



df = pd.read_csv('/Users/SamFriedman/Downloads/sample_df - Sheet1.csv')
print(df)


def compare_sp(s_date, e_date):
    sp_data = cache.get('sp', 'market')
    if sp_data is None:
        sp_data = si.get_data('^GSPC')
        cache.set('sp', 'market', sp_data)

    if not s_date:
        s_date = str(sp_data.index[0].date())

    sp_data = sp_data.loc[datetime.strptime(s_date, '%Y-%m-%d') : datetime.strptime(e_date, '%Y-%m-%d')]
    sp_data['cum_percent_change'] = ((sp_data['close'])).pct_change().cumsum()
    sp_data = sp_data.fillna(0)

    sp_net = (100 * (sp_data['close'].iloc[-1] - sp_data['close'].iloc[0]) / sp_data['close'].iloc[0])

    return sp_data, str(sp_net)


def test_strategy(df, show_stats = False):
    # gets data table with all relevant data
    all_stock = pd.DataFrame()
    for ticker in df.iterrows():
        stock_data = si.get_data(ticker[1]['ticker'], start_date = datetime.strptime(ticker[1]['buy_date'], '%Y-%m-%d'), end_date = datetime.strptime(ticker[1]['sell_date'], '%Y-%m-%d') + timedelta(days=1))
        stock_data['percent_change'] = (stock_data[ticker[1]['buy_sell_time']]).pct_change().cumsum()
        stock_data['real_percent_change'] = stock_data['percent_change'] * ticker[1]['pct_importance']
        all_stock = all_stock.append(stock_data)
    all_stock = all_stock.fillna(0)

    # gets the daily growth of all stocks
    grouped = all_stock.groupby(all_stock.index)['real_percent_change'].mean()

    # # gets overall growth of stratgey
    stocks_net = reduce(lambda y, z: y + z, (map(lambda x: df.iloc[x]['pct_importance'] * (all_stock.loc[(all_stock.index == df.iloc[x]['sell_date']) & (all_stock['ticker'] == df.iloc[x]['ticker'])][df.iloc[x]['buy_sell_time']].values[0] - all_stock.loc[(all_stock.index == df.iloc[x]['buy_date']) & (all_stock['ticker'] == df.iloc[x]['ticker'])][df.iloc[x]['buy_sell_time']].values[0]) / all_stock.loc[(all_stock.index == df.iloc[x]['buy_date']) & (all_stock['ticker'] == df.iloc[x]['ticker'])][df.iloc[x]['buy_sell_time']].values[0], df.index)))

    # gets s&p data
    sp_data = compare_sp(df['buy_date'].min(), df['sell_date'].max())


    plt.plot(sp_data[0].index, sp_data[0]['cum_percent_change'], label = 'S&P')
    plt.plot(grouped.index, grouped.values, label = 'TICKERS')
    plt.title("S&P500 GAIN:" + sp_data[1] + " | TICKERS GAIN: " + str(round(stocks_net, 5)) + "%")
    plt.xlabel('Date')
    plt.ylabel('Percent Change')
    plt.legend()
    plt.show()





test_strategy(df)
