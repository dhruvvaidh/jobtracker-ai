import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

def create_service(client_secret_file, api_name, api_version, scopes, prefix=''):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    # Ensure scopes is a list (or convert to list if tuple)
    SCOPES = list(scopes) if isinstance(scopes, (list, tuple)) else [scopes]
    creds = None
    working_dir = os.getcwd()
    token_dir = 'token files'
    token_file = f'token_{API_SERVICE_NAME}_{API_VERSION}_{prefix}.json'
    
    # Check if token directory exists; if not, create it.
    token_path = os.path.join(working_dir, token_dir)
    if not os.path.exists(token_path):
        os.mkdir(token_path)
    
    token_file_path = os.path.join(token_path, token_file)
    if os.path.exists(token_file_path):
        creds = Credentials.from_authorized_user_file(token_file_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file_path, 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)
        print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {API_SERVICE_NAME}')
        os.remove(token_file_path)
        return None

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt

def build_user_gmail_service(access_token: str, api_name="gmail", api_version="v1"):
    if not access_token:
        raise ValueError("Missing access token for Gmail service.")
    creds = Credentials(token=access_token)
    service = build(api_name, api_version, credentials=creds, static_discovery=False)
    return service