# app.py (excerpt)

from fastapi import FastAPI, Depends, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import jwt
import os
from typing import Dict, List

# Replace these with your own values
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
JWT_ALGORITHM = "HS256"

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
class GoogleToken(BaseModel):
    token: str

# 3. POST /auth/google endpoint
@app.post("/auth/google")
async def auth_google(data: GoogleToken, response: Response):
    """
    1. Verify the ID token with Google.
    2. Generate a JWT for your own app.
    3. Set it as an HttpOnly cookie.
    4. Return some JSON if desired (e.g. { "status": "ok" }).
    """
    try:
        # Verify the ID token against Google
        idinfo = id_token.verify_oauth2_token(
            data.token, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")

    # Example: idinfo contains fields like 'email', 'email_verified', 'sub' (Google user ID), etc.
    if not idinfo.get("email_verified"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified by Google")

    user_email = idinfo["email"]
    user_id = idinfo["sub"]

    # TODO: (Optional) Create or lookup this user in your own DB.
    # For now, just embed email and sub in the JWT payload.
    payload = {
        "sub": user_id,
        "email": user_email,
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # Set as HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",      # prevents CSRF on cross-site requests
        secure=False,        # set True if you serve over HTTPS (in production)
        max_age=60 * 60 * 24  # e.g. 1 day
    )

    return {"status": "success"}


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

#7. 
@app.get("/auth/verify")
async def verify_login(request: Request):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"user_id": payload["user_id"], "email": payload["email"]}