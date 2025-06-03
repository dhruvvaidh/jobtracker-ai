from gmail_api import init_gmail_service
from gmail_auth import build_user_gmail_service
from utils import download_emails,extract_emails, normalize_to_date, initialize_db
import os
from tqdm import tqdm
from sqlalchemy import text
from dotenv import load_dotenv
import uuid

load_dotenv()

def classification(access_token:str):
    DATABASE_URL = os.getenv("DATABASE_URL")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    engine = initialize_db(DATABASE_URL)

    # Authentication
    #client_file = 'credentials.json'
    #service = init_gmail_service(client_file)

    service = build_user_gmail_service(access_token)

    #Downloading Emails
    emails = download_emails(service,2)
    print(len(emails))

    # Extracting Job Application Emails
    data = extract_emails(emails)

    print(f"Number of Job Application emails: {len(data)}")

    # Filter out None entries
    filtered = [d for d in data if d is not None]

    # Upsert each item in filtered into the database
    with engine.begin() as conn:
        for item in tqdm(filtered):
            company = item.get('company_name')
            title = item.get('job_title')
            date_applied = normalize_to_date(item.get('date_applied'))
            application_status = item.get('application_status')
            date_rejected = normalize_to_date(item.get('date_rejected'))
            interview_date = normalize_to_date(item.get('interview_date'))
            offer_date = normalize_to_date(item.get('offer_date'))
            existing = conn.execute(
                text("SELECT job_id FROM job_applications WHERE company_name = :company AND job_title = :title"),
                {"company": company, "title": title}
            ).fetchone()

            if existing:
                job_id = existing[0]
                # Conditional update based on application_status
                if application_status == "Applied":
                    conn.execute(text("""
                        UPDATE job_applications
                        SET date_applied = :date_applied,
                            application_status = :application_status
                        WHERE job_id = :job_id
                    """), {
                        "date_applied": date_applied,
                        "application_status": application_status,
                        "job_id": job_id
                    })
                elif application_status == "Rejected":
                    conn.execute(text("""
                        UPDATE job_applications
                        SET date_rejected = :date_rejected,
                            application_status = :application_status
                        WHERE job_id = :job_id
                    """), {
                        "date_rejected": date_rejected,
                        "application_status": application_status,
                        "job_id": job_id
                    })
                elif application_status == "Interview":
                    conn.execute(text("""
                        UPDATE job_applications
                        SET interview_date = :interview_date,
                            application_status = :application_status
                        WHERE job_id = :job_id
                    """), {
                        "interview_date": interview_date,
                        "application_status": application_status,
                        "job_id": job_id
                    })
                elif application_status == "Offer":
                    conn.execute(text("""
                        UPDATE job_applications
                        SET offer_date = :offer_date,
                            application_status = :application_status
                        WHERE job_id = :job_id
                    """), {
                        "offer_date": offer_date,
                        "application_status": application_status,
                        "job_id": job_id
                    })
            else:
                job_id = str(uuid.uuid4())
                params = {
                    "job_id": job_id,
                    "date_applied": date_applied,
                    "company_name": company,
                    "job_title": title,
                    "application_status": application_status,
                    "date_rejected": date_rejected,
                    "interview_date": interview_date,
                    "offer_date": offer_date
                }
                conn.execute(
                    text("""
                    INSERT INTO job_applications (job_id, date_applied, company_name, job_title, application_status, date_rejected, interview_date, offer_date)
                    VALUES (:job_id, :date_applied, :company_name, :job_title, :application_status, :date_rejected, :interview_date, :offer_date)
                    """),
                    params
                )

    print(filtered)

def get_applications_by_status() -> dict:
    """
    Returns a dict mapping each status to a list of records.
    Each record is a dict with only the fields relevant for that status.
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = initialize_db(DATABASE_URL)

    statuses = ["Applied", "Rejected", "Interview", "Offer"]
    result_dict: dict[str, list[dict]] = {}

    with engine.begin() as conn:
        for status in tqdm(statuses):
            if status == "Applied":
                stmt = text("""
                    SELECT company_name, job_title, date_applied
                    FROM job_applications
                    WHERE application_status = :status
                """)
            elif status == "Rejected":
                stmt = text("""
                    SELECT company_name, job_title, date_applied, date_rejected
                    FROM job_applications
                    WHERE application_status = :status
                """)
            elif status == "Interview":
                stmt = text("""
                    SELECT company_name, job_title, date_applied, interview_date
                    FROM job_applications
                    WHERE application_status = :status
                """)
            else:  # Offer
                stmt = text("""
                    SELECT company_name, job_title, date_applied, interview_date, offer_date
                    FROM job_applications
                    WHERE application_status = :status
                """)

            rows = conn.execute(stmt, {"status": status}).mappings().all()
            # .mappings() gives each row as dict-like
            result_dict[status] = [dict(r) for r in rows]

    return result_dict