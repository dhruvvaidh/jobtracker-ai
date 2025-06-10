import os
import webbrowser
import msal
import httpx
from dotenv import load_dotenv

load_dotenv()
MS_GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0'

def get_access_token (application_id, client_secret, scopes):
    client=msal.ConfidentialClientApplication(
    client_id=application_id,
    client_credential=client_secret,
    authority='https://login.microsoftonline.com/consumers/'
    )
    # Check if there is a refresh token stored
    refresh_token = None
    if os.path.exists('refresh_token.txt'):
        with open('refresh_token.txt', 'r') as file:
            refresh_token = file.read().strip()

    if refresh_token:
        # Try to acquire a new access token using the refresh token
        token_response = client.acquire_token_by_refresh_token(refresh_token, scopes=scopes)
    else:
        # No refresh token, proceed with the authorization code flow
        auth_request_url = client.get_authorization_request_url(scopes)
        webbrowser.open(auth_request_url)
        authorization_code = input('Enter the authorization code: ')

        if not authorization_code:
            raise ValueError("Authorization code is empty")
        
        token_response = client.acquire_token_by_authorization_code(
            code=authorization_code,
            scopes=scopes
        )


    if 'access_token' in token_response:
        # Store the refresh token securely
        if 'refresh_token' in token_response:
            with open('refresh_token.txt', 'w') as file:
                file.write(token_response['refresh_token'])
            return token_response['access_token']
        else:
            raise Exception('Failed to acquire access token: ' + str(token_response))
        

def search_messages(headers, search_query, filter=None, folder_id=None, fields='*', top=5, max_results=100):
    print('Setting Endpoint')
    if folder_id is None:
        endpoint = f'{MS_GRAPH_BASE_URL}/me/messages'
    else:
        endpoint = f'{MS_GRAPH_BASE_URL}/me/mailFolders/{folder_id}/messages'
    print('Formulating Search Query')
    params = {
        '$search': f'"{search_query}"',
        '$filter': filter,
        '$select': fields,
        '$top': min(top, max_results),
    }
    messages = []
    next_link = endpoint
    while next_link and len(messages) < max_results:
        response = httpx.get(next_link, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code != 200:
            raise Exception(f'Failed to retrieve emails: {response.json()}')
    
        json_response = response.json()
        messages.extend(json_response.get('value', []))
        next_link = json_response.get('@odata.nextLink', None)
        params=None # Clear params for subsequent requests
        if next_link and len(messages) + top > max_results:
            params = {
            '$top': max_results - len(messages)
            }
    return messages[:max_results]