import pandas as pd
import glob
from Preprocessing import normalize
from Trends import seasonality
def read_data_and_return_dataframe( path : str):
    # Get a list of all CSV files in the folder
    csv_files = glob.glob(f'{path}/*.csv')

    # Create an empty list to store the dataframes
    dfs = []

    # Loop over the CSV files and read them into dataframes
    for file in csv_files:
        df = pd.read_csv(file)
        if(  not df.empty):
            dfs.append(df)


    # Concatenate all the dataframes into a single dataframe
    
    combined_df = pd.concat(dfs, ignore_index = True)
    combined_df.drop(combined_df.columns[combined_df.columns.str.contains(
    'unnamed', case=False)], axis=1, inplace=True)
    return combined_df

if __name__ == '__main__':
    dataframe = read_data_and_return_dataframe(path='data')
    normalized_df = normalize.normalize_data_frame(data=dataframe)
    normalized_df.set_index('Datetime' , inplace=True)
    for ticker in normalized_df['ticker'].unique() :
        seasonal_df = normalized_df[normalized_df['ticker'] == ticker]
        seasonal_df = seasonal_df[[ 'Close' , 'Volume'  ]]
        seasonality.find_the_seasonality_on_column(df =  seasonal_df , column = 'Close' , ticker=ticker )