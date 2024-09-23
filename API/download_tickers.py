from yahooquery import Screener
import numpy as np
s = Screener()
data = s.get_screeners('all_cryptocurrencies_us', count=250)

# data is in the quotes key
dicts = data['all_cryptocurrencies_us']['quotes']
symbols = [d['symbol'] for d in dicts]
np.save('crypto_tickers.npy' , np.array(symbols , dtype='str' ).flatten())