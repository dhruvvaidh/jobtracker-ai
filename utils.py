from gmail_api import get_email_messages, get_email_message_details
import re
import json
import pandas as pd
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from tqdm import tqdm
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from microsoft import get_access_token, MS_GRAPH_BASE_URL, search_messages
import os
from load_dotenv import load_dotenv
import httpx
load_dotenv()



def get_emails(service,messages):
    emails = []
    for msg in messages:
        details = get_email_message_details(service,msg['id'])
        if details:
            emails.append(details)
            print(details)

    return emails

def download_emails_google(service,days:int = 1):

    query = f'subject:"application" newer_than:{days}d -subject:"credit card"'
    filtered_emails = get_email_messages(service, query=query, max_results=None)
    emails = get_emails(service,filtered_emails)

    return emails

def extract_application_info(raw_response: str) -> Optional[Dict[str, Any]]:
    """
    Given the LLM's raw response, return a Python dict if it contains JSON,
    or None if the response is exactly "None" (case-insensitive).
    """
    text = raw_response.strip()
    # strip markdown code fences
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    
    if text.lower() == 'none':
        return None
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # fallback: grab the first {...} block
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Could not parse JSON from response: {raw_response!r}")

def extract_emails(emails):
    # system + human templates
    system_message_template = """
    You are an assistant that analyzes whether a given email is a job application email.  
    - If it is a job application email, extract the following and present them in a JSON object:  
      1. "date_applied" (None if the email is not for Applied)
      2. “company_name”  
      3. “job_title”  
      4. “application_status” (Applied, Interview, Offer, Rejected)  
      5. "date_rejected" (None if not present)(None if the email is not for Rejected)(Date of receiving the rejection email)
      6. "interview_date" (None if not present)(Date of receiving the interview email)(None if the email is not for an Interview)
      7. "offer_date" (None if not present)(Date of receiving the offer email)(None if the email is not for an Offer)

    - If it is NOT a job application email, respond with:
      None
    """

    human_message_template = """
    Analyze the following email:

    {email_body}
    """

    template = ChatPromptTemplate([
        ("system", system_message_template),
        ("human", human_message_template)
    ])

    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.2
    )

    data = []
    for email in tqdm(emails):
        prompt_value = template.format_prompt(email_body=email)
        messages     = prompt_value.to_messages()
        response     = llm.invoke(input=messages)
        
        # Clean & parse the LLM's output
        parsed = extract_application_info(response.content)
        data.append(parsed)

    return data

def normalize_to_date(val):
    """
    Take a string or datetime-like value and return a Python date
    or None if it can't be parsed.
    """
    if not val:
        return None
    try:
        ts = pd.to_datetime(val, errors="raise")
        return ts.date()
    except Exception:
        try:
            dt = datetime.fromisoformat(val)
            return dt.date()
        except Exception:
            return None
        
def initialize_db(DATABASE_URL):
    # Database setup for SQL storage
    engine = create_engine(DATABASE_URL)

    # Ensure the job_applications table exists with job_id as primary key
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS job_applications (
            job_id TEXT PRIMARY KEY,
            date_applied DATE,
            company_name TEXT,
            job_title TEXT,
            application_status TEXT,
            date_rejected DATE,
            interview_date DATE,
            offer_date DATE
        )
        """))

    return engine

def download_outlook_emails():
    APPLICATION_ID = os.getenv('MICROSOFT_APPLICATION_ID')
    CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET')
    SCOPES = ['User.Read', 'Mail.ReadWrite']
    endpoint = f'{MS_GRAPH_BASE_URL}/me/messages'
    try:
        access_token = get_access_token(APPLICATION_ID,CLIENT_SECRET,scopes=SCOPES)
        headers = {
                'Authorization': 'Bearer' + access_token
            }

        search_query='Job Applications OR Rejection OR Interview'
        messages = search_messages(headers, search_query)
        emails = []
        for indx, mail_message in enumerate(messages):
            print(f'Email {indx + 1}')
            print('Subject:', mail_message['subject'])
            print('From: ', mail_message['from']['emailAddress']['name'], f"({mail_message['from']['emailAddress']['address']})")
            print('Received Date Time:', mail_message['receivedDateTime'])
            print('Body Preview: ', mail_message['bodyPreview'])
            print('-'*150)
            emails.append(f"""
            Subject: {mail_message['subject']}\n
            From: {mail_message['from']['emailAddress']['name']}({mail_message['from']['emailAddress']['address']})\n
            Received Date Time: {mail_message['receivedDateTime']} \n
            Body: {mail_message['bodyPreview']}
            """)

    except httpx.HTTPStatusError as e:
        print (f'HTTP Error: {e}')
    except Exception as e:
        print(f'Error: {e}')

    return emails