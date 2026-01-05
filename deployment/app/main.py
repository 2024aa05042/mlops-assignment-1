from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline



app = FastAPI(title="Heart Disease Prediction API")

# Resolve model path relative to this file
BASE_DIR = os.path.dirname(__file__)
MODEL_FILENAME = "heart_disease_pipeline_prod.joblib"
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "models", MODEL_FILENAME))
#MODEL_PATH = "/app/models/heart_disease_pipeline_prod.joblib"
import sklearn, sys
print("API ENV:", sys.executable, sklearn.__version__)
# Try to load model but don't crash the app at import time; record any error
model = None
load_error = None
try:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    print(f"Loading model from: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
except Exception as e:
    load_error = str(e)
    # Print stack for local debugging; the server will stay up and return a 503 on requests
    import traceback
    print(f"Failed to load model: {load_error}")
    traceback.print_exc()



class HeartPatient(BaseModel):
    age: float
    sex: int
    cp: int
    trestbps: float
    chol: float
    fbs: int
    restecg: int
    thalach: float
    exang: int
    oldpeak: float
    slope: int
    ca: float
    thal: int


@app.get("/")
def read_root():
    return {"message": "Heart Disease Prediction API ✅"}


@app.post("/predict")
def predict(data: HeartPatient):
    try:
        # Convert to DataFrame with column names (required for sklearn ColumnTransformer)
        column_names = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
                       'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
        features = pd.DataFrame([[data.age, data.sex, data.cp, data.trestbps, data.chol,
                                  data.fbs, data.restecg, data.thalach, data.exang,
                                  data.oldpeak, data.slope, data.ca, data.thal]], 
                                columns=column_names)

        # Predict
        prediction = model.predict(features)[0]
        probability = None
        # Some models may not implement predict_proba
        if hasattr(model, "predict_proba"):
            probability = float(model.predict_proba(features)[0][1])
        else:
            probability = float(model.predict(features)[0])

        return {
            "prediction": int(prediction),
            "probability": float(probability),
            "risk": "HIGH" if probability > 0.5 else "LOW"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
