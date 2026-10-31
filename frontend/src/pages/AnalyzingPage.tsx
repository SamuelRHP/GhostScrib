import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import type { JobResponse, JobStageName } from "@/types/api";

const STAGE_LABELS: Record<JobStageName, string> = {
  parsing: "Document Parsing & Hygiene",
  detection: "Primary Lukkinen Ensemble Detection",
  stylometry: "Sentence Structure & Stylometry Profiling",
  attribution: "Token Transition Attribution Analysis",
  citations: "Crossref & OpenAlex Citation Verification",
  scoring: "Provenance Aggregation & Transparency Report",
};

export default function AnalyzingPage(): React.ReactElement {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();

  const [job, setJob] = useState<JobResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    let isMounted = true;
    let timerId: ReturnType<typeof setTimeout>;

    const pollJob = async () => {
      try {
        const res = await fetch(`/api/jobs/${jobId}`);
        if (!res.ok) {
          if (res.status === 404) {
            throw new Error(`Analysis job '${jobId}' was not found.`);
          }
          throw new Error(`Failed to fetch job status (HTTP ${res.status})`);
        }

        const data: JobResponse = await res.json();
        if (!isMounted) return;

        setJob(data);

        if (data.status === "done") {
          // Navigate to completed report
          navigate(`/report/${jobId}`);
        } else if (data.status === "error") {
          setError(data.error?.message || "An unexpected error occurred during analysis.");
        } else {
          // Continue polling
          timerId = setTimeout(pollJob, 1000);
        }
      } catch (err: unknown) {
        if (!isMounted) return;
        const msg = err instanceof Error ? err.message : "Error connecting to server.";
        setError(msg);
      }
    };

    pollJob();

    return () => {
      isMounted = false;
      clearTimeout(timerId);
    };
  }, [jobId, navigate]);

  const stages = job?.stages || [
    { name: "parsing" as JobStageName, status: "running" },
    { name: "detection" as JobStageName, status: "pending" },
    { name: "stylometry" as JobStageName, status: "pending" },
    { name: "attribution" as JobStageName, status: "pending" },
    { name: "citations" as JobStageName, status: "pending" },
    { name: "scoring" as JobStageName, status: "pending" },
  ];

  const progressPct = job ? Math.round(job.progress * 100) : 10;

  return (
    <div style={{ padding: "var(--spacing-8, 32px)", maxWidth: "700px", margin: "0 auto" }}>
      <div
        style={{
          border: "1px solid var(--color-border, #e2e8f0)",
          padding: "var(--spacing-8, 32px)",
          borderRadius: "var(--radius-lg, 12px)",
          backgroundColor: "var(--color-bg-card, #ffffff)",
          boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.05)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "var(--spacing-6, 24px)" }}>
          <h2 style={{ margin: "0 0 var(--spacing-2, 8px) 0", fontSize: "var(--font-size-xl, 20px)" }}>
            Analyzing Manuscript...
          </h2>
          <p style={{ color: "var(--color-text-secondary, #64748b)", margin: "0 0 var(--spacing-3, 12px) 0", fontSize: "14px" }}>
            Job ID: <code style={{ backgroundColor: "#f1f5f9", padding: "2px 6px", borderRadius: "4px" }}>{jobId ?? "unknown"}</code>
          </p>

          {/* Progress Bar */}
          <div
            style={{
              width: "100%",
              height: "10px",
              backgroundColor: "#e2e8f0",
              borderRadius: "5px",
              overflow: "hidden",
              margin: "16px 0 8px 0",
            }}
          >
            <div
              style={{
                width: `${progressPct}%`,
                height: "100%",
                backgroundColor: "var(--color-primary, #2563eb)",
                transition: "width 0.3s ease-in-out",
              }}
            />
          </div>
          <div style={{ fontSize: "13px", color: "var(--color-text-secondary, #64748b)" }}>
            {progressPct}% complete
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div
            role="alert"
            style={{
              padding: "12px 16px",
              backgroundColor: "rgba(220, 38, 38, 0.08)",
              border: "1px solid rgba(220, 38, 38, 0.3)",
              borderRadius: "8px",
              color: "#b91c1c",
              marginBottom: "20px",
              fontSize: "14px",
            }}
          >
            <strong>Analysis Failed:</strong> {error}
            <div style={{ marginTop: "10px" }}>
              <button
                type="button"
                onClick={() => navigate("/")}
                style={{
                  padding: "6px 14px",
                  fontSize: "13px",
                  backgroundColor: "#b91c1c",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                }}
              >
                Return to Upload
              </button>
            </div>
          </div>
        )}

        {/* 6-Stage Progress Stepper */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {stages.map((st, idx) => {
            const isDone = st.status === "done";
            const isRunning = st.status === "running";
            const isSkipped = st.status === "skipped";
            const isError = st.status === "error";

            let iconColor = "#94a3b8";
            let iconText = `${idx + 1}`;
            let textColor = "#64748b";

            if (isDone) {
              iconColor = "#10b981";
              iconText = "✓";
              textColor = "#1e293b";
            } else if (isRunning) {
              iconColor = "#2563eb";
              iconText = "●";
              textColor = "#1e293b";
            } else if (isSkipped) {
              iconColor = "#94a3b8";
              iconText = "–";
              textColor = "#94a3b8";
            } else if (isError) {
              iconColor = "#dc2626";
              iconText = "✕";
              textColor = "#dc2626";
            }

            return (
              <div
                key={st.name}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  padding: "8px 12px",
                  borderRadius: "6px",
                  backgroundColor: isRunning ? "rgba(37, 99, 235, 0.05)" : "transparent",
                }}
              >
                <div
                  style={{
                    width: "28px",
                    height: "28px",
                    borderRadius: "50%",
                    backgroundColor: iconColor,
                    color: "#ffffff",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: "bold",
                    fontSize: "13px",
                    flexShrink: 0,
                  }}
                >
                  {iconText}
                </div>
                <div style={{ flex: 1, fontSize: "14px", fontWeight: isRunning ? 600 : 400, color: textColor }}>
                  {STAGE_LABELS[st.name as JobStageName] || st.name}
                </div>
                <div style={{ fontSize: "12px", textTransform: "capitalize", color: iconColor, fontWeight: 500 }}>
                  {st.status}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
