import pandas as pd
from sklearn.preprocessing import StandardScaler

def normalize_data_frame(data : pd.DataFrame):
    # Assuming 'data' is your DataFrame containing financial data for 250 cryptocurrencies
    # and has columns: ['Datetime', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'ticker']
    df = data.copy()
    # Initialize the StandardScaler
    scaler = StandardScaler()

    # List of columns to normalize
    columns_to_normalize = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

    # Normalize data for each crypto individually
    for ticker in data['ticker'].unique():
        # Subset of data for the current cryptocurrency
        crypto_data = data.loc[data['ticker'] == ticker, columns_to_normalize]

        # Apply Z-score normalization (standardization)
        normalized_data = scaler.fit_transform(crypto_data)

        # Replace the original columns with normalized values
        data.loc[data['ticker'] == ticker, columns_to_normalize] = normalized_data
        # print(data == df)

        return data

    # The 'data' DataFrame now contains normalized values for each cryptocurrency
