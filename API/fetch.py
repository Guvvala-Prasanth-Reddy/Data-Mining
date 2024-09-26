import yfinance as yf
import numpy as np
import datetime
# Example: Fetching data for Bitcoin and Ethereum
tickers = np.load('crypto_tickers.npy')
tickers = list(map( str , list(tickers)))
print(tickers , type(tickers))
for i in tickers :
    crypto_data = yf.download(i, period='6mo', interval='1h')
    print(crypto_data.shape)
    crypto_data  =  crypto_data.reset_index()
    crypto_data['ticker'] = i
    crypto_data.to_csv(f'data/{i}-6m-{str(datetime.date.today())}.csv')
    #Todo : persist and create  a dataset form the above fetched data 
