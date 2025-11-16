from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import joblib
import pandas as pd
import logging
import time
import json

# --- OpenTelemetry Imports ---
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

# --- Setup Tracer ---
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(CloudTraceSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# --- Setup Structured Logging ---
logger = logging.getLogger("iris-classifier-service")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(json.dumps({
    "severity": "%(levelname)s",
    "message": "%(message)s",
    "timestamp": "%(asctime)s"
}))
handler.setFormatter(formatter)
logger.addHandler(handler)

# --- FastAPI App & State ---
app = FastAPI(title="🌸 Iris Classifier API")
app_state = {"model": None, "is_ready": False, "is_alive": True}

# --- Schemas ---
class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

class PredictionOut(BaseModel):
    predicted_class: str

# --- Startup & Probes ---
@app.on_event("startup")
async def startup_event():
    try:
        app_state["model"] = joblib.load("model.joblib")
        app_state["is_ready"] = True
        logger.info(json.dumps({"event": "startup", "status": "model_loaded"}))
    except Exception as e:
        app_state["is_alive"] = False 
        logger.critical(json.dumps({
            "event": "startup_failure",
            "error": str(e)
        }))

@app.get("/live_check", tags=["Probe"])
async def liveness_probe():
    if app_state["is_alive"]:
        return {"status": "alive"}
    return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/ready_check", tags=["Probe"])
async def readiness_probe():
    if app_state["is_ready"]:
        return {"status": "ready"}
    return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

# --- Middleware & Exception Handlers ---
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Process-Time-ms"] = str(duration)
    return response

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, "032x")
    logger.exception(json.dumps({
        "event": "unhandled_exception",
        "trace_id": trace_id,
        "path": str(request.url),
        "error": str(exc)
    }))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "trace_id": trace_id},
    )

# --- API Routes ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Iris Classifier API!"}

@app.post("/predict", response_model=PredictionOut)
async def predict_species(data: IrisInput, request: Request):
    if not app_state["is_ready"] or app_state["model"] is None:
        raise HTTPException(status_code=500, detail="Model not loaded or app not ready")

    with tracer.start_as_current_span("model_inference") as span:
        start_time = time.time()
        trace_id = format(span.get_span_context().trace_id, "032x")

        try:
            input_data = data.dict()
            input_df = pd.DataFrame([input_data])

            model = app_state["model"]
            y_pred = model.predict(input_df)[0]
            y = y_pred.item() if hasattr(y_pred, "item") else str(y_pred)
            
            result = {"predicted_class": y}
            latency = round((time.time() - start_time) * 1000, 2)

            logger.info(json.dumps({
                "event": "prediction",
                "trace_id": trace_id,
                "input": input_data,
                "result": result,
                "latency_ms": latency,
                "status": "success"
            }))

            return result

        except Exception as e:
            logger.exception(json.dumps({
                "event": "prediction_error",
                "trace_id": trace_id,
                "error": str(e)
            }))
            raise HTTPException(status_code=500, detail="Prediction failed")