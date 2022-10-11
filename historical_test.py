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
    sp_data['cum_percent_change'] = (sp_data['close'] - sp_data['close'].iloc[0]) / sp_data['close'].iloc[0]
    sp_data = sp_data.fillna(0)

    sp_net = (100 * (sp_data['close'].iloc[-1] - sp_data['close'].iloc[0]) / sp_data['close'].iloc[0])

    return sp_data, sp_net


def test_strategy(df, show_stats = False):
    # gets data table with all relevant data
    all_stock = pd.DataFrame()
    for ticker in df.iterrows():
        stock_data = si.get_data(ticker[1]['ticker'], start_date = datetime.strptime(ticker[1]['buy_date'], '%Y-%m-%d'), end_date = datetime.strptime(ticker[1]['sell_date'], '%Y-%m-%d') + timedelta(days=1))
        stock_data['sale_index'] = ticker[0]
        stock_data['percent_change'] = (stock_data['close'] - stock_data['close'].iloc[0]) / stock_data['close'].iloc[0]
        stock_data['real_percent_change'] = stock_data['percent_change'] * ticker[1]['pct_importance']
        all_stock = all_stock.append(stock_data)
    all_stock = all_stock.fillna(0)

    # gets the daily growth of all stocks
    gains_per_stock = all_stock.groupby('sale_index')['real_percent_change'].last()
    grouped = all_stock.groupby(all_stock.index)['real_percent_change'].mean()

    # gets full stock growth
    for row in df.iterrows():
        grouped.loc[grouped.index > row[1]['sell_date']] = grouped.loc[grouped.index > row[1]['sell_date']] + gains_per_stock.loc[gains_per_stock.index == row[0]].values

    # gets overall growth of stratgey
    stocks_net = 100 * reduce(lambda y, z: y + z, (map(lambda x: df.iloc[x]['pct_importance'] * (all_stock.loc[(all_stock.index == df.iloc[x]['sell_date']) & (all_stock['ticker'] == df.iloc[x]['ticker'])][df.iloc[x]['buy_sell_time']].values[0] - all_stock.loc[(all_stock.index == df.iloc[x]['buy_date']) & (all_stock['ticker'] == df.iloc[x]['ticker'])][df.iloc[x]['buy_sell_time']].values[0]) / all_stock.loc[(all_stock.index == df.iloc[x]['buy_date']) & (all_stock['ticker'] == df.iloc[x]['ticker'])][df.iloc[x]['buy_sell_time']].values[0], df.index)))

    # gets s&p data
    sp_data = compare_sp(df['buy_date'].min(), df['sell_date'].max())


    plt.plot(sp_data[0].index, 100 * sp_data[0]['cum_percent_change'], label = 'S&P')
    plt.plot(grouped.index, 100 * grouped.values, label = 'TICKERS')
    plt.text(sp_data[0].loc[sp_data[0].index== sp_data[0].index.max()].index, 100 * sp_data[0].loc[sp_data[0].index == sp_data[0].index.max()]['cum_percent_change'], '({}, {})'.format(sp_data[0].loc[sp_data[0].index == sp_data[0].index.max()].index.date[0], round(100 * sp_data[0].loc[sp_data[0].index == sp_data[0].index.max()]['cum_percent_change'].values[0],2)))
    plt.text(grouped.loc[grouped.index == grouped.index.max()].index, 100 * grouped.loc[grouped.index == grouped.index.max()].values, '({}, {})'.format(grouped.loc[grouped.index == grouped.index.max()].index.date[0], round(100 * grouped.loc[grouped.index == grouped.index.max()].values[0],2)))
    plt.title("S&P500 GAIN: " + str(round(sp_data[1],2)) + "% | TICKERS GAIN: " + str(round(stocks_net, 2)) + "%")
    plt.xlabel('Date')
    plt.ylabel('Percent Change')
    plt.legend()
    plt.show()





test_strategy(df)
