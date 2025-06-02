from fastapi import FastAPI, Depends, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import jwt
import os
from typing import Dict, List
import google.oauth2

# Replace these with your own values
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = 3600

app = FastAPI()

# 1. CORS middleware (allow frontend origin with credentials)
origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# 2. Schemas for request bodies
# In app.py
class GoogleToken(BaseModel):
    token: str

# 3. Google Authentication
@app.post("/auth/google")
async def auth_google(payload: GoogleToken, response: Response):
    # 1) Verify the Google ID token
    id_info = google.oauth2.id_token.verify_oauth2_token(
        payload.token,
        google.auth.transport.requests.Request(),
        GOOGLE_CLIENT_ID
    )

    # 2) Build your own JWT
    import time
    jwt_payload = {
        "user_id": id_info["sub"],
        "email": id_info["email"],
        "exp": time.time() + JWT_EXPIRE_SECONDS
    }
    my_jwt = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # 3) Set the HttpOnly cookie “token”
    response.set_cookie(
        key="token",
        value=my_jwt,
        httponly=True,
        secure=False,    # true in prod
        samesite="lax",  # or "none" in prod with secure=True
        max_age=JWT_EXPIRE_SECONDS,
        path="/",
    )

    # 4) Return success
    return {"email": id_info["email"]}


# 4. Utility function to get current user from cookie (for protected routes)
from fastapi.security import HTTPBearer
from fastapi import Header

# Example dependency:
def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload  # contains "sub" and "email"


# 5. Protected GET /applications_by_status
@app.get("/applications_by_status", dependencies=[Depends(get_current_user)])
async def applications_by_status():
    """
    This endpoint should already call get_applications_by_status() 
    and return a dictionary. Just ensure it's protected.
    """
    from utils import get_applications_by_status  # wherever that function lives
    return get_applications_by_status()


# 6. Protected POST /classify
@app.post("/classify", dependencies=[Depends(get_current_user)])
async def classify_emails():
    """
    Runs classify.py, updates the database, then returns something (e.g. {"status":"updated"}).
    """
    from classify import run_classification  # assume you have a function like this
    run_classification()
    return {"status": "classification complete"}

#7. Verifying the authentication
@app.get("/auth/verify")
async def verify_login(request: Request):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    return {"user_id": payload["user_id"], "email": payload["email"]}