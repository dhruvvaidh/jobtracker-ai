from gmail_api import init_gmail_service, get_email_messages, get_email_message_details
import os
import re
import json
import csv
import pandas as pd
from sqlalchemy import create_engine
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from tqdm import tqdm

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Database setup for SQL storage
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///jobtracker.db")
engine = create_engine(DATABASE_URL)

def get_emails(messages):
    emails = []
    for msg in messages:
        details = get_email_message_details(service,msg['id'])
        if details:
            emails.append(details)
            print(details)

    return emails

def download_emails(service,days:int = 1):

    query = f'subject:"application" newer_than:{days}d -subject:"credit card'
    filter_emails = get_email_messages(service, query=query, max_results=None)
    emails = get_emails(filter_emails)

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
      1. “company_name”  
      2. “job_title”  
      3. “application_status” (Applied, Interview, Offer, Rejected)  
      4. “important_dates” (list of any dates mentioned)  
      5. “action_items” (list of any required follow-up tasks)  

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

if __name__ == "__main__":

    # Authentication
    client_file = 'credentials.json'
    service = init_gmail_service(client_file)

    #Downloading Emails
    emails = download_emails(service,2)
    print(len(emails))

    # Extracting Job Application Emails
    data = extract_emails(emails)

    print(f"Number of Job Application emails: {len(data)}")

    # Convert list of application info dicts into a pandas DataFrame
    filtered = [d for d in data if d is not None]
    df = pd.DataFrame(filtered)
    df.insert(0, 'job_id', [f"Job_{i:02d}" for i in range(1, len(df) + 1)])
    # make it the index so lookups naturally key off job_id
    df.set_index('job_id', inplace=True)
    df.to_csv('job_applications.csv', index=False)
    df.to_sql('job_applications', con=engine, if_exists='append', index=False)
    print(df)
