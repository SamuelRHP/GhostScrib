import React, { useState, useMemo, memo } from "react";
import type { Report, Section, Paragraph, SentenceScore, SectionBand } from "@/types/report";
import {
  ChevronDown,
  ChevronRight,
  AlertTriangle,
  Filter,
  CheckCircle2,
  HelpCircle,
} from "lucide-react";
import styles from "./DocumentViewTab.module.css";

// Band helper returning text label and style class
function getBandMeta(band: SectionBand | undefined): { label: string; className: string } {
  switch (band) {
    case "high":
      return { label: "High AI Resemblance", className: styles.bandHigh };
    case "medium":
      return { label: "Medium AI Resemblance", className: styles.bandMed };
    case "low":
      return { label: "Low AI Resemblance", className: styles.bandLow };
    case "not_assessed":
    default:
      return { label: "Not Assessed", className: styles.bandNeutral };
  }
}

// Paragraph label helper
function getParagraphLabelMeta(label: Paragraph["label"]): {
  text: string;
  className: string;
  badgeClassName: string;
} {
  switch (label) {
    case "ai":
      return {
        text: "AI-like",
        className: styles.paragraphAi,
        badgeClassName: styles.bandHigh,
      };
    case "uncertain":
      return {
        text: "Uncertain",
        className: styles.paragraphUncertain,
        badgeClassName: styles.bandMed,
      };
    case "human":
      return {
        text: "Human-like",
        className: styles.paragraphHuman,
        badgeClassName: styles.bandLow,
      };
    case "not_assessed":
    default:
      return {
        text: "Not Assessed",
        className: styles.paragraphNotAssessed,
        badgeClassName: styles.bandNeutral,
      };
  }
}

// Render sentence highlights with keyboard and hover accessibility
function SentenceHighlightedText({
  sentences,
  fallbackText,
}: {
  sentences?: SentenceScore[];
  fallbackText: string;
}): React.ReactElement {
  if (!sentences || sentences.length === 0) {
    return <span className={styles.paragraphText}>{fallbackText}</span>;
  }

  return (
    <span className={styles.paragraphText}>
      {sentences.map((s, idx) => {
        let highlightClass = styles.sentenceNeutral;
        let scoreLabel = "";

        if (typeof s.score === "number") {
          scoreLabel = `Sentence likelihood score: ${s.score > 0 ? "+" : ""}${s.score.toFixed(2)}`;
          if (s.score >= 1.0) {
            highlightClass = styles.sentenceHighlightHigh;
          } else if (s.score >= 0.3) {
            highlightClass = styles.sentenceHighlightMed;
          }
        }

        if (highlightClass !== styles.sentenceNeutral) {
          return (
            <span
              key={idx}
              className={highlightClass}
              title={scoreLabel}
              tabIndex={0}
              role="mark"
              aria-label={scoreLabel}
            >
              {s.text}{" "}
            </span>
          );
        }

        return <span key={idx}>{s.text} </span>;
      })}
    </span>
  );
}

// Memoized Paragraph Card
const ParagraphCard = memo(function ParagraphCard({
  paragraph,
  index,
}: {
  paragraph: Paragraph;
  index: number;
}): React.ReactElement {
  const meta = getParagraphLabelMeta(paragraph.label);
  const isAiOrUncertain = paragraph.label === "ai" || paragraph.label === "uncertain";

  return (
    <article
      className={`${styles.paragraphCard} ${meta.className}`}
      aria-label={`Paragraph ${index + 1}, classified as ${meta.text}`}
    >
      <div className={styles.paragraphHeader}>
        <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-2)" }}>
          <span className={`${styles.paragraphLabelBadge} ${meta.badgeClassName}`}>
            {paragraph.label === "human" && <CheckCircle2 size={13} aria-hidden="true" />}
            {paragraph.label === "ai" && <AlertTriangle size={13} aria-hidden="true" />}
            {paragraph.label === "uncertain" && <HelpCircle size={13} aria-hidden="true" />}
            {meta.text}
          </span>
          {typeof paragraph.score === "number" && (
            <span className={styles.paragraphMeta}>
              Score: {paragraph.score > 0 ? "+" : ""}{paragraph.score.toFixed(2)}
            </span>
          )}
        </div>

        <div className={styles.paragraphMeta}>
          <span>{paragraph.words} words</span>
          {paragraph.label === "not_assessed" && (
            <span className={styles.skippedReason} data-testid="paragraph-skip-reason">
              (Excluded: {paragraph.reason || "under 40 words or non-prose structure"})
            </span>
          )}
        </div>
      </div>

      {isAiOrUncertain ? (
        <SentenceHighlightedText
          sentences={paragraph.sentences}
          fallbackText={paragraph.text}
        />
      ) : (
        <p className={styles.paragraphText}>{paragraph.text}</p>
      )}
    </article>
  );
});

