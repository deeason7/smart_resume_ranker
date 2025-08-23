# train_model.py
"""
This script is a standalone, advanced machine learning pipeline for retraining
the candidate ranking model.

It uses a scikit-learn Pipeline to preprocess features and GridSearchCV to
automatically find the best model hyperparameters on a training set. It then
evaluates the final model's performance on a separate, unseen test set.
"""
import os
import joblib
import pandas as pd
from datetime import datetime
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from app import create_app
from app.models import Application

print("Starting Advanced Model Retraining Pipeline ")

app = create_app()

with app.app_context():
    print("Fetching labeled data from the database...")
    # Fetch Labeled Data
    labeled_apps = Application.query.filter(
        Application.status.in_(['Accepted', 'Declined']),
        Application.feature_scores.isnot(None)
    ).all()

    if len(labeled_apps) < 20:
        print(f"PROCESS CANCELED: Not enough labeled data. Found {len(labeled_apps)}, but need at least 20.")
        exit()

    #  Prepare Full Dataset
    features = [app.feature_scores for app in labeled_apps]
    labels = [1 if app.status == 'Accepted' else 0 for app in labeled_apps]

    df = pd.DataFrame(features)
    target = pd.Series(labels)
    numeric_features = [col for col in df.columns if 'similarity' in col]

    X_train, X_test, y_train, y_test = train_test_split(
        df, target, test_size=0.2, random_state=42, stratify=target
    )
    print(f"Data split: {len(X_train)} training samples, {len(X_test)} holdout test samples.")

    #  Create Preprocessing and Modeling Pipeline
    preprocessor = ColumnTransformer(
        transformers=[('num', StandardScaler(), numeric_features)],
        remainder='passthrough'
    )
    xgboost_model = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False,
                                      random_state=42)
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', xgboost_model)
    ])

    #  Define Hyperparameter Grid for GridSearchCV
    param_grid = {
        'classifier__n_estimators': [100, 200],
        'classifier__max_depth': [3, 5],
        'classifier__learning_rate': [0.05, 0.1],
    }

    # Setup the Grid Search to run on the TRAINING DATA ONLY
    print("Starting Hyperparameter Tuning on training data...")
    grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='roc_auc', n_jobs=-1, verbose=1)
    grid_search.fit(X_train, y_train)

    print(f"Best parameters found: {grid_search.best_params_}")
    print(f"Best cross-validation AUC score on training data: {grid_search.best_score_:.4f}")

    #  Evaluate the best model on the UNSEEN test set
    best_model = grid_search.best_estimator_
    test_predictions = best_model.predict_proba(X_test)[:, 1]
    final_test_auc = roc_auc_score(y_test, test_predictions)
    print(f"FINAL MODEL PERFORMANCE on Holdout Test Set")
    print(f"Test Set AUC Score: {final_test_auc:.4f}")

    model_dir = os.path.join(app.instance_path, 'ml_models')
    os.makedirs(model_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_filename = f"ranking_model_{timestamp}_auc_{final_test_auc:.2f}.pkl"
    model_path = os.path.join(model_dir, model_filename)
    joblib.dump(best_model, model_path)

    print(f"SUCCESS: Successfully saved new, optimized model to {model_path}")
