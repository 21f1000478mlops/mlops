# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="🌸 Iris Classifier API")

# Load model
try:
    model = joblib.load("model.joblib")
except Exception as e:
    model = None
    print(f"Warning: could not load model.joblib -> {e}")

# ----- Schemas -----
class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

class PredictionOut(BaseModel):
    predicted_class: str  # return as JSON-safe string

# ----- Routes -----
@app.get("/")
def read_root():
    return {"message": "Welcome to the Iris Classifier API!"}

@app.get("/health")
def health():
    return {"model_loaded": model is not None}

@app.post("/predict", response_model=PredictionOut)
def predict_species(data: IrisInput):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # Convert input to DataFrame expected by the model
    input_df = pd.DataFrame([data.dict()])

    # Predict and convert to JSON-safe scalar
    y = model.predict(input_df)[0]
    y = y.item() if hasattr(y, "item") else str(y)

    return {"predicted_class": y}

# Comment for video demo - Roll no: 21F1000478