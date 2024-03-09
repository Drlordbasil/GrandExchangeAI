import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.decomposition import PCA

class FeatureEngineer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.selector = SelectKBest(f_regression, k=5)
        self.pca = PCA(n_components=3)

    def preprocess_data(self, items_data):
        X = []
        for item in items_data:
            X.append([
                item["High (Sell)"],
                item["Low (Buy)"],
                item["High Volume"],
                item["Low Volume"],
                item["5-Minute Average High Price"],
                item["Price Fluctuation"],
                item["Buy Limit"],
                item["ROI"]
            ])

        X = np.array(X)
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled

    def engineer_features(self, items_data):
        engineered_features = []
        for item in items_data:
            price_ratio = item["High (Sell)"] / item["Low (Buy)"]
            volume_ratio = item["High Volume"] / (item["Low Volume"] + 1e-8)  # Add a small value to avoid division by zero
            price_volatility = item["Price Fluctuation"] / (item["5-Minute Average High Price"] + 1e-8)  # Add a small value to avoid division by zero
            roi_normalized = item["ROI"] / (item["Buy Limit"] + 1e-8)  # Add a small value to avoid division by zero
            volume_price_ratio = (item["High Volume"] + item["Low Volume"]) / (item["High (Sell)"] + item["Low (Buy)"] + 1e-8)  # Add a small value to avoid division by zero
            engineered_features.append([price_ratio, volume_ratio, price_volatility, roi_normalized, volume_price_ratio])

        return np.array(engineered_features)

    def select_features(self, X, y):
        self.selector.fit(X, y)
        selected_features = self.selector.transform(X)
        return selected_features

    def apply_pca(self, X):
        pca_features = self.pca.fit_transform(X)
        return pca_features

    def combine_features(self, items_data):
        preprocessed_data = self.preprocess_data(items_data)
        engineered_features = self.engineer_features(items_data)
        combined_features = np.concatenate((preprocessed_data, engineered_features), axis=1)

        y = np.array([item["Potential Profit (After Tax)"] for item in items_data])
        selected_features = self.select_features(combined_features, y)
        pca_features = self.apply_pca(selected_features)

        return pca_features