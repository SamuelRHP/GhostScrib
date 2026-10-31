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

import styles from "./DevSandbox.module.css";

export default function DevSandbox(): React.ReactElement {
  const fixtureKeys = Object.keys(fixtures);
  const [selectedFixtureKey, setSelectedFixtureKey] = useState<string>(
    fixtureKeys[0] ?? ""
  );
  const [selectedTab, setSelectedTab] = useState<string>("document");

  const report: Report = fixtures[selectedFixtureKey] ?? fixtures[fixtureKeys[0]];

  const totalParas = report.assessment?.paragraphs_total ??
    report.document?.sections?.reduce((sum, s) => sum + (s.paragraphs?.length || 0), 0) ?? 0;
  const assessedParas = report.assessment?.paragraphs_assessed ??
    report.document?.sections?.reduce((sum, s) => sum + (s.paragraphs?.filter(p => p.label !== "not_assessed").length || 0), 0) ?? 0;

  return (
    <div className={styles.container}>
      <div className={styles.controlsCard}>
        <h2 className={styles.headerTitle}>Developer Sandbox (Member 3)</h2>
        <p className={styles.headerSubtitle}>
          Isolated fixture workbench to verify and debug report detail tabs without backend or detector dependencies.
        </p>

        {/* Controls */}
        <div className={styles.controlsRow}>
          <div className={styles.controlGroup}>
            <label htmlFor="fixture-select" className={styles.label}>
              Select Fixture
            </label>
            <select
              id="fixture-select"
              value={selectedFixtureKey}
              onChange={(e) => setSelectedFixtureKey(e.target.value)}
              className={styles.select}
            >
              {fixtureKeys.map((key) => (
                <option key={key} value={key}>
                  {key}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.controlGroup}>
            <label htmlFor="tab-select" className={styles.label}>
              Select View Tab
            </label>
            <select
              id="tab-select"
              value={selectedTab}
              onChange={(e) => setSelectedTab(e.target.value)}
              className={styles.select}
            >
              <option value="document">Document View</option>
              <option value="attribution">Attribution (Experimental)</option>
              <option value="citations">Citations</option>
              <option value="breakdown">Detailed Breakdown</option>
              <option value="limitations">Limitations</option>
              <option value="overview">Overview (Member 2)</option>
            </select>
          </div>
        </div>

        {/* Metadata Badge Strip */}
        <div className={styles.badgeRow}>
          <span className={`${styles.metaBadge} ${styles.syntheticBadge}`}>
            SYNTHETIC DEMO DATA
          </span>
          <span className={styles.metaBadge}>
            Band: {report.transparency_report?.document_band ?? "N/A"}
          </span>
          <span className={styles.metaBadge}>
            Words: {report.document?.n_words ?? 0}
          </span>
          <span className={styles.metaBadge}>
            Sections: {report.document?.sections?.length ?? 0}
          </span>
          <span className={styles.metaBadge}>
            Paragraphs: {assessedParas} assessed / {totalParas} total
          </span>
          {report.assessment?.insufficient_text && (
            <span className={styles.metaBadge} style={{ color: "var(--color-band-med-text)" }}>
              Insufficient Text
            </span>
          )}
        </div>
      </div>

      {/* Rendered Sandbox View */}
      <div className={styles.tabContentWrapper} role="region" aria-label="Tab Preview">
        {selectedTab === "document" && <DocumentViewTab report={report} />}
        {selectedTab === "attribution" && <AttributionTab report={report} />}
        {selectedTab === "citations" && <CitationsTab report={report} />}
        {selectedTab === "breakdown" && <BreakdownTab report={report} />}
        {selectedTab === "limitations" && <LimitationsTab report={report} />}
        {selectedTab === "overview" && <OverviewTab report={report} />}
      </div>
    </div>
  );
}
