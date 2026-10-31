import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import UploadZone from "@/features/upload/UploadZone";
import type { HealthResponse } from "@/types/api";

export default function HomePage(): React.ReactElement {
  const navigate = useNavigate();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [field, setField] = useState<"cs_eng" | "other">("cs_eng");
  const [disclosure, setDisclosure] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isHealthLoading, setIsHealthLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    fetch("/api/health")
      .then((res) => (res.ok ? res.json() : null))
      .then((data: HealthResponse | null) => {
        if (isMounted) {
          setHealth(data);
          setIsHealthLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setIsHealthLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setSubmitError(null);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setSubmitError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || isSubmitting) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("field", field);
      if (disclosure.trim()) {
        formData.append("disclosure", disclosure.trim());
      }

      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorJson = await response.json().catch(() => null);
        const errMsg = errorJson?.error?.message || `Server error (HTTP ${response.status})`;
        throw new Error(errMsg);
      }

      const data = await response.json();
      if (!data.job_id) {
        throw new Error("No job_id returned by server.");
      }

      navigate(`/analyzing/${data.job_id}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to submit manuscript for analysis.";
      setSubmitError(msg);
      setIsSubmitting(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div style={{ padding: "var(--spacing-8, 32px)", maxWidth: "800px", margin: "0 auto" }}>
      {/* Title & Description */}
      <div style={{ textAlign: "center", marginBottom: "var(--spacing-6, 24px)" }}>
        <h1
          style={{
            margin: "0 0 var(--spacing-2, 8px) 0",
            fontSize: "var(--font-size-2xl, 28px)",
            fontWeight: "var(--font-weight-bold, 700)",
            color: "var(--color-text-primary, #1e293b)",
            letterSpacing: "-0.5px",
          }}
        >
          GhostScrib: Manuscript Provenance Framework
        </h1>
        <p
          style={{
            margin: "0 0 var(--spacing-4, 16px) 0",
            color: "var(--color-text-secondary, #64748b)",
            fontSize: "var(--font-size-md, 16px)",
          }}
        >
          Decision support for editors and reviewers. Never an automated misconduct verdict.
        </p>

        {/* Detector Health Status Badge */}
        {!isHealthLoading && (
          <div style={{ display: "inline-flex", alignItems: "center", gap: "8px", fontSize: "13px" }}>
            <span
              style={{
                display: "inline-block",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                backgroundColor: health?.detector === "healthy" ? "#10b981" : "#f59e0b",
              }}
            />
            <span style={{ color: "var(--color-text-secondary, #64748b)" }}>
              {health?.detector === "healthy"
                ? "Primary detector service online"
                : "Primary detector offline (heuristic mode)"}
            </span>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit}>
        {/* Upload Zone Component */}
        <UploadZone
          onFileSelect={handleFileSelect}
          disabled={isSubmitting}
          disabledReason={isSubmitting ? "Analysis in progress..." : undefined}
        />

        {/* Selected File Card */}
        {selectedFile && (
          <div
            data-testid="selected-file-card"
            style={{
              marginTop: "var(--spacing-4, 16px)",
              padding: "var(--spacing-4, 16px)",
              backgroundColor: "var(--color-bg-card, #ffffff)",
              border: "1px solid var(--color-border, #e2e8f0)",
              borderRadius: "var(--radius-md, 8px)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <div
                style={{
                  width: "40px",
                  height: "40px",
                  borderRadius: "6px",
                  backgroundColor: "rgba(37, 99, 235, 0.1)",
                  color: "var(--color-primary, #2563eb)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: "bold",
                  fontSize: "12px",
                }}
              >
                {selectedFile.name.split(".").pop()?.toUpperCase() || "DOC"}
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: "14px", color: "var(--color-text-primary, #1e293b)" }}>
                  {selectedFile.name}
                </div>
                <div style={{ fontSize: "12px", color: "var(--color-text-secondary, #64748b)" }}>
                  {formatFileSize(selectedFile.size)}
                </div>
              </div>
            </div>

            <button
              type="button"
              data-testid="remove-file-btn"
              onClick={handleRemoveFile}
              disabled={isSubmitting}
              style={{
                background: "none",
                border: "1px solid var(--color-border, #cbd5e1)",
                borderRadius: "6px",
                padding: "6px 12px",
                fontSize: "12px",
                color: "var(--color-text-secondary, #64748b)",
                cursor: "pointer",
              }}
            >
              Change
            </button>
          </div>
        )}

        {/* Analysis Configuration */}
        <div
          style={{
            marginTop: "var(--spacing-6, 24px)",
            padding: "var(--spacing-5, 20px)",
            backgroundColor: "var(--color-bg-card, #ffffff)",
            border: "1px solid var(--color-border, #e2e8f0)",
            borderRadius: "var(--radius-lg, 12px)",
          }}
        >
          <div style={{ marginBottom: "var(--spacing-4, 16px)" }}>
            <label
              htmlFor="field-select"
              style={{
                display: "block",
                fontWeight: 600,
                fontSize: "14px",
                marginBottom: "6px",
                color: "var(--color-text-primary, #1e293b)",
              }}
            >
              Academic Discipline / Domain:
            </label>
            <select
              id="field-select"
              value={field}
              onChange={(e) => setField(e.target.value as "cs_eng" | "other")}
              disabled={isSubmitting}
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: "6px",
                border: "1px solid var(--color-border, #cbd5e1)",
                backgroundColor: "#ffffff",
                fontSize: "14px",
                color: "var(--color-text-primary, #1e293b)",
              }}
            >
              <option value="cs_eng">Computer Science &amp; Engineering (Model Calibrated Domain)</option>
              <option value="other">Other Academic Field (Confidence Adjustment Applied)</option>
            </select>
            <div style={{ fontSize: "12px", color: "var(--color-text-secondary, #64748b)", marginTop: "4px" }}>
              Primary detector ensemble was trained and calibrated on arXiv English CS &amp; engineering papers.
            </div>
          </div>

          <div>
            <label
              htmlFor="disclosure-input"
              style={{
                display: "block",
                fontWeight: 600,
                fontSize: "14px",
                marginBottom: "6px",
                color: "var(--color-text-primary, #1e293b)",
              }}
            >
              Author AI Disclosure Statement (Optional):
            </label>
            <textarea
              id="disclosure-input"
              value={disclosure}
              onChange={(e) => setDisclosure(e.target.value)}
              placeholder="e.g. 'The authors used ChatGPT exclusively for grammar editing and style proofreading...'"
              rows={3}
              disabled={isSubmitting}
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: "6px",
                border: "1px solid var(--color-border, #cbd5e1)",
                fontSize: "14px",
                fontFamily: "inherit",
                resize: "vertical",
                boxSizing: "border-box",
              }}
            />
          </div>
        </div>

        {/* Submission Error Banner */}
        {submitError && (
          <div
            role="alert"
            data-testid="submit-error"
            style={{
              marginTop: "var(--spacing-4, 16px)",
              padding: "12px 16px",
              backgroundColor: "rgba(220, 38, 38, 0.08)",
              border: "1px solid rgba(220, 38, 38, 0.3)",
              borderRadius: "8px",
              color: "#b91c1c",
              fontSize: "14px",
            }}
          >
            {submitError}
          </div>
        )}

        {/* Submit Button */}
        <div style={{ marginTop: "var(--spacing-6, 24px)", textAlign: "center" }}>
          <button
            type="submit"
            data-testid="upload-submit-button"
            disabled={!selectedFile || isSubmitting}
            style={{
              padding: "12px 32px",
              fontSize: "16px",
              fontWeight: 600,
              backgroundColor: !selectedFile || isSubmitting ? "#94a3b8" : "var(--color-primary, #2563eb)",
              color: "#ffffff",
              border: "none",
              borderRadius: "8px",
              cursor: !selectedFile || isSubmitting ? "not-allowed" : "pointer",
              transition: "background-color 0.2s",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            }}
          >
            {isSubmitting ? "Uploading & Initializing Analysis..." : "Start Forensic Analysis"}
          </button>
        </div>
      </form>
    </div>
  );
}
