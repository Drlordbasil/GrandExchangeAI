import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error

def generate_item_suggestions(items_data, starting_gold, model):
    try:
        print("Generating item suggestions...")
        X = []
        for item in items_data:
            X.append([
                item["high_price"],
                item["low_price"],
                item["high_volume"],
                item["low_volume"],
                item["avg_price_5m"],
                item["price_fluctuation"],
                item["buy_limit"],
                item["roi"]
            ])

        X = np.array(X)
        print(f"Shape of feature matrix X: {X.shape}")

        scaler = StandardScaler()
        X_normalized = scaler.fit_transform(X)
        print(f"Shape of normalized feature matrix X_normalized: {X_normalized.shape}")

        if model is None:
            print("No model available. Generating default suggestions based on potential profit.")
            suggestions = []
            for item in items_data:
                if item["potential_profit"] > 0:
                    buy_limit = item["buy_limit"]
                    buy_price = item["low_price"]
                    max_quantity = min(buy_limit, starting_gold // buy_price, 1000)  # Limit max quantity to 1000
                    item["Max Quantity"] = max_quantity
                    item["Total Profit"] = item["potential_profit"] * max_quantity
                    if item["Total Profit"] > 1000000:  # Filter out suggestions with total profit over 1 million
                        suggestions.append(item)
        else:
            try:
                predictions = model.predict(X_normalized)
                suggestions = []
                for i, item in enumerate(items_data):
                    prediction = predictions[i]
                    if prediction > 0:
                        item["Predicted Profit"] = prediction
                        buy_limit = item["buy_limit"]
                        buy_price = item["low_price"]
                        max_quantity = min(buy_limit, starting_gold // buy_price, 1000)  # Limit max quantity to 1000
                        item["Max Quantity"] = max_quantity
                        item["Total Profit"] = item["potential_profit"] * max_quantity
                        if item["Total Profit"] > 100:  
                            suggestions.append(item)
            except Exception as e:
                print(f"Error occurred during model prediction: {e}")
                suggestions = []

        suggestions.sort(key=lambda x: x["Total Profit"], reverse=True)
        return suggestions[:5]
    except Exception as e:
        print(f"Error occurred in generate_item_suggestions: {e}")
        return []

def prepare_training_data(items_data):
    try:
        print("Preparing training data...")
        X = []
        y = []
        for item in items_data:
            X.append([
                item["high_price"],
                item["low_price"],
                item["high_volume"],
                item["low_volume"],
                item["avg_price_5m"],
                item["price_fluctuation"],
                item["buy_limit"],
                item["roi"]
            ])
            y.append(item["potential_profit"])

        X = np.array(X)
        y = np.array(y)

        # Handle NaN or infinite values in y
        valid_indices = np.isfinite(y)
        X = X[valid_indices]
        y = y[valid_indices]

        # Apply logarithmic transformation to y
        y[y <= 0] = 1e-8  # Replace non-positive values with a small positive value
        y_log_transformed = np.log1p(y)

        return X, y_log_transformed
    except Exception as e:
        print(f"Error occurred in prepare_training_data: {e}")
        return None, None

def train_model(items_data, epochs=2):
    try:
        print("Training model...")
        X, y = prepare_training_data(items_data)
        if X is None or y is None:
            print("Error occurred during data preparation. Aborting model training.")
            return None

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        models = [
            RandomForestRegressor(random_state=42),
            GradientBoostingRegressor(random_state=42)
        ]

        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 5, 10],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }

        best_model = None
        best_params = None
        best_score = np.inf

        for model in models:
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
    except Exception as e:
        print(f"Error occurred in train_model: {e}")
        return None

def format_suggestions(suggestions):
    try:
        print("Formatting suggestions...")
        formatted_suggestions = []
        for suggestion in suggestions:
            formatted_suggestion = f"- {suggestion['Item Name']}\n  Buy Price: {suggestion['low_price']}\n  Sell Price: {suggestion['high_price']}\n  Potential Profit (After Tax): {suggestion['potential_profit']} per item\n  Buy Limit: {suggestion['buy_limit']}\n  Max Quantity: {suggestion['Max Quantity']}\n  Total Profit: {suggestion['Total Profit']}\n"
            formatted_suggestions.append(formatted_suggestion)
        return "\n".join(formatted_suggestions)
    except Exception as e:
        print(f"Error occurred in format_suggestions: {e}")
        return ""

def load_model(model_file):
    try:
        print(f"Loading model from file: {model_file}")
        with open(model_file, "rb") as file:
            model = pickle.load(file)
        return model
    except FileNotFoundError:
        print(f"Model file not found: {model_file}")
        return None
    except Exception as e:
        print(f"Error occurred while loading model: {e}")
        return None

def save_model(model, model_file):
    try:
        print(f"Saving model to file: {model_file}")
        with open(model_file, "wb") as file:
            pickle.dump(model, file)
    except Exception as e:
        print(f"Error occurred while saving model: {e}")