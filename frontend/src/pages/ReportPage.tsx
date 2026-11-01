import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import type { Report } from "@/types/report";
import { demoReport } from "@/mocks/demoReport";

// Member 2 Components
import OverviewTab from "@/features/report/OverviewTab";
import ExportBar from "@/features/report/ExportBar";

// Member 3 Tabs (strictly ordered per contract)
import DocumentViewTab from "@/features/report/tabs/DocumentViewTab";
import AttributionTab from "@/features/report/tabs/AttributionTab";
import CitationsTab from "@/features/report/tabs/CitationsTab";
import BreakdownTab from "@/features/report/tabs/BreakdownTab";
import LimitationsTab from "@/features/report/tabs/LimitationsTab";

type TabKey = "overview" | "document" | "attribution" | "citations" | "breakdown" | "limitations";

export default function ReportPage({ initialReport }: { initialReport?: Report }): React.ReactElement {
  const { jobId } = useParams<{ jobId: string }>();
  const [activeTab, setActiveTab] = useState<TabKey>("overview");
  const [report, setReport] = useState<Report | null>(
    initialReport ?? (jobId === "demo" || !jobId ? demoReport : null)
  );
  const [isLoading, setIsLoading] = useState<boolean>(!initialReport && !!jobId && jobId !== "demo");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialReport) {
      setReport(initialReport);
      setIsLoading(false);
      return;
    }
    if (!jobId || jobId === "demo") {
      setReport(demoReport);
      setIsLoading(false);
      return;
    }

    let isMounted = true;
    setIsLoading(true);
    setError(null);

    fetch(`/api/jobs/${jobId}/report`)
      .then(async (res) => {
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData?.error?.message || `Failed to fetch report (HTTP ${res.status})`);
        }
        return res.json();
      })
      .then((data: Report) => {
        if (isMounted) {
          setReport(data);
          setIsLoading(false);
        }
      })
      .catch((err: Error) => {
        if (isMounted) {
          setError(err.message);
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [jobId, initialReport]);

  const tabs: { key: TabKey; label: string }[] = [
    { key: "overview", label: "Overview" },
    { key: "document", label: "Document View" },
    { key: "attribution", label: "Attribution (Experimental)" },
    { key: "citations", label: "Citations" },
    { key: "breakdown", label: "Detailed Breakdown" },
    { key: "limitations", label: "Limitations" },
  ];

  if (isLoading) {
    return (
      <div
        style={{
          padding: "var(--spacing-12) var(--spacing-6)",
          maxWidth: "800px",
          margin: "0 auto",
          textAlign: "center",
        }}
      >
        <div
          style={{
            width: "48px",
            height: "48px",
            border: "4px solid var(--color-border)",
            borderTopColor: "var(--color-primary)",
            borderRadius: "50%",
            margin: "0 auto var(--spacing-4) auto",
            animation: "spin 1s linear infinite",
          }}
        />
        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
        <h2 style={{ fontSize: "var(--font-size-xl)", margin: "0 0 var(--spacing-2) 0", color: "var(--color-text)" }}>
          Loading Analysis Report...
        </h2>
        <p style={{ color: "var(--color-text-muted)", margin: 0 }}>
          Retrieving complete provenance data for Job <code>{jobId}</code>
        </p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div
        style={{
          padding: "var(--spacing-12) var(--spacing-6)",
          maxWidth: "800px",
          margin: "0 auto",
          textAlign: "center",
        }}
      >
        <div
          style={{
            padding: "var(--spacing-6)",
            backgroundColor: "var(--color-amber-bg)",
            border: "1px solid var(--color-amber-border)",
            borderRadius: "var(--radius-card)",
            marginBottom: "var(--spacing-6)",
          }}
        >
          <h2
            style={{
              fontSize: "var(--font-size-xl)",
              color: "var(--color-amber-text)",
              margin: "0 0 var(--spacing-2) 0",
            }}
          >
            Unable to Load Report
          </h2>
          <p style={{ color: "var(--color-amber-text)", margin: 0 }}>
            {error || "Report not found or incomplete."}
          </p>
        </div>
        <div style={{ display: "flex", gap: "var(--spacing-3)", justifyContent: "center" }}>
          {jobId && jobId !== "demo" && (
            <Link
              to={`/analyzing/${jobId}`}
              style={{
                padding: "var(--spacing-2) var(--spacing-4)",
                backgroundColor: "var(--color-bg-card)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-control)",
                color: "var(--color-text)",
                textDecoration: "none",
                fontSize: "var(--font-size-sm)",
              }}
            >
              Check Job Status
            </Link>
          )}
          <Link
            to="/"
            style={{
              padding: "var(--spacing-2) var(--spacing-4)",
              backgroundColor: "var(--color-primary)",
              color: "var(--color-text-on-dark)",
              borderRadius: "var(--radius-control)",
              textDecoration: "none",
              fontSize: "var(--font-size-sm)",
            }}
          >
            Upload Another File
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: "var(--spacing-8) var(--spacing-6)", maxWidth: "var(--container-max)", margin: "0 auto" }}>
      {/* Header & Export Bar */}
      <div style={{ marginBottom: "var(--spacing-6)" }}>
        <div
          style={{
            padding: "var(--spacing-5) var(--spacing-6)",
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-card)",
            boxShadow: "var(--shadow-card)",
            marginBottom: "var(--spacing-4)",
          }}
        >
          <h1 style={{ margin: "0 0 var(--spacing-1) 0", fontSize: "var(--font-size-2xl)", color: "var(--color-text)" }}>
            Journal Transparency Report
          </h1>
          <p style={{ margin: 0, color: "var(--color-text-muted)", fontSize: "var(--font-size-sm)" }}>
            Decision support for editors, not an automated misconduct verdict.
          </p>
        </div>
        <ExportBar report={report} jobId={jobId} />
      </div>

      {/* Tabs Navigation Bar */}
      <div
        style={{
          display: "flex",
          gap: "var(--spacing-2)",
          borderBottom: "1px solid var(--color-border)",
          marginBottom: "var(--spacing-6)",
          overflowX: "auto",
        }}
      >
        {tabs.map((tab) => {
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              role="tab"
              aria-selected={isActive}
              onClick={() => setActiveTab(tab.key)}
              style={{
                padding: "var(--spacing-2) var(--spacing-4)",
                background: "none",
                border: "none",
                borderBottom: isActive ? "3px solid var(--color-primary)" : "3px solid transparent",
                fontWeight: isActive ? "var(--font-weight-semibold)" : "var(--font-weight-normal)",
                color: isActive ? "var(--color-primary)" : "var(--color-text-muted)",
                cursor: "pointer",
                fontSize: "var(--font-size-sm)",
                whiteSpace: "nowrap",
                transition: "color 0.15s, border-color 0.15s",
              }}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Active Tab Panel */}
      <div>
        {activeTab === "overview" && <OverviewTab report={report} />}
        {activeTab === "document" && <DocumentViewTab report={report} />}
        {activeTab === "attribution" && <AttributionTab report={report} />}
        {activeTab === "citations" && <CitationsTab report={report} />}
        {activeTab === "breakdown" && <BreakdownTab report={report} />}
        {activeTab === "limitations" && <LimitationsTab report={report} />}
      </div>
    </div>
  );
}
