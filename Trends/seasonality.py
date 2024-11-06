import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd

def find_the_seasonality_on_column(df: pd.DataFrame, column: str, ticker: str, test_period=7 , figure_directory = 'Plots'):
    # Ensure data is sorted by date in ascending order
    df = df.sort_index()
    
    # Detrending and identifying seasonality using decomposition
    decomposition = seasonal_decompose(df[column], model='additive', period=test_period)

    # Plot the decomposition
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 10))

    # Plot observed data (Original Time Series)
    decomposition.observed.plot(ax=ax1, legend=False)
    ax1.set_ylabel('Observed')
    ax1.set_title(f'{ticker} - Observed ({column})')

    # Plot the trend component
    decomposition.trend.plot(ax=ax2, legend=False)
    ax2.set_ylabel('Trend')
    ax2.set_title(f'{ticker} - Trend')

    # Plot the seasonal component
    decomposition.seasonal.plot(ax=ax3, legend=False)
    ax3.set_ylabel('Seasonal')
    ax3.set_title(f'{ticker} - Seasonality (Period = {test_period} Days)')

    # Plot the residual component
    decomposition.resid.plot(ax=ax4, legend=False)
    ax4.set_ylabel('Residual')
    ax4.set_title(f'{ticker} - Residual')

    # Overall title and saving the plot
    plt.suptitle(f'Seasonal Decomposition of {ticker} ({column}) Time Series', fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to make space for the main title
    plt.savefig(f'{figure_directory}/{ticker}_seasonal_decomposition_{column}.png')
    plt.close()
    return decomposition

# Example usage:
# df is your DataFrame with DateTimeIndex and relevant columns, e.g., 'Close' or 'Volume'
# find_the_seasonality_on_column(df, 'Close', 'BTC', test_period=30) for monthly seasonality
