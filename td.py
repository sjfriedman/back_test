import os
from dotenv import load_dotenv

import tda
from tda import auth, client
from tda.auth import easy_client
from tda.client import Client

import datetime
import json
import pandas as pd

# pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# pretty prints json
def __dump(j):
    print(json.dumps(j,indent=2))

# accesses td account
def get_client():
    # gets info from env file
    load_dotenv()

    # puts in paths to access TD
    token_path = os.getenv("token_path")
    api_key = os.getenv("api_key")
    redirect_url = os.getenv("redirect_url")

    # tries to access TD
    try:
        c = auth.client_from_token_file(token_path, api_key)
    except FileNotFoundError:
        from selenium import webdriver
        with webdriver.Chrome() as driver:
            c = auth.client_from_login_flow(
                driver, api_key, redirect_url, token_path)

    # returns client infromation
    return c

# gets stock quotes
def data(client, options, time, x = 0):

    file = "./second_data/" + str(time) + ".pkl"
    if not os.path.exists(file):
        # gets the tickers of the top 10 movers
        tickers = list(options['symbol'])

        # gets the quotes of the top 10 movers
        quotes = client.get_quotes(tickers).json()

        # datetime_array that has as many dates as there are columns
        datetime_array = [datetime.datetime.now()] * len(quotes[tickers[0]].keys())

        # pushes data in dataframe and adds time as multi index
        data = pd.DataFrame(quotes)


        data.to_pickle(file)

# For testing
if __name__ == "__main__":
    # gets client
    client = get_client()

    # get top 10 movers
    options = pd.DataFrame(client.get_movers('$SPX.X', client.Movers.Direction.UP, client.Movers.Change.PERCENT).json())

    # runs code from 9:30 to 4:00
    while True:
        time = datetime.datetime.now().time().replace(microsecond=0)
        if time >= datetime.datetime.strptime('09:30:00', "%H:%M:%S").time() and time < datetime.datetime.strptime('16:00:00', "%H:%M:%S").time():
            data(client, options, time)
        if time >= datetime.datetime.strptime('16:00:00', "%H:%M:%S").time():
            break
