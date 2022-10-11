from datetime import datetime, date, timedelta
from yahoo_fin import stock_info as si
import day_cache as cache

markets = {'s&p': '^GSPC', 'dow jones': '^DJI', 'nasdaq': '^IXIC'}

# gets market comparison
def compare_market(market, s_date, e_date):
    ticker = markets[market]
    market_date = cache.get(market, 'market')
    if market_date is None:
        market_date = si.get_data(ticker)
        cache.set(market, 'market', market_date)

    if not s_date:
        s_date = str(market_date.index[0].date())

    market_date = market_date.loc[datetime.strptime(s_date, '%Y-%m-%d') : datetime.strptime(e_date, '%Y-%m-%d')]
    market_date['cum_percent_change'] = (market_date['close'] - market_date['open'].iloc[0]) / market_date['open'].iloc[0]
    market_date = market_date.fillna(0)

    sp_net = (100 * (market_date['close'].iloc[-1] - market_date['open'].iloc[0]) / market_date['open'].iloc[0])

    return market_date, sp_net
