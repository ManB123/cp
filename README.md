# Corner Predictor (CP)

This project predicts football match results and corner counts using data from the API-Football service.

## Setup

1. **Python environment** – Create a virtual environment with Python 3.11+ and install dependencies:
   ```bash
   pip install pandas numpy scikit-learn lightgbm joblib requests pyyaml streamlit
   ```

2. **API credentials** – Add your API key to `config.yaml`:
   ```yaml
   api_football:
     key: "YOUR_API_KEY"
     host: "v3.football.api-sports.io"
   ```

## Training pipeline

Run the following scripts from the project root to build models:

1. **Extract training data** – downloads historical fixtures and computes features:
   ```bash
   python scripts/extract_and_save_training_data.py
   ```
   This creates CSV files under `data/training/`.

2. **Train models** – trains LightGBM models and saves them to the `models/` directory:
   ```bash
   python scripts/train_models.py
   ```

After these steps, `models/model_match_result.pkl`, `model_home_corners.pkl`,
`model_away_corners.pkl`, and `training_columns.pkl` will exist.

## Making predictions

With the trained models available, you can predict upcoming fixtures:

```bash
python scripts/predict_upcoming.py
```

The `predict_upcoming_for_league` function will load the models and generate
predictions for upcoming matches. If the models are missing, the script falls
back to dummy predictions (which is the warning you may have seen).

You can also launch the Streamlit frontend for an interactive interface:

```bash
streamlit run frontend/app.py
```

Make sure to run the training pipeline at least once before attempting
predictions so that the models are present.
