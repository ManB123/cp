import pandas as pd
import lightgbm as lgb
import xgboost as xgb
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, accuracy_score, f1_score, log_loss, mean_absolute_error
from sklearn.calibration import CalibratedClassifierCV
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

# ----------------------------
# Tune and train model_home
# ----------------------------
param_grid_home = {
    "num_leaves": [31, 50],
    "max_depth": [-1, 10],
    "learning_rate": [0.1, 0.05],
    "n_estimators": [100, 200]
}

grid_search_home = GridSearchCV(
    estimator=lgb.LGBMRegressor(),
    param_grid=param_grid_home,
    cv=3,
    scoring="neg_mean_squared_error",
    n_jobs=-1,
    verbose=1
)
grid_search_home.fit(X_train, yh_train)
model_home = grid_search_home.best_estimator_
print("✅ Best params for Home Corners:", grid_search_home.best_params_)

# ----------------------------
# Tune and train model_away
# ----------------------------
param_grid_away = {
    "num_leaves": [31, 50],
    "max_depth": [-1, 10],
    "learning_rate": [0.1, 0.05],
    "n_estimators": [100, 200]
}

grid_search_away = GridSearchCV(
    estimator=lgb.LGBMRegressor(),
    param_grid=param_grid_away,
    cv=3,
    scoring="neg_mean_squared_error",
    n_jobs=-1,
    verbose=1
)
grid_search_away.fit(X_train, ya_train)
model_away = grid_search_away.best_estimator_
print("✅ Best params for Away Corners:", grid_search_away.best_params_)

# ----------------------------
# Tune ensemble classifier for match result
# ----------------------------
param_grid_ensemble = {
    'lgb__n_estimators': [100, 200],
    'lgb__learning_rate': [0.05, 0.1],
    'xgb__n_estimators': [100, 200],
    'xgb__learning_rate': [0.05, 0.1]
}

lgb_clf = lgb.LGBMClassifier()
xgb_clf = xgb.XGBClassifier(eval_metric='mlogloss', use_label_encoder=False)

ensemble = VotingClassifier(
    estimators=[('lgb', lgb_clf), ('xgb', xgb_clf)],
    voting='soft'
)

grid_search_ensemble = GridSearchCV(
    estimator=ensemble,
    param_grid=param_grid_ensemble,
    cv=3,
    scoring='neg_log_loss',
    n_jobs=-1,
    verbose=1
)
grid_search_ensemble.fit(X_train, ym_train)

calibrated_clf = CalibratedClassifierCV(grid_search_ensemble.best_estimator_, cv=3)
calibrated_clf.fit(X_train, ym_train)
model_match = calibrated_clf
print("✅ Best params for Match Result Classifier:", grid_search_ensemble.best_params_)

# ----------------------------
# Evaluation
# ----------------------------
rmse_home = np.sqrt(mean_squared_error(yh_test, model_home.predict(X_test)))
mae_home = mean_absolute_error(yh_test, model_home.predict(X_test))

rmse_away = np.sqrt(mean_squared_error(ya_test, model_away.predict(X_test)))
mae_away = mean_absolute_error(ya_test, model_away.predict(X_test))

preds_match = model_match.predict(X_test)
preds_proba = model_match.predict_proba(X_test)

acc_match = accuracy_score(ym_test, preds_match)
f1_match = f1_score(ym_test, preds_match, average='weighted')
logloss_match = log_loss(ym_test, preds_proba)

print("\n✅ Model Performance")
print("🏠 Home corner RMSE:", rmse_home)
print("🏠 Home corner MAE:", mae_home)
print("🚌 Away corner RMSE:", rmse_away)
print("🚌 Away corner MAE:", mae_away)
print("🎯 Match result accuracy:", acc_match)
print("🎯 Match result F1 score:", f1_match)
print("🎯 Match result log loss:", logloss_match)

# Save models
joblib.dump(model_home, "models/model_home_corners.pkl")
joblib.dump(model_away, "models/model_away_corners.pkl")
joblib.dump(model_match, "models/model_match_result.pkl")
