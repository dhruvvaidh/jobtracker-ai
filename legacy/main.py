from gmail_api import init_gmail_service
from utils import download_emails,extract_emails, normalize_to_date
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import uuid

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Database setup for SQL storage
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///jobtracker.db")
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

    # Filter out None entries
    filtered = [d for d in data if d is not None]

    # Upsert each item in filtered into the database
    with engine.begin() as conn:
        for item in filtered:
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