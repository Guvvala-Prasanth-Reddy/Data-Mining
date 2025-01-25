# Cryptocurrency Market Analysis Using Data Mining Techniques

## **Overview**
This project focuses on analyzing the cryptocurrency market to uncover trends, predict price movements, and group cryptocurrencies based on their behaviors. By leveraging data mining techniques and machine learning models, this framework combines historical price data with sentiment analysis to provide actionable insights for investors and researchers.

## **Features**
1. **Cryptocurrency Price Prediction:**
   - Implemented an LSTM model to forecast cryptocurrency prices using historical data and sentiment analysis.
   - Engineered advanced features like rolling sentiment averages, lagged price values, and log-transformed trading volumes.
   - Visualized model performance through true vs. predicted price plots and training loss graphs.

2. **Cryptocurrency Clustering:**
   - Conducted similarity analysis using Agglomerative Hierarchical Clustering to group cryptocurrencies based on price correlations.
   - Generated dendrograms and heatmaps to visualize clusters of cryptocurrencies with similar movements.

3. **Sentiment Analysis:**
   - Extracted cryptocurrency-related news articles using the Cryptonews API.
   - Performed sentiment scoring on news articles using FinBERT, incorporating rolling sentiment averages into predictive models.

4. **Data Preprocessing:**
   - Processed and normalized over 1.9 million data points from Yahoo Finance for 231 cryptocurrencies.
   - Addressed seasonal decomposition, anomaly detection, and data gaps to ensure clean and reliable datasets.

## **Tech Stack**
- **Programming Languages:** Python
- **Libraries:** Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn, PyTorch, Beautiful Soup
- **APIs:** Yahoo Finance API, Cryptonews API
- **Database:** PostgreSQL for sentiment data storage
- **Machine Learning Models:** LSTM (for time series forecasting), Agglomerative Hierarchical Clustering (for similarity analysis)
- **Tools:** FinBERT for sentiment analysis, Beautiful Soup for web scraping

## **Data Sources**
1. **Yahoo Finance API:** Historical price data for 231 cryptocurrencies.
2. **Cryptonews API:** News articles related to cryptocurrencies for sentiment analysis.

## **Key Results**
- **Price Prediction:** Achieved accurate predictions for volatile cryptocurrencies like Bitcoin and Ethereum using LSTM models.
- **Clustering:** Identified meaningful clusters of cryptocurrencies based on price correlations, aiding in market understanding and portfolio optimization.
- **Insights:** Highlighted the impact of public sentiment and external events on cryptocurrency price trends.

## **Future Work**
- Integrate additional social media platforms (e.g., Twitter, Reddit) for sentiment analysis.
- Explore other clustering algorithms (e.g., DBSCAN, Gaussian Mixture Models).
- Optimize LSTM architecture and feature engineering for production-grade implementations.
- Address API rate limitations to fetch larger datasets for more robust predictions.

## **Contributors**
- **Prasanth Reddy Guvvala:** Data fetching, sentiment analysis pipeline, and LSTM model development
- **Rahul Payeli:** Data preprocessing, clustering analysis, and visualization of results
