# utils.py

import pickle
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
def generate_item_suggestions(items_data, starting_gold, model):
    X, _ = prepare_training_data(items_data)
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
            suggestions.append(item)

    suggestions.sort(key=lambda x: x["Predicted Profit"], reverse=True)
    return suggestions[:5]

def prepare_training_data(items_data):
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
        y.append(item["Potential Profit"])

    X_normalized = StandardScaler().fit_transform(X)
    y_log_transformed = np.log1p(y)
    return X_normalized, y_log_transformed

def train_model(items_data):
    model_file = "model.pkl"
    if os.path.exists(model_file):
        with open(model_file, "rb") as file:
            model = pickle.load(file)
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=42)

    X, y = prepare_training_data(items_data)
    model.fit(X, y)

    with open(model_file, "wb") as file:
        pickle.dump(model, file)

    return model

def format_suggestions(suggestions):
    formatted_suggestions = []
    for suggestion in suggestions:
        formatted_suggestion = f"- {suggestion['Item Name']}\n  Buy Price: {suggestion['Low (Buy)']}\n  Sell Price: {suggestion['High (Sell)']}\n  Potential Profit: {suggestion['Potential Profit']} per item\n  Buy Limit: {suggestion['Buy Limit']}\n  Max Quantity: {suggestion['Max Quantity']}\n"
        formatted_suggestions.append(formatted_suggestion)
    return "\n".join(formatted_suggestions)