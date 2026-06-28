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
    # FIX: Set reload=False to prevent multiple processes from locking the Qdrant DB
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=False)