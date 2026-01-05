#!/usr/bin/env python3
# Automated ML Pipeline with DVC integration
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
import mlflow
import argparse
import logging

def train_model():
    # Load data
    df = pd.read_csv("data/raw/heart_disease_full.csv")
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Full pipeline (same as Task 2)
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.impute import SimpleImputer
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    
    numeric_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'ca']
    categorical_features = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']
    
    preprocessor = ColumnTransformer([
        ('num', Pipeline([('imputer', SimpleImputer(strategy='median')),
                         ('scaler', StandardScaler())]), numeric_features),
        ('cat', Pipeline([('imputer', SimpleImputer(strategy='most_frequent')),
                         ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))]), 
         categorical_features)
    ])
    
    # Train best model
    full_pipeline = Pipeline([('preprocessor', preprocessor),
                             ('classifier', RandomForestClassifier(n_estimators=200, max_depth=10, 
                                                                 min_samples_split=2, random_state=42))])
    
    full_pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_proba = full_pipeline.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_proba)
    
    # MLflow logging
    mlflow.set_experiment("Production_Pipeline")
    with mlflow.start_run(run_name="Automated_Training"):
        mlflow.log_param("model", "RandomForest_Prod")
        mlflow.log_metric("test_auc", auc)
        mlflow.sklearn.log_model(full_pipeline, "prod_model")
    
    # Save production model
    joblib.dump(full_pipeline, "models/heart_disease_pipeline_prod.joblib")
    
    logging.info(f"✅ Pipeline complete. Test AUC: {auc:.3f}")
    return auc

if __name__ == "__main__":
    train_model()
