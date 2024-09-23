import yfinance as yf
import numpy as np
# Example: Fetching data for Bitcoin and Ethereum
tickers = np.load('crypto_tickers.npy')
tickers = list(tickers)
print(tickers , type(tickers))
for i in tickers :
    crypto_data = yf.download(i, period='1d', interval='1h')    
    #Todo : persist and create  a dataset form the above fetched data 
