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

load_dotenv()



def get_emails(service,messages):
    emails = []
    for msg in messages:
        details = get_email_message_details(service,msg['id'])
        if details:
            emails.append(details)
            print(details)

    return emails

def download_emails(service,days:int = 1):

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
      5. "date_rejected" (None if not present)(None if the email is not for Rejected)
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
        response     = llm(messages=messages)
        
        # Clean & parse the LLM's output
        parsed = extract_application_info(response.content)
        data.append(parsed)
        #print(parsed)         # dict or None
        #print(type(parsed))   # <class 'dict'> or <class 'NoneType'>

    return data

def normalize_to_date(val):
    """
    Take a string or datetime-like value and return a Python date
    or None if it can't be parsed.
    """
    if not val:
        return None
    # Try pandas’ parser first (very forgiving), fallback to datetime.fromisoformat
    try:
        ts = pd.to_datetime(val, errors="raise")
        return ts.date()
    except Exception:
        try:
            dt = datetime.fromisoformat(val)
            return dt.date()
        except Exception:
            return None