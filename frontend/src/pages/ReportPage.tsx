import React, { useState } from "react";
import { useParams } from "react-router-dom";
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
  const report: Report = initialReport ?? demoReport;

  const tabs: { key: TabKey; label: string }[] = [
    { key: "overview", label: "Overview" },
    { key: "document", label: "Document View" },
    { key: "attribution", label: "Attribution (Experimental)" },
    { key: "citations", label: "Citations" },
    { key: "breakdown", label: "Detailed Breakdown" },
    { key: "limitations", label: "Limitations" },
  ];

  return (
    <div style={{ padding: "var(--spacing-8)", maxWidth: "1100px", margin: "0 auto" }}>
      {/* Header & Export Bar */}
      <div style={{ marginBottom: "var(--spacing-6)" }}>
        <h1 style={{ margin: "0 0 var(--spacing-2) 0", fontSize: "var(--font-size-2xl)" }}>
          Journal Transparency Report
        </h1>
        <p style={{ margin: "0 0 var(--spacing-4) 0", color: "var(--color-text-secondary)" }}>
          Decision support for editors, not an automated misconduct verdict.
        </p>
        <ExportBar report={report} jobId={jobId} />
      </div>

      {/* Tabs Navigation Bar */}
      <div
        style={{
          display: "flex",
          gap: "var(--spacing-2)",
          borderBottom: "1px solid var(--color-border)",
          marginBottom: "var(--spacing-6)",
        }}
      >
        {tabs.map((tab) => {
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              style={{
                padding: "var(--spacing-2) var(--spacing-4)",
                background: "none",
                border: "none",
                borderBottom: isActive ? "3px solid var(--color-primary)" : "3px solid transparent",
                fontWeight: isActive ? "var(--font-weight-semibold)" : "var(--font-weight-normal)",
                color: isActive ? "var(--color-primary)" : "var(--color-text-secondary)",
                cursor: "pointer",
                fontSize: "var(--font-size-sm)",
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
