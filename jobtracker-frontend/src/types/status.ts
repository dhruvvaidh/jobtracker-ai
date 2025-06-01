// src/types/status.ts

export interface AppliedRecord {
  company_name: string;
  job_title: string;
  date_applied: string; // "YYYY-MM-DD"
}

export interface InterviewRecord {
  company_name: string;
  job_title: string;
  date_applied: string;
  interview_date: string;
}

export interface OfferRecord {
  company_name: string;
  job_title: string;
  date_applied: string;
  interview_date: string;
  offer_date: string;
}

export interface RejectedRecord {
  company_name: string;
  job_title: string;
  date_applied: string;
  date_rejected: string;
}

// The shape returned by GET /applications_by_status
export interface ApplicationsByStatus {
  Applied: AppliedRecord[];
  Interview: InterviewRecord[];
  Offer: OfferRecord[];
  Rejected: RejectedRecord[];
}