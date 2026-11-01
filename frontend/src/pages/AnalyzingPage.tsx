import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import type { JobResponse, JobStage, JobStageName } from "@/types/api";

const STAGE_LABELS: Record<JobStageName, string> = {
  parsing: "Document Extraction & Structure Analysis",
  detection: "Multi-Model AI Probability Detection",
  stylometry: "Statistical Stylometry & Burstiness",
  attribution: "Fingerprint Model Attribution (Experimental)",
  citations: "Crossref Reference Verification & DOI Resolution",
  scoring: "Composite Provenance Synthesis",
};

export default function AnalyzingPage(): React.ReactElement {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();

  const [job, setJob] = useState<JobResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      setError("No job ID provided.");
      return;
    }

    let isMounted = true;
    let timerId: NodeJS.Timeout | null = null;

    const pollStatus = async () => {
      try {
        const res = await fetch(`/api/jobs/${jobId}`);
        if (!res.ok) {
          throw new Error(`Failed to fetch job status (HTTP ${res.status})`);
        }
        const data: JobResponse = await res.json();
        if (!isMounted) return;

        setJob(data);

        if (data.status === "done" || (data.status as string) === "completed") {
          navigate(`/report/${jobId}`);
        } else if (data.status === "error" || (data.status as string) === "failed") {
          setError(data.error?.message || "Analysis failed.");
        } else {
          // Poll every 1 second while pending/processing
          timerId = setTimeout(pollStatus, 1000);
        }
      } catch (err: unknown) {
        if (!isMounted) return;
        const msg = err instanceof Error ? err.message : "Error polling job status.";
        setError(msg);
      }
    };

    pollStatus();

    return () => {
      isMounted = false;
      if (timerId) clearTimeout(timerId);
    };
  }, [jobId, navigate]);

  const stages: JobStage[] = job?.stages || [
    { name: "parsing", status: "pending" },
    { name: "detection", status: "pending" },
    { name: "stylometry", status: "pending" },
    { name: "attribution", status: "pending" },
    { name: "citations", status: "pending" },
    { name: "scoring", status: "pending" },
  ];

  const progressPct = job ? Math.round(job.progress * 100) : 10;

  return (
    <div style={{ padding: "var(--spacing-8) var(--spacing-4)", maxWidth: "720px", margin: "0 auto" }}>
      <div
        style={{
          border: "1px solid var(--color-border)",
          padding: "var(--spacing-8)",
          borderRadius: "var(--radius-card)",
          backgroundColor: "var(--color-bg-card)",
          boxShadow: "var(--shadow-card)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "var(--spacing-6)" }}>
          <h2 style={{ margin: "0 0 var(--spacing-2) 0", fontSize: "var(--font-size-2xl)", color: "var(--color-text)" }}>
            Analyzing Manuscript...
          </h2>
          <p style={{ color: "var(--color-text-muted)", margin: "0 0 var(--spacing-4) 0", fontSize: "var(--font-size-sm)" }}>
            Job ID:{" "}
            <code
              style={{
                backgroundColor: "var(--color-surface)",
                padding: "var(--spacing-1) var(--spacing-2)",
                borderRadius: "var(--radius-chip)",
                color: "var(--color-text)",
                fontFamily: "var(--font-family-mono)",
              }}
            >
              {jobId ?? "unknown"}
            </code>
          </p>

          {/* Progress Bar */}
          <div
            style={{
              width: "100%",
              height: "10px",
              backgroundColor: "var(--color-surface)",
              borderRadius: "var(--radius-pill)",
              overflow: "hidden",
              margin: "var(--spacing-4) 0 var(--spacing-2) 0",
            }}
          >
            <div
              style={{
                width: `${progressPct}%`,
                height: "100%",
                backgroundColor: "var(--color-primary)",
                borderRadius: "var(--radius-pill)",
                transition: "width 0.3s ease-in-out",
              }}
            />
          </div>
          <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)" }}>
            {progressPct}% complete
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div
            role="alert"
            style={{
              padding: "var(--spacing-3) var(--spacing-4)",
              backgroundColor: "var(--color-amber-bg)",
              border: "1px solid var(--color-amber-border)",
              borderRadius: "var(--radius-control)",
              color: "var(--color-amber-text)",
              marginBottom: "var(--spacing-5)",
              fontSize: "var(--font-size-sm)",
            }}
          >
            <strong>Analysis Failed:</strong> {error}
            <div style={{ marginTop: "var(--spacing-2)" }}>
              <button
                type="button"
                onClick={() => navigate("/")}
                style={{
                  padding: "var(--spacing-1) var(--spacing-3)",
                  fontSize: "var(--font-size-xs)",
                  backgroundColor: "var(--color-primary)",
                  color: "var(--color-text-on-dark)",
                  border: "none",
                  borderRadius: "var(--radius-control)",
                  cursor: "pointer",
                }}
              >
                Return to Upload
              </button>
            </div>
          </div>
        )}

        {/* 6-Stage Progress Stepper */}
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-3)" }}>
          {stages.map((st: JobStage, idx: number) => {
            const isDone = st.status === "done";
            const isRunning = st.status === "running";
            const isSkipped = st.status === "skipped";
            const isError = st.status === "error";

            let iconBg = "var(--color-surface)";
            let iconColor = "var(--color-text-muted)";
            let iconBorder = "var(--color-border)";
            let iconText = `${idx + 1}`;
            let textColor = "var(--color-text-muted)";

            if (isDone) {
              iconBg = "var(--color-mint-pale)";
              iconColor = "var(--color-primary)";
              iconBorder = "var(--color-mint)";
              iconText = "✓";
              textColor = "var(--color-text)";
            } else if (isRunning) {
              iconBg = "var(--color-mint-pale)";
              iconColor = "var(--color-primary)";
              iconBorder = "var(--color-primary)";
              iconText = "●";
              textColor = "var(--color-primary)";
            } else if (isSkipped) {
              iconText = "–";
              textColor = "var(--color-text-muted)";
            } else if (isError) {
              iconBg = "var(--color-amber-bg)";
              iconColor = "var(--color-amber-text)";
              iconBorder = "var(--color-amber-border)";
              iconText = "✕";
              textColor = "var(--color-amber-text)";
            }

            return (
              <div
                key={st.name}
                data-testid={`stage-${st.name}`}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "var(--spacing-2) var(--spacing-3)",
                  borderRadius: "var(--radius-control)",
                  backgroundColor: isRunning ? "var(--color-mint-pale)" : "transparent",
                  border: isRunning ? "1px solid var(--color-mint)" : "1px solid transparent",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-3)" }}>
                  <div
                    style={{
                      width: "24px",
                      height: "24px",
                      borderRadius: "50%",
                      backgroundColor: iconBg,
                      border: `1px solid ${iconBorder}`,
                      color: iconColor,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "var(--font-size-xs)",
                      fontWeight: "var(--font-weight-bold)",
                    }}
                  >
                    {iconText}
                  </div>
                  <span
                    style={{
                      fontSize: "var(--font-size-sm)",
                      fontWeight: isRunning ? "var(--font-weight-semibold)" : "var(--font-weight-normal)",
                      color: textColor,
                    }}
                  >
                    {STAGE_LABELS[st.name] || st.name}
                  </span>
                </div>

                <span
                  style={{
                    fontSize: "var(--font-size-xs)",
                    color: isRunning ? "var(--color-primary)" : "var(--color-text-muted)",
                    fontWeight: isRunning ? "var(--font-weight-semibold)" : "var(--font-weight-normal)",
                    textTransform: "capitalize",
                  }}
                >
                  {isRunning ? "In Progress..." : st.status}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
