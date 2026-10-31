import React, { useState } from "react";
import type { CitationItemStatus, ReferenceDetail, Report } from "@/types/report";

export default function CitationsTab({ report }: { report: Report }): React.ReactElement {
  const citations = report.citation_integrity;
  const references = citations.per_reference || [];
  const outOfRange = citations.out_of_range_intext_citations || [];

  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filteredReferences = references.filter((ref: ReferenceDetail) => {
    if (statusFilter === "all") return true;
    return ref.status === statusFilter;
  });

  const notCheckedRefs = references.filter((ref: ReferenceDetail) => ref.status === "not_checked");

  const getStatusBadge = (status: CitationItemStatus) => {
    switch (status) {
      case "verified":
        return {
          bg: "var(--color-band-low-bg)",
          text: "var(--color-band-low-text)",
          border: "var(--color-band-low-border)",
          label: "Verified",
        };
      case "partial":
        return {
          bg: "var(--color-band-med-bg)",
          text: "var(--color-band-med-text)",
          border: "var(--color-band-med-border)",
          label: "Partially Verified",
        };
      case "unverified":
        return {
          bg: "var(--color-band-high-bg)",
          text: "var(--color-band-high-text)",
          border: "var(--color-band-high-border)",
          label: "Could Not Be Verified",
        };
      case "not_checked":
      default:
        return {
          bg: "var(--color-band-neutral-bg)",
          text: "var(--color-band-neutral-text)",
          border: "var(--color-band-neutral-border)",
          label: "Not Checked",
        };
    }
  };

  return (
    <div
      style={{
        padding: "var(--spacing-6)",
        borderRadius: "var(--radius-lg)",
        backgroundColor: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
        display: "flex",
        flexDirection: "column",
        gap: "var(--spacing-6)",
      }}
    >
      {/* Header & Overview Banner */}
      <div>
        <h3 style={{ margin: "0 0 var(--spacing-2) 0", fontSize: "var(--font-size-xl)" }}>
          Bibliographic Citation Integrity
        </h3>
        <p style={{ color: "var(--color-text-secondary)", margin: "0 0 var(--spacing-4) 0", fontSize: "var(--font-size-sm)" }}>
          Automated reference verification against open scholarly databases (Crossref). Unverified status indicates
          that the citation could not be verified; this may stem from a database coverage gap, volume/page discrepancies,
          or preprint status rather than an invalid entry.
        </p>
      </div>

      {/* KPI Metrics Strip */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
          gap: "var(--spacing-3)",
        }}
        data-testid="citations-summary-grid"
      >
        <div
          style={{
            padding: "var(--spacing-3) var(--spacing-4)",
            backgroundColor: "var(--color-bg-card-muted)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-md)",
          }}
        >
          <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)" }}>
            Total References
          </div>
          <div style={{ fontSize: "var(--font-size-2xl)", fontWeight: "var(--font-weight-bold)", color: "var(--color-text-primary)" }}>
            {citations.total}
          </div>
        </div>

        <div
          style={{
            padding: "var(--spacing-3) var(--spacing-4)",
            backgroundColor: "var(--color-band-low-bg)",
            border: "1px solid var(--color-band-low-border)",
            borderRadius: "var(--radius-md)",
          }}
        >
          <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-band-low-text)", fontWeight: "var(--font-weight-medium)" }}>
            Verified in Crossref
          </div>
          <div style={{ fontSize: "var(--font-size-2xl)", fontWeight: "var(--font-weight-bold)", color: "var(--color-band-low-text)" }}>
            {citations.verified}
          </div>
        </div>

        <div
          style={{
            padding: "var(--spacing-3) var(--spacing-4)",
            backgroundColor: "var(--color-band-med-bg)",
            border: "1px solid var(--color-band-med-border)",
            borderRadius: "var(--radius-md)",
          }}
        >
          <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-band-med-text)", fontWeight: "var(--font-weight-medium)" }}>
            Partially Matched
          </div>
          <div style={{ fontSize: "var(--font-size-2xl)", fontWeight: "var(--font-weight-bold)", color: "var(--color-band-med-text)" }}>
            {citations.partial}
          </div>
        </div>

        <div
          style={{
            padding: "var(--spacing-3) var(--spacing-4)",
            backgroundColor: "var(--color-band-high-bg)",
            border: "1px solid var(--color-band-high-border)",
            borderRadius: "var(--radius-md)",
          }}
        >
          <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-band-high-text)", fontWeight: "var(--font-weight-medium)" }}>
            Could Not Be Verified
          </div>
          <div style={{ fontSize: "var(--font-size-2xl)", fontWeight: "var(--font-weight-bold)", color: "var(--color-band-high-text)" }}>
            {citations.unverified}
          </div>
        </div>

        <div
          style={{
            padding: "var(--spacing-3) var(--spacing-4)",
            backgroundColor: "var(--color-band-neutral-bg)",
            border: "1px solid var(--color-band-neutral-border)",
            borderRadius: "var(--radius-md)",
          }}
        >
          <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-band-neutral-text)", fontWeight: "var(--font-weight-medium)" }}>
            Not Checked (Offline/Web)
          </div>
          <div style={{ fontSize: "var(--font-size-2xl)", fontWeight: "var(--font-weight-bold)", color: "var(--color-band-neutral-text)" }}>
            {citations.not_checked}
          </div>
        </div>
      </div>

      {/* Out-of-Range In-Text Citations Alert */}
      {outOfRange.length > 0 && (
        <div
          data-testid="out-of-range-alert"
          style={{
            padding: "var(--spacing-3) var(--spacing-4)",
            backgroundColor: "var(--color-band-high-bg)",
            border: "1px solid var(--color-band-high-border)",
            borderRadius: "var(--radius-md)",
            color: "var(--color-band-high-text)",
            fontSize: "var(--font-size-sm)",
          }}
        >
          <div style={{ fontWeight: "var(--font-weight-bold)", marginBottom: "var(--spacing-1)" }}>
            Discrepancy: Out-of-Range In-Text Citations Detected
          </div>
          <div>
            The body text references numbers that do not correspond to any listed entry in the bibliography:{" "}
            <strong>{outOfRange.map((n) => `[${n}]`).join(", ")}</strong> (Total bibliography entries: {citations.total}).
          </div>
        </div>
      )}

      {/* Filter Toolbar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "var(--spacing-3)",
          borderBottom: "1px solid var(--color-border)",
          paddingBottom: "var(--spacing-3)",
        }}
      >
        <div style={{ fontSize: "var(--font-size-sm)", fontWeight: "var(--font-weight-semibold)", color: "var(--color-text-primary)" }}>
          Reference Verification Records ({filteredReferences.length} of {references.length})
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-2)" }}>
          <label htmlFor="citation-status-filter" style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)" }}>
            Filter Status:
          </label>
          <select
            id="citation-status-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            data-testid="citation-status-filter"
            style={{
              padding: "var(--spacing-1) var(--spacing-3)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-border)",
              backgroundColor: "var(--color-bg-card)",
              color: "var(--color-text-primary)",
              fontSize: "var(--font-size-xs)",
            }}
          >
            <option value="all">All Statuses ({references.length})</option>
            <option value="verified">Verified ({citations.verified})</option>
            <option value="partial">Partially Verified ({citations.partial})</option>
            <option value="unverified">Could Not Be Verified ({citations.unverified})</option>
            <option value="not_checked">Not Checked ({citations.not_checked})</option>
          </select>
        </div>
      </div>

      {/* References Table */}
      <div style={{ overflowX: "auto" }}>
        <table
          data-testid="citations-table"
          style={{
            width: "100%",
            borderCollapse: "collapse",
            fontSize: "var(--font-size-sm)",
          }}
        >
          <thead>
            <tr style={{ borderBottom: "2px solid var(--color-border)", textAlign: "left", color: "var(--color-text-secondary)" }}>
              <th style={{ padding: "var(--spacing-3)", width: "60px" }}>#</th>
              <th style={{ padding: "var(--spacing-3)", width: "160px" }}>Verification Status</th>
              <th style={{ padding: "var(--spacing-3)" }}>Raw Citation / Matched Record</th>
              <th style={{ padding: "var(--spacing-3)", width: "120px", textAlign: "right" }}>Similarity</th>
              <th style={{ padding: "var(--spacing-3)", width: "120px", textAlign: "center" }}>DOI Link</th>
            </tr>
          </thead>
          <tbody>
            {filteredReferences.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ padding: "var(--spacing-6)", textAlign: "center", color: "var(--color-text-muted)" }}>
                  No citations match the selected filter.
                </td>
              </tr>
            ) : (
              filteredReferences.map((ref: ReferenceDetail, idx: number) => {
                const badge = getStatusBadge(ref.status);
                const similarityScore = Math.round((ref.similarity || 0) * 100);
                return (
                  <tr
                    key={idx}
                    style={{
                      borderBottom: "1px solid var(--color-border)",
                    }}
                  >
                    <td style={{ padding: "var(--spacing-3)", color: "var(--color-text-muted)", verticalAlign: "top" }}>
                      [{idx + 1}]
                    </td>
                    <td style={{ padding: "var(--spacing-3)", verticalAlign: "top" }}>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "2px 8px",
                          borderRadius: "var(--radius-sm)",
                          backgroundColor: badge.bg,
                          color: badge.text,
                          border: `1px solid ${badge.border}`,
                          fontSize: "var(--font-size-xs)",
                          fontWeight: "var(--font-weight-medium)",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {badge.label}
                      </span>
                    </td>
                    <td style={{ padding: "var(--spacing-3)", verticalAlign: "top" }}>
                      <div style={{ color: "var(--color-text-primary)", marginBottom: "var(--spacing-1)" }}>
                        {ref.raw}
                      </div>
                      {ref.matched_title && (
                        <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)" }}>
                          <strong>Matched Title:</strong> {ref.matched_title}
                        </div>
                      )}
                      {ref.reason && (
                        <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)", fontStyle: "italic", marginTop: "2px" }}>
                          Note: {ref.reason}
                        </div>
                      )}
                    </td>
                    <td style={{ padding: "var(--spacing-3)", textAlign: "right", verticalAlign: "top" }}>
                      <span style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)" }}>
                        Match: {similarityScore}%
                      </span>
                    </td>
                    <td style={{ padding: "var(--spacing-3)", textAlign: "center", verticalAlign: "top" }}>
                      {ref.matched_doi ? (
                        <a
                          href={`https://doi.org/${encodeURIComponent(ref.matched_doi)}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            display: "inline-block",
                            padding: "2px 8px",
                            borderRadius: "var(--radius-sm)",
                            backgroundColor: "var(--color-primary-bg)",
                            color: "var(--color-primary)",
                            fontSize: "var(--font-size-xs)",
                            textDecoration: "none",
                            fontWeight: "var(--font-weight-medium)",
                          }}
                        >
                          View DOI
                        </a>
                      ) : (
                        <span style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)" }}>
                          —
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Not Checked Section Details */}
      {notCheckedRefs.length > 0 && (
        <div
          data-testid="not-checked-summary"
          style={{
            padding: "var(--spacing-4)",
            backgroundColor: "var(--color-band-neutral-bg)",
            border: "1px solid var(--color-band-neutral-border)",
            borderRadius: "var(--radius-md)",
            fontSize: "var(--font-size-xs)",
            color: "var(--color-band-neutral-text)",
          }}
        >
          <div style={{ fontWeight: "var(--font-weight-bold)", marginBottom: "var(--spacing-1)" }}>
            Non-Indexed / Offline Resources ({notCheckedRefs.length} items)
          </div>
          <div>
            These references were recognized as textbooks, URL/web resources, or dataset repositories not indexed in
            Crossref's journal DOI corpus, and were set to <strong>Not Checked</strong> rather than unverified.
          </div>
        </div>
      )}

      {/* Privacy Notice */}
      <div
        style={{
          padding: "var(--spacing-3) var(--spacing-4)",
          backgroundColor: "var(--color-bg-card-muted)",
          border: "1px solid var(--color-border)",
          borderRadius: "var(--radius-md)",
          fontSize: "var(--font-size-xs)",
          color: "var(--color-text-muted)",
          display: "flex",
          alignItems: "center",
          gap: "var(--spacing-2)",
        }}
      >
        <span style={{ fontWeight: "var(--font-weight-semibold)", color: "var(--color-text-secondary)" }}>
          Privacy Note:
        </span>
        <span>
          Only raw bibliographic reference strings are transmitted to external metadata index APIs (Crossref/OpenAlex).
          Manuscript text, authorship data, and proprietary prose are never shared with external services.
        </span>
      </div>
    </div>
  );
}
