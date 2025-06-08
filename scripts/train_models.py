import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import joblib
import numpy as np

# Load training data
df = pd.read_csv("data/training/training_data.csv")

# Targets
yh = df["home_corners"]
ya = df["away_corners"]

# Classify match result: home/draw/away
def label_result(row):
    if row["home_corners"] > row["away_corners"]:
        return "home"
    elif row["home_corners"] < row["away_corners"]:
        return "away"
    else:
        return "draw"

ym = df.apply(label_result, axis=1)

# Drop non-feature columns
X = df.drop(columns=["fixture_id", "home_corners", "away_corners", "home_team", "away_team"], errors='ignore')

# Clean and transform
X = X.replace('%', '', regex=True).apply(pd.to_numeric, errors='coerce')
X = X.dropna(axis=1, thresh=int(0.8 * len(X)))   # Keep columns with ≥80% data
X = X.loc[:, X.nunique() > 1]                    # Remove constant columns
X = X.fillna(0)                                  # Fill remaining NaNs
X.columns = X.columns.str.replace(" ", "_")      # Make feature names safe

# ✅ Save training column names
joblib.dump(X.columns.tolist(), "models/training_columns.pkl")

# Debug
print("Features in X:", X.columns.tolist())
print("Sample values:\n", X.head())
print("Training rows:", len(X))

# Split
data = train_test_split(X, yh, ya, ym, test_size=0.2, random_state=42)
X_train, X_test, yh_train, yh_test, ya_train, ya_test, ym_train, ym_test = data

# Train regressors
model_home = lgb.LGBMRegressor()
model_home.fit(X_train, yh_train)

model_away = lgb.LGBMRegressor()
model_away.fit(X_train, ya_train)

# Train classifier
model_match = lgb.LGBMClassifier()
model_match.fit(X_train, ym_train)

# Evaluate
rmse_home = np.sqrt(mean_squared_error(yh_test, model_home.predict(X_test)))
rmse_away = np.sqrt(mean_squared_error(ya_test, model_away.predict(X_test)))
acc_match = accuracy_score(ym_test, model_match.predict(X_test))

print("\n✅ Model Performance")
print("🏠 Home corner RMSE:", rmse_home)
print("🚌 Away corner RMSE:", rmse_away)
print("🎯 Match result accuracy:", acc_match)

# Save models
joblib.dump(model_home, "models/model_home_corners.pkl")
joblib.dump(model_away, "models/model_away_corners.pkl")
joblib.dump(model_match, "models/model_match_result.pkl")