// Memoized Section Panel (Lazy rendering when collapsed for 300+ paragraphs performance)
const SectionPanel = memo(function SectionPanel({
  section,
  isOpen,
  onToggle,
  showFlaggedOnly,
}: {
  section: Section;
  isOpen: boolean;
  onToggle: () => void;
  showFlaggedOnly: boolean;
}): React.ReactElement {
  const bandMeta = getBandMeta(section.band);

  const displayedParagraphs = useMemo(() => {
    if (!section.paragraphs) return [];
    if (!showFlaggedOnly) return section.paragraphs;
    return section.paragraphs.filter(
      (p) => p.label === "ai" || p.label === "uncertain"
    );
  }, [section.paragraphs, showFlaggedOnly]);

  const stats = section.stats;

  return (
    <section className={styles.sectionCard}>
      <button
        type="button"
        className={`${styles.sectionHeader} ${isOpen ? styles.sectionHeaderOpen : ""}`}
        onClick={onToggle}
        aria-expanded={isOpen}
      >
        <div className={styles.sectionTitleRow}>
          <span className={styles.sectionChevron} aria-hidden="true">
            {isOpen ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
          </span>
          <h4 className={styles.sectionName}>{section.name}</h4>
        </div>

        <div className={styles.sectionMetaGroup}>
          <span className={`${styles.bandBadge} ${bandMeta.className}`}>
            {bandMeta.label}
          </span>

          {stats && (
            <>
              <span className={styles.statPill}>
                {stats.assessed_words ?? 0} assessed words
              </span>
              <span className={styles.statPill}>
                {stats.n_ai ?? 0} AI / {stats.n_uncertain ?? 0} uncertain
              </span>
            </>
          )}
        </div>
      </button>

      {section.notes && isOpen && (
        <div className={styles.sectionNotes}>
          <strong>Editorial Note:</strong> {section.notes}
        </div>
      )}

      {/* Lazy render paragraphs: do not mount DOM nodes when collapsed */}
      {isOpen && (
        <div className={styles.sectionBody}>
          {displayedParagraphs.length > 0 ? (
            displayedParagraphs.map((p, idx) => (
              <ParagraphCard key={idx} paragraph={p} index={idx} />
            ))
          ) : (
            <div className={styles.emptyFilterNote}>
              {showFlaggedOnly
                ? "No flagged paragraphs in this section matching active filter."
                : "No paragraphs recorded in this section."}
            </div>
          )}
        </div>
      )}
    </section>
  );
});

export default function DocumentViewTab({ report }: { report: Report }): React.ReactElement {
  const sections = useMemo(() => report.document?.sections ?? [], [report.document?.sections]);

  // Expand state: default to all open (up to 5 sections), or first 3 if large
  const [openSectionIndices, setOpenSectionIndices] = useState<Set<number>>(() => {
    const initial = new Set<number>();
    const countToOpen = Math.min(sections.length, 5);
    for (let i = 0; i < countToOpen; i++) {
      initial.add(i);
    }
    return initial;
  });

  const [showFlaggedOnly, setShowFlaggedOnly] = useState<boolean>(false);

  // Toggle individual section
  const toggleSection = (idx: number) => {
    setOpenSectionIndices((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) {
        next.delete(idx);
      } else {
        next.add(idx);
      }
      return next;
    });
  };

  const expandAll = () => {
    const all = new Set<number>();
    sections.forEach((_, idx) => all.add(idx));
    setOpenSectionIndices(all);
  };

  const collapseAll = () => {
    setOpenSectionIndices(new Set());
  };

  // Assessment summary stats
  const totalParagraphs = report.assessment?.paragraphs_total ??
    sections.reduce((sum, s) => sum + (s.paragraphs?.length ?? 0), 0);

  const assessedParagraphs = report.assessment?.paragraphs_assessed ??
    sections.reduce(
      (sum, s) => sum + (s.paragraphs?.filter((p) => p.label !== "not_assessed").length ?? 0),
      0
    );

  const skippedParagraphs = report.assessment?.paragraphs_skipped ??
    (totalParagraphs - assessedParagraphs);

  const wordsAssessed = report.assessment?.words_assessed ??
    sections.reduce((sum, s) => sum + (s.stats?.assessed_words ?? 0), 0);

  const isInsufficientText = Boolean(
    report.assessment?.insufficient_text ||
    (report.transparency_report?.document_band === "Insufficient text") ||
    assessedParagraphs < 3
  );

  const totalFlaggedCount = useMemo(() => {
    return sections.reduce((sum, s) => {
      return (
        sum +
        (s.paragraphs?.filter((p) => p.label === "ai" || p.label === "uncertain").length ?? 0)
      );
    }, 0);
  }, [sections]);

  return (
    <div className={styles.container}>
      {/* Insufficient Text Banner */}
      {isInsufficientText && (
        <div className={styles.warningBanner} role="alert">
          <AlertTriangle size={24} className={styles.warningIcon} aria-hidden="true" />
          <div>
            <h3 className={styles.warningTitle}>Insufficient text to assess</h3>
            <p className={styles.warningText}>
              Fewer than 3 prose paragraphs were eligible for sequence evaluation.
              Aggregated Human and AI contribution ranges are withheld because short or fragmented
              text yields unreliable statistical distributions.
            </p>
          </div>
        </div>
      )}

      {/* Summary Card with Controls */}
      <div className={styles.summaryCard}>
        <div className={styles.summaryHeader}>
          <div className={styles.summaryTitleGroup}>
            <h3 className={styles.summaryTitle}>Document Section Inspection</h3>
            <p className={styles.summarySubtitle}>
              Interactive sequence-level inspection across sections, paragraphs, and sentence likelihood distributions.
            </p>
          </div>

          <div className={styles.toolbar}>
            <label className={styles.filterToggle}>
              <Filter size={14} aria-hidden="true" />
              <input
                type="checkbox"
                checked={showFlaggedOnly}
                onChange={(e) => setShowFlaggedOnly(e.target.checked)}
                className={styles.filterCheckbox}
              />
              <span>Show flagged paragraphs only ({totalFlaggedCount})</span>
            </label>

            <button type="button" onClick={expandAll} className={styles.actionButton}>
              Expand all
            </button>
            <button type="button" onClick={collapseAll} className={styles.actionButton}>
              Collapse all
            </button>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className={styles.metricsGrid}>
          <div className={styles.metricItem}>
            <span className={styles.metricLabel}>Total Sections</span>
            <span className={styles.metricValue}>{sections.length}</span>
            <span className={styles.metricSubtext}>Extracted manuscript divisions</span>
          </div>

          <div className={styles.metricItem}>
            <span className={styles.metricLabel}>Total Paragraphs</span>
            <span className={styles.metricValue}>{totalParagraphs}</span>
            <span className={styles.metricSubtext}>Prose & metadata units</span>
          </div>

          <div className={styles.metricItem}>
            <span className={styles.metricLabel}>Assessed Paragraphs</span>
            <span className={styles.metricValue}>{assessedParagraphs}</span>
            <span className={styles.metricSubtext}>{wordsAssessed} prose words evaluated</span>
          </div>

          <div className={styles.metricItem}>
            <span className={styles.metricLabel}>Skipped Paragraphs</span>
            <span className={styles.metricValue}>{skippedParagraphs}</span>
            <span className={styles.metricSubtext}>Under 40 words / non-prose</span>
          </div>
        </div>
      </div>

      {/* Sections List */}
      <div className={styles.sectionsList}>
        {sections.length > 0 ? (
          sections.map((section, idx) => (
            <SectionPanel
              key={idx}
              section={section}
              isOpen={openSectionIndices.has(idx)}
              onToggle={() => toggleSection(idx)}
              showFlaggedOnly={showFlaggedOnly}
            />
          ))
        ) : (
          <div className={styles.emptyFilterNote}>
            No sections found in this manuscript report.
          </div>
        )}
      </div>
    </div>
  );
}
