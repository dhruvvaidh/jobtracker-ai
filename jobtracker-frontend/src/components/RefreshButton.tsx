// src/components/RefreshButton.tsx
import React from "react";

interface Props {
  onClick: () => void;
}

export default function RefreshButton({ onClick }: Props) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "0.5rem 1rem",
        fontSize: "1rem",
        border: "1px solid #333",
        borderRadius: "4px",
        backgroundColor: "#fff",
        cursor: "pointer",
      }}
    >
      Refresh
    </button>
  );
}