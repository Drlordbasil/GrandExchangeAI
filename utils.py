# utils.py

import pickle
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics import mean_absolute_error
def generate_item_suggestions(items_data, starting_gold, model):
    X = prepare_training_data(items_data, return_y=False)
    X_normalized = StandardScaler().fit_transform(X)
    predictions = model.predict(X_normalized)

    suggestions = []
    for i, item in enumerate(items_data):
        prediction = predictions[i]
        if prediction > 0:
            item["Predicted Profit"] = prediction
            buy_limit = item["Buy Limit"]
            buy_price = item["Low (Buy)"]
            max_quantity = min(buy_limit, starting_gold // buy_price)
            item["Max Quantity"] = max_quantity
            item["Total Profit"] = item["Potential Profit (After Tax)"] * max_quantity
            suggestions.append(item)

    suggestions.sort(key=lambda x: x["Total Profit"], reverse=True)
    return suggestions[:5]

def prepare_training_data(items_data, return_y=True):
    X = []
    y = []
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
        y.append(item["Potential Profit (After Tax)"])

    X = np.array(X)
    
    if return_y:
        y = np.array(y)
        # Replace non-positive values with a small positive value
        y[y <= 0] = 1e-8
        y_log_transformed = np.log1p(y)
        return X, y_log_transformed
    else:
        return X



def train_model(items_data, epochs=10):
    if len(items_data) < 2:
        print("Insufficient data for training. Please ensure that items_data contains at least 2 samples.")
        return None

    X, y = prepare_training_data(items_data)

    # Remove samples with NaN or infinite values
    valid_samples = np.isfinite(y)
    X = X[valid_samples]
    y = y[valid_samples]

    if len(X) < 5:
        print("Insufficient data for cross-validation. Performing train-test split.")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    else:
        X_train, y_train = X, y
        X_test, y_test = X, y

    models = [
        RandomForestRegressor(random_state=42),
        GradientBoostingRegressor(random_state=42)
    ]

    best_model = None
    best_params = None
    best_score = np.inf

    for model in models:
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 5, 10],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        if len(X) < 5:
            grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=2, scoring='neg_mean_absolute_error')
        else:
            grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, scoring='neg_mean_absolute_error')
        grid_search.fit(X_train, y_train)
        best_params_current = grid_search.best_params_
        best_score_current = -grid_search.best_score_

        if best_score_current < best_score:
            best_model = model
            best_params = best_params_current
            best_score = best_score_current

    if best_model is not None:
        best_model.set_params(**best_params)
        for _ in range(epochs):
            best_model.fit(X_train, y_train)

        y_pred = best_model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        print(f"Best Model: {type(best_model).__name__}")
        print(f"Best Parameters: {best_params}")
        print(f"Mean Absolute Error: {mae}")

    return best_model

def format_suggestions(suggestions):
    formatted_suggestions = []
    for suggestion in suggestions:
        formatted_suggestion = f"- {suggestion['Item Name']}\n  Buy Price: {suggestion['Low (Buy)']}\n  Sell Price: {suggestion['High (Sell)']}\n  Potential Profit (After Tax): {suggestion['Potential Profit (After Tax)']} per item\n  Buy Limit: {suggestion['Buy Limit']}\n  Max Quantity: {suggestion['Max Quantity']}\n  Total Profit: {suggestion['Total Profit']}\n"
        formatted_suggestions.append(formatted_suggestion)
    return "\n".join(formatted_suggestions)

def load_model(model_file):
    if os.path.exists(model_file):
        with open(model_file, "rb") as file:
            model = pickle.load(file)
        return model
    else:
        return None

def save_model(model, model_file):
    with open(model_file, "wb") as file:
        pickle.dump(model, file)