from classify import classification, get_applications_by_status
# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/classify")
def classify_and_fetch():
    # 1) upsert new/updated applications
    classification()
    # 2) return per-status application details
    return get_applications_by_status()