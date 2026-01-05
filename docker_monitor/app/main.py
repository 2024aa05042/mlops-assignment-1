from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import uvicorn
import logging
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, REGISTRY
from prometheus_fastapi_instrumentator import Instrumentator
from typing import Optional
import json

# Prometheus metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration')
ACTIVE_USERS = Gauge('api_active_users', 'Active users')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HeartDiseaseAPI")

app = FastAPI(title="Heart Disease Prediction API with Monitoring")
instrumentator = Instrumentator().instrument(app).expose(app)

# Load model
model = joblib.load("models/heart_disease_pipeline_prod.joblib")
PREDICTIONS = Counter('model_predictions_total', 'Model predictions', ['prediction'])

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

@app.middleware("http")
async def prometheus_metrics(request: Request, call_next):
    start_time = datetime.now()
    ACTIVE_USERS.inc()
    
    try:
        response = await call_next(request)
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, 
                           status=response.status_code).inc()
        ACTIVE_USERS.dec()
        return response
    except Exception as e:
        ACTIVE_USERS.dec()
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, 
                           status=500).inc()
        raise

@app.get("/")
async def root():
    logger.info("Health check - API alive")
    return {"message": "Heart Disease API (MONITORED) ✅", "metrics": "/metrics"}

@app.post("/predict")
async def predict(patient: HeartPatient, request: Request):
    start_time = datetime.now()
    logger.info(f"PREDICTION REQUEST: {patient.dict()}")
    
    try:
        feature_columns = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
                          'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
        test_df = pd.DataFrame([patient.dict()])[feature_columns]
        
        prediction = int(model.predict(test_df)[0])
        probability = float(model.predict_proba(test_df)[0][1])
        PREDICTIONS.labels(prediction=str(prediction)).inc()
        
        risk_level = "HIGH RISK" if probability > 0.5 else "LOW RISK"
        
        duration = (datetime.now() - start_time).total_seconds()
        REQUEST_DURATION.observe(duration)
        
        logger.info(f"PREDICTION: {prediction}, CONF: {probability:.3f}, DURATION: {duration}s")
        
        return {
            "prediction": prediction,
            "confidence": round(probability, 4),
            "risk_level": risk_level,
            "response_time": f"{duration:.3f}s"
        }
        
    except Exception as e:
        logger.error(f"PREDICTION ERROR: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
