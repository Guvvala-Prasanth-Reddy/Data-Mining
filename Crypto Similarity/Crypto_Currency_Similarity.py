import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform
import seaborn as sns
from scipy.cluster.hierarchy import fcluster
import pandas as pd

directory = r"/Users/rahulpayeli/Documents/DataMining/Project/data"

combined_dfs = []

# Iterate over files in directory
for file in os.listdir(directory):
    df = pd.read_csv(f'/Users/rahulpayeli/Documents/DataMining/Project/data/{file}')
    if not df.empty:
        df = df.iloc[:,1:]
        
        #create a new column called 'Daily Return', that holds percentage change in the 'Adj Close'.
        df['Daily Return'] = df['Adj Close'].pct_change().fillna(0)
        combined_dfs.append(df)

combined_data = pd.concat(combined_dfs, ignore_index=True)

pivot_data = combined_data.pivot(index='Datetime', columns='ticker', values='Daily Return')

pivot_data.sort_index

# Fill forward, then backward for any remaining NaNs
pivot_data_filled = pivot_data.ffill().bfill()

# Compute the correlation matrix
correlation_matrix = pivot_data_filled.corr()

# distance matrix is calculated using the correlation matrix. As correlation value corresponds to 
# how close it is to the other ticker. Therefore, 1-corr gives the dissimilarity/distance.
dist_matrix = 1 - np.abs(correlation_matrix)

linkage_matrix = linkage(squareform(dist_matrix), method='complete')

labels = fcluster(linkage_matrix, 0.6999, criterion='distance')

# Reorder the correlation matrix based on cluster labels
clustered_tickers = pd.DataFrame({'Ticker': correlation_matrix.columns, 'Cluster': labels})
clustered_tickers = clustered_tickers.sort_values('Cluster')

cluster_table = clustered_tickers.groupby("Cluster")["Ticker"].apply(list).reset_index()
cluster_table.columns = ["Cluster", "Tickers"]
cluster_table.to_csv("clustered_tickers.csv", index=False)

# Plot the dendrogram
plt.figure(figsize=(28, 24))
dendrogram(linkage_matrix, labels=correlation_matrix.columns)
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('Features')
plt.ylabel('Distance')
plt.axhline(y=0.6999, color='r', linestyle='--')
plt.show()

print('Number of clusters: ', len(np.unique(labels)))