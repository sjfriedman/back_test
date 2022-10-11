from datetime import datetime, date, timedelta
from functools import reduce
from yahoo_fin import stock_info as si
import compare_to_market as ctm
import matplotlib.pyplot as plt
import pandas as pd


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


df = pd.read_csv('/Users/SamFriedman/Downloads/sample_df - Sheet1.csv')
print(df)

def test_strategy(df, market, show_stats = False):
    # gets data table with all relevant data
    all_stock = pd.DataFrame()
    for ticker in df.iterrows():
        stock_data = si.get_data(ticker[1]['ticker'], start_date = datetime.strptime(ticker[1]['buy_date'], '%Y-%m-%d'), end_date = datetime.strptime(ticker[1]['sell_date'], '%Y-%m-%d') + timedelta(days=1))
        stock_data['sale_index'] = ticker[0]
        stock_data['percent_change'] = (stock_data[ticker[1]['sell_time']] - stock_data[ticker[1]['buy_time']].iloc[0]) / stock_data[ticker[1]['buy_time']].iloc[0]
        stock_data['real_percent_change'] = stock_data['percent_change'] * ticker[1]['pct_importance']
        all_stock = all_stock.append(stock_data)
    all_stock = all_stock.fillna(0)

    # gets the daily growth of all stocks
    gains_per_stock = all_stock.groupby('sale_index')['real_percent_change'].last()
    grouped = all_stock.groupby(all_stock.index)['real_percent_change'].mean()

    print(gains_per_stock)
    # gets full stock growth
    for row in df.iterrows():
        grouped.loc[grouped.index > row[1]['sell_date']] = grouped.loc[grouped.index > row[1]['sell_date']] + gains_per_stock.loc[gains_per_stock.index == row[0]].values

    # gets overall growth of stratgey
    stocks_net = 100 * reduce(lambda y, z: y + z, (map(lambda x: df.iloc[x]['pct_importance'] * (all_stock.loc[(all_stock.index == df.iloc[x]['sell_date']) & (all_stock['ticker'] == df.iloc[x]['ticker'])][df.iloc[x]['sell_time']].values[0] - all_stock.loc[(all_stock.index == df.iloc[x]['buy_date']) & (all_stock['ticker'] == df.iloc[x]['ticker'])][df.iloc[x]['buy_time']].values[0]) / all_stock.loc[(all_stock.index == df.iloc[x]['buy_date']) & (all_stock['ticker'] == df.iloc[x]['ticker'])][df.iloc[x]['buy_time']].values[0], df.index)))

    # gets s&p data
    market_date = ctm.compare_market(market, df['buy_date'].min(), df['sell_date'].max())

    plt.plot(market_date[0].index, 100 * market_date[0]['cum_percent_change'], label = market)
    plt.plot(grouped.index, 100 * grouped.values, label = 'TICKERS')
    plt.text(market_date[0].loc[market_date[0].index== market_date[0].index.max()].index, 100 * market_date[0].loc[market_date[0].index == market_date[0].index.max()]['cum_percent_change'], '({}, {})'.format(market_date[0].loc[market_date[0].index == market_date[0].index.max()].index.date[0], round(100 * market_date[0].loc[market_date[0].index == market_date[0].index.max()]['cum_percent_change'].values[0],2)))
    plt.text(grouped.loc[grouped.index == grouped.index.max()].index, 100 * grouped.loc[grouped.index == grouped.index.max()].values, '({}, {})'.format(grouped.loc[grouped.index == grouped.index.max()].index.date[0], round(100 * grouped.loc[grouped.index == grouped.index.max()].values[0],2)))
    plt.title(market.upper() + " GAIN:" + str(round(market_date[1],2)) + "% | TICKERS GAIN: " + str(round(stocks_net, 2)) + "%")
    plt.xlabel('Date')
    plt.ylabel('Percent Change')
    plt.legend()
    plt.show()





test_strategy(df, 'dow jones')
