import os
import pickle
from datetime import date
from dotenv import load_dotenv


if not os.path.isdir(".symbol_cache"):
    os.mkdir(".symbol_cache")

def _get_path(ticker):
    path = './.symbol_cache/'+ ticker.upper() +'/'
    if not os.path.isdir(path):
        os.mkdir(path)
    return path

def _get_file(ticker, key):
    ticker = ticker.upper()
    path = _get_path(ticker)
    month = str(date.today().month)
    file = path + key + '.' + ticker + '.' + month + '.pickle'
    return file

def delete(ticker, key):
    try: os.remove(_get_fule(ticker, key))
    except:  pass

def get(ticker, key):
    load_dotenv()
    dont_cache = os.getenv("dont_cache", "")
    if key in dont_cache:
        return None

    value = None
    try:
        with open( _get_file(ticker, key), 'rb') as f:
            value = pickle.load(f)
    except Exception as e:
        pass
    if value is False:
        raise Exception("Data stored as false")
    return value

def set(ticker,key,value):
    load_dotenv()
    dont_cache = os.getenv("dont_cache", "")
    if key in dont_cache:
        return

    try:
        # data = { 'updated': date.today(), 'value': value }
        with open( _get_file(ticker,key), 'wb') as f:
            pickle.dump(value,f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print("oops", e)
        pass


if __name__ == "__main__":
    print('y')
