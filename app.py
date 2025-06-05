from fastapi import FastAPI, Depends, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
import os
from typing import Dict, List
import time
import httpx

# Replace these with your own values
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = 3600

app = FastAPI()

# 1. CORS middleware (allow frontend origin with credentials)
origins = [
    "https://localhost:5173",
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
user_gmail_token_store: dict[str, str] = {}

class GoogleLoginPayload(BaseModel):
    access_token: str

@app.post("/auth/google")
async def auth_google(payload: GoogleLoginPayload, response: Response):
    # 1) Use access_token to get user info from Google API
    async with httpx.AsyncClient() as client:
        userinfo_response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {payload.access_token}"}
        )
    if userinfo_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid access token.")
    id_info = userinfo_response.json()

    google_user_id = id_info.get("sub")
    email = id_info.get("email")

    if not google_user_id or not email:
        raise HTTPException(status_code=400, detail="Failed to retrieve user info.")

    # 2) Issue a session JWT for your own backend
    jwt_payload = {
        "user_id": google_user_id,
        "email": email,
        "exp": time.time() + JWT_EXPIRE_SECONDS,
    }
    my_jwt = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    response.set_cookie(
        key="token",
        value=my_jwt,
        httponly=True,
        secure=True,  # True in production (HTTPS)
        samesite="none", # Or "none" + secure=True in prod
        max_age=JWT_EXPIRE_SECONDS,
        path="/",
    )

    # 3) Store the user’s Gmail access token so we can call Gmail API later
    user_gmail_token_store[google_user_id] = payload.access_token

    return {"email": email}


@app.get("/auth/verify")
async def verify_login(request: Request):
    print(">>> [VERIFY] Incoming cookies:", request.cookies)
    token = request.cookies.get("token")
    if not token:
        print(">>> [VERIFY] No 'token' cookie found → returning 401")
        raise HTTPException(status_code=401, detail="Not authenticated. Did not recieve the token")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        print(">>> [VERIFY] Found token but JWT.decode failed. (Expired or invalid.)")
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    
    print(f">>> [VERIFY] JWT payload:", payload)
    return {"user_id": payload["user_id"], "email": payload["email"]}

# 4. Utility function to get current user from cookie (for protected routes)
from fastapi.security import HTTPBearer
from fastapi import Header

# Example dependency:
def get_current_user(request: Request):
    token = request.cookies.get("token")
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
    from classify import get_applications_by_status
    return get_applications_by_status()


# 6. Protected POST /classify
@app.post("/classify", dependencies=[Depends(get_current_user)])
async def classify_emails(request: Request):
    """
    Decode our session JWT, look up the user's Gmail access_token, and
    pass that token into classification(...).
    """
    # 1) Read the session cookie
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    # 2) Decode our own JWT to get google_user_id
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired session token.")

    google_user_id = payload.get("user_id")
    if not google_user_id:
        raise HTTPException(status_code=400, detail="Invalid session payload (no user_id).")

    # 3) Look up the stored Gmail access token for that user
    access_token = user_gmail_token_store.get(google_user_id)
    if not access_token:
        raise HTTPException(status_code=400, detail="No Gmail access token stored for this user.")

    # 4) Call classification(...) passing in that access_token
    from classify import classification
    classification(access_token)

    return {"status": "classification complete"}

# 7. Logging out of the application
@app.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="token", path="/")
    return {"message": "Logged out"}