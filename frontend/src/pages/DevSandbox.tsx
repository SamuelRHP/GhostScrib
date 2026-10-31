import React, { useState } from "react";
import { fixtures } from "@/mocks/fixtures";
import type { Report } from "@/types/report";

// All 6 tabs available for sandbox preview
import OverviewTab from "@/features/report/OverviewTab";
import DocumentViewTab from "@/features/report/tabs/DocumentViewTab";
import AttributionTab from "@/features/report/tabs/AttributionTab";
import CitationsTab from "@/features/report/tabs/CitationsTab";
import BreakdownTab from "@/features/report/tabs/BreakdownTab";
import LimitationsTab from "@/features/report/tabs/LimitationsTab";

export default function DevSandbox(): React.ReactElement {
  const fixtureKeys = Object.keys(fixtures);
  const [selectedFixtureKey, setSelectedFixtureKey] = useState<string>(
    fixtureKeys[0] ?? ""
  );
  const [selectedTab, setSelectedTab] = useState<string>("overview");

  const report: Report = fixtures[selectedFixtureKey] ?? fixtures[fixtureKeys[0]];

  return (
    <div style={{ padding: "var(--spacing-8)", maxWidth: "1100px", margin: "0 auto" }}>
      <div
        style={{
          padding: "var(--spacing-4)",
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          borderRadius: "var(--radius-lg)",
          marginBottom: "var(--spacing-6)",
        }}
      >
        <h2 style={{ margin: "0 0 var(--spacing-3) 0", fontSize: "var(--font-size-xl)" }}>
          Developer Sandbox (Member 3)
        </h2>
        <p style={{ margin: "0 0 var(--spacing-4) 0", color: "var(--color-text-secondary)", fontSize: "var(--font-size-sm)" }}>
          Render and debug report tabs in isolation against mock fixtures.
        </p>

        {/* Controls */}
        <div style={{ display: "flex", gap: "var(--spacing-4)", flexWrap: "wrap", alignItems: "center" }}>
          <label style={{ fontSize: "var(--font-size-sm)", fontWeight: "var(--font-weight-medium)" }}>
            Fixture:
            <select
              value={selectedFixtureKey}
              onChange={(e) => setSelectedFixtureKey(e.target.value)}
              style={{
                marginLeft: "var(--spacing-2)",
                padding: "var(--spacing-1) var(--spacing-2)",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--color-border)",
              }}
            >
              {fixtureKeys.map((key) => (
                <option key={key} value={key}>
                  {key}
                </option>
              ))}
            </select>
          </label>

          <label style={{ fontSize: "var(--font-size-sm)", fontWeight: "var(--font-weight-medium)" }}>
            Tab:
            <select
              value={selectedTab}
              onChange={(e) => setSelectedTab(e.target.value)}
              style={{
                marginLeft: "var(--spacing-2)",
                padding: "var(--spacing-1) var(--spacing-2)",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--color-border)",
              }}
            >
              <option value="overview">Overview</option>
              <option value="document">Document View</option>
              <option value="attribution">Attribution</option>
              <option value="citations">Citations</option>
              <option value="breakdown">Breakdown</option>
              <option value="limitations">Limitations</option>
            </select>
          </label>
        </div>
      </div>

      {/* Rendered Sandbox View */}
      <div>
        {selectedTab === "overview" && <OverviewTab report={report} />}
        {selectedTab === "document" && <DocumentViewTab report={report} />}
        {selectedTab === "attribution" && <AttributionTab report={report} />}
        {selectedTab === "citations" && <CitationsTab report={report} />}
        {selectedTab === "breakdown" && <BreakdownTab report={report} />}
        {selectedTab === "limitations" && <LimitationsTab report={report} />}
      </div>
    </div>
  );
}
