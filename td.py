import os
from dotenv import load_dotenv

import tda
from tda import auth, client
from tda.auth import easy_client
from tda.client import Client

import datetime
import json
import pandas as pd

import day_cache as cache

# pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

def __dump(j):
    print(json.dumps(j,indent=2))

def get_client():
    load_dotenv()
    token_path = os.getenv("token_path")
    api_key = os.getenv("api_key")
    redirect_url = os.getenv("redirect_url")

    try:
        c = auth.client_from_token_file(token_path, api_key)
    except FileNotFoundError:
        from selenium import webdriver
        with webdriver.Chrome() as driver:
            c = auth.client_from_login_flow(
                driver, api_key, redirect_url, token_path)
    return c

def data():
    # gets client
    client = get_client()

    # The index symbol to get movers from class
    # can be $COMPX, $DJI, or $SPX.X. Click to edit the value.
    # gets top 10 up movers
    options = pd.DataFrame(client.get_movers('$SPX.X', client.Movers.Direction.UP, client.Movers.Change.PERCENT).json())

    # gets the tickers of the top 10 movers
    tickers = list(options['symbol'])

    # gets the quotes of the top 10 movers
    quotes = client.get_quotes(tickers).json()

    # datetime_array that has as many dates as there are columns
    datetime_array = [datetime.datetime.now()] * len(quotes[tickers[0]].keys())

    # pushes data in dataframe and adds time as multi index
    data = pd.DataFrame(quotes)
    data = data.set_index([data.index, datetime_array])

    time = str(data.index[0][1].strftime("%H:%M:%S"))
    data.to_pickle("./second_data/" + time + ".pkl")

    # returns data


print(data())
# print(data())

# def optionChain(ticker, price):
#     today = datetime.date.today()
#     endInterval = today + datetime.timedelta(days = 7)
#     client = get_client()
#     optionsJson = cache.get(ticker,'td_options')
#     if optionsJson is None:
#         options = client.get_option_chain(ticker.upper(),
#             contract_type = client.Options.ContractType.CALL,
#             include_quotes = True,
#             strike_count = 100,
#             from_date = today, to_date = endInterval)
#         optionsJson = options.json()
#         # __dump(optionsJson)
#         cache.set(ticker,'td_options',optionsJson)
#     optionsMap = optionsJson['callExpDateMap']
#     # __dump(optionsMap)
#     optionsInfo = pd.DataFrame(columns = ['Strike', 'Price','Contract Name', 'Volume'])
#     for date in optionsMap:
#         for strike in optionsMap[date]:
#             chain = optionsMap[date][strike][0]
#             if((float)(strike) > (float)(price)):
#                 optionsInfo = optionsInfo.append( { "Strike": (float)(strike),
#                                 "Price": (chain['last']),
#                                 "Contract Name": chain['symbol'],
#                                 'Volume' : chain['totalVolume']}, ignore_index=True )
#     return optionsInfo
#
# def optionChainForPredict(ticker):
#     today = datetime.date.today()
#     endInterval = today + datetime.timedelta(days = 365)
#     client = get_client()
#     # optionsJson = cache.get(ticker,'td_options')
#     optionsJson = None
#     if optionsJson is None:
#         options = client.get_option_chain(ticker.upper(),
#             include_quotes = True,
#             from_date = today, to_date = endInterval)
#         optionsJson = options.json()
#         # __dump(optionsJson)
#         cache.set(ticker,'td_options',optionsJson)
#     optionsMapCall = optionsJson['callExpDateMap']
#     optionsMapPut = optionsJson['putExpDateMap']
#     # __dump(optionsMap)
#     optionsInfoCall = pd.DataFrame(columns = ['Strike', 'Price','Contract Name', 'Volume', 'Type', 'Expiration Date'])
#     optionsInfoPut = pd.DataFrame(columns = ['Strike', 'Price','Contract Name', 'Volume', 'Type', 'Expiration Date'])
#
#     for date in optionsMapCall:
#         for strike in optionsMapCall[date]:
#             chain = optionsMapCall[date][strike][0]
#             optionsInfoCall = optionsInfoCall.append( { "Strike": (float)(strike),
#                             "Price": (chain['last']),
#                             "Contract Name": chain['symbol'],
#                             'Volume' : chain['totalVolume'],
#                             'Type' : chain['putCall'],
#                             'Expiration Date' : (int)(chain['expirationDate'])}, ignore_index=True )
#
#     for date in optionsMapPut:
#         for strike in optionsMapPut[date]:
#             chain = optionsMapPut[date][strike][0]
#             optionsInfoPut = optionsInfoPut.append( { "Strike": (float)(strike),
#                             "Price": (chain['last']),
#                             "Contract Name": chain['symbol'],
#                             'Volume' : chain['totalVolume'],
#                             'Type' : chain['putCall'],
#                             'Expiration Date' : (int)(chain['expirationDate'])}, ignore_index=True )
#     optionsInfoCall = optionsInfoCall[optionsInfoCall['Volume'] != 0]
#     optionsInfoPut = optionsInfoPut[optionsInfoPut['Volume'] != 0]
#     return optionsInfoCall, optionsInfoPut






# For testing
# if __name__ == "__main__":
#     pd.set_option("display.max_columns", None)
#     pd.set_option('display.max_rows', None)
#     pd.set_option('display.width', None)
#     pd.set_option('display.max_colwidth', None)

    # print(optionChainForPredict('aapl'))
