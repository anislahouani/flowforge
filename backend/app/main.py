from fastapi import FastAPI

app = FastAPI(title="FlowForge API", version="0.1.0")

@app.get("/health")

def health_check():
    return { "status": "ok", "service": "flowforge-api" } 
