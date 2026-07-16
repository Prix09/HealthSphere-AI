from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api import auth, records, analytics, assessment

app = FastAPI(title="HealthSphere AI", openapi_url="/api/v1/openapi.json")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(records.router, prefix="/api/records", tags=["records"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])
app.include_router(assessment.router, prefix="/api/assessment", tags=["assessment"])

@app.get("/healthz", tags=["health"])
def health_check():
    return {"status": "ok"}
