// src/components/StatusTile.tsx
import React from "react";
import type {
  AppliedRecord,
  InterviewRecord,
  OfferRecord,
  RejectedRecord,
} from "../types/status";

interface CommonProps {
  company_name: string;
  job_title: string;
  date_applied: string;
}

interface Props {
  title: "Applied" | "Interview" | "Offer" | "Rejected";
  records: Array<
    | AppliedRecord
    | InterviewRecord
    | OfferRecord
    | RejectedRecord
  >;
}

export default function StatusTile({ title, records }: Props) {
  return (
    <div
      style={{
        backgroundColor: "#fff",
        border: "1px solid #ddd",
        borderRadius: "8px",
        padding: "1rem",
      }}
    >
      <h2 style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>
        {title} ({records.length})
      </h2>

      {records.length === 0 && <p>No entries.</p>}

      {records.map((rec, idx) => {
        return (
          <div
            key={idx}
            style={{
              padding: "0.75rem",
              marginBottom: "0.75rem",
              border: "1px solid #eee",
              borderRadius: "4px",
            }}
          >
            <p>
              <strong>Company:</strong> {rec.company_name}
            </p>
            <p>
              <strong>Title:</strong> {rec.job_title}
            </p>
            <p>
              <strong>Date Applied:</strong> {rec.date_applied}
            </p>

            {/* Conditionally render fields based on status */}
            {"interview_date" in rec && rec.interview_date && (
              <p>
                <strong>Interview Date:</strong> {rec.interview_date}
              </p>
            )}
            {"offer_date" in rec && rec.offer_date && (
              <p>
                <strong>Offer Date:</strong> {rec.offer_date}
              </p>
            )}
            {"date_rejected" in rec && rec.date_rejected && (
              <p>
                <strong>Date Rejected:</strong> {rec.date_rejected}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}