import warnings
# Suppress the specific websockets/uvicorn deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="uvicorn")

from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="SD-WAN Copilot API",
    description="Air-Gapped Predictive NOC Copilot API for MPLS Operations",
    version="1.0.0"
)

# Include the routes defined in routes.py
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    # Increased timeout_keep_alive to 30 seconds to keep the pool active between telemetry loops
    uvicorn.run(
        "api.app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False, 
        timeout_keep_alive=30 
    )