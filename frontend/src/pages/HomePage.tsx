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

  const isHealthy = health?.detector === "healthy";

  return (
    <div style={{ padding: "var(--spacing-8) var(--spacing-4)", maxWidth: "840px", margin: "0 auto" }}>
      {/* Title & Description */}
      <div style={{ textAlign: "center", marginBottom: "var(--spacing-8)" }}>
        <h1
          style={{
            margin: "0 0 var(--spacing-2) 0",
            fontSize: "var(--font-size-3xl)",
            fontWeight: "var(--font-weight-bold)",
            color: "var(--color-text)",
            letterSpacing: "-0.5px",
          }}
        >
          GhostScrib: Manuscript Provenance Framework
        </h1>
        <p
          style={{
            margin: "0 0 var(--spacing-4) 0",
            color: "var(--color-text-muted)",
            fontSize: "var(--font-size-base)",
          }}
        >
          Decision support for editors and reviewers. Never an automated misconduct verdict.
        </p>

        {/* Detector Health Status Badge */}
        {!isHealthLoading && (
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "var(--spacing-2)",
              padding: "var(--spacing-1) var(--spacing-3)",
              borderRadius: "var(--radius-pill)",
              backgroundColor: isHealthy ? "var(--color-mint-pale)" : "var(--color-amber-bg)",
              color: isHealthy ? "var(--color-primary)" : "var(--color-amber-text)",
              border: `1px solid ${isHealthy ? "var(--color-mint)" : "var(--color-amber-border)"}`,
              fontSize: "var(--font-size-xs)",
              fontWeight: "var(--font-weight-medium)",
            }}
          >
            <span
              style={{
                display: "inline-block",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                backgroundColor: isHealthy ? "var(--color-primary)" : "var(--color-amber-text)",
              }}
            />
            <span>
              {isHealthy
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
              marginTop: "var(--spacing-4)",
              padding: "var(--spacing-4)",
              backgroundColor: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-card)",
              boxShadow: "var(--shadow-card)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-3)" }}>
              <div
                style={{
                  width: "40px",
                  height: "40px",
                  borderRadius: "var(--radius-control)",
                  backgroundColor: "var(--color-mint-pale)",
                  color: "var(--color-primary)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: "var(--font-weight-bold)",
                  fontSize: "var(--font-size-xs)",
                }}
              >
                {selectedFile.name.split(".").pop()?.toUpperCase() || "DOC"}
              </div>
              <div>
                <div style={{ fontWeight: "var(--font-weight-semibold)", fontSize: "var(--font-size-sm)", color: "var(--color-text)" }}>
                  {selectedFile.name}
                </div>
                <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)" }}>
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
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-control)",
                padding: "var(--spacing-1) var(--spacing-3)",
                fontSize: "var(--font-size-xs)",
                color: "var(--color-text-muted)",
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
            marginTop: "var(--spacing-6)",
            padding: "var(--spacing-6)",
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-card)",
            boxShadow: "var(--shadow-card)",
          }}
        >
          <div style={{ marginBottom: "var(--spacing-5)" }}>
            <label
              htmlFor="field-select"
              style={{
                display: "block",
                fontWeight: "var(--font-weight-semibold)",
                fontSize: "var(--font-size-sm)",
                marginBottom: "var(--spacing-2)",
                color: "var(--color-text)",
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
                padding: "var(--spacing-2) var(--spacing-3)",
                borderRadius: "var(--radius-control)",
                border: "1px solid var(--color-border)",
                backgroundColor: "var(--color-bg-card)",
                fontSize: "var(--font-size-sm)",
                color: "var(--color-text)",
              }}
            >
              <option value="cs_eng">Computer Science &amp; Engineering (Model Calibrated Domain)</option>
              <option value="other">Other Academic Field (Confidence Adjustment Applied)</option>
            </select>
            <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)", marginTop: "var(--spacing-1)" }}>
              Primary detector ensemble was trained and calibrated on arXiv English CS &amp; engineering papers.
            </div>
          </div>

          <div>
            <label
              htmlFor="disclosure-input"
              style={{
                display: "block",
                fontWeight: "var(--font-weight-semibold)",
                fontSize: "var(--font-size-sm)",
                marginBottom: "var(--spacing-2)",
                color: "var(--color-text)",
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
                padding: "var(--spacing-2) var(--spacing-3)",
                borderRadius: "var(--radius-control)",
                border: "1px solid var(--color-border)",
                backgroundColor: "var(--color-bg-card)",
                fontSize: "var(--font-size-sm)",
                color: "var(--color-text)",
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
              marginTop: "var(--spacing-4)",
              padding: "var(--spacing-3) var(--spacing-4)",
              backgroundColor: "var(--color-amber-bg)",
              border: "1px solid var(--color-amber-border)",
              borderRadius: "var(--radius-control)",
              color: "var(--color-amber-text)",
              fontSize: "var(--font-size-sm)",
            }}
          >
            {submitError}
          </div>
        )}

        {/* Submit Button */}
        <div style={{ marginTop: "var(--spacing-6)", textAlign: "center" }}>
          <button
            type="submit"
            data-testid="upload-submit-button"
            disabled={!selectedFile || isSubmitting}
            style={{
              padding: "var(--spacing-3) var(--spacing-8)",
              fontSize: "var(--font-size-base)",
              fontWeight: "var(--font-weight-semibold)",
              backgroundColor: !selectedFile || isSubmitting ? "var(--color-surface)" : "var(--color-primary)",
              color: !selectedFile || isSubmitting ? "var(--color-text-muted)" : "var(--color-text-on-dark)",
              border: `1px solid ${!selectedFile || isSubmitting ? "var(--color-border)" : "var(--color-primary)"}`,
              borderRadius: "var(--radius-control)",
              cursor: !selectedFile || isSubmitting ? "not-allowed" : "pointer",
              transition: "background-color 0.2s",
              boxShadow: "var(--shadow-card)",
            }}
          >
            {isSubmitting ? "Uploading & Initializing Analysis..." : "Start Forensic Analysis"}
          </button>
        </div>
      </form>
    </div>
  );
}
