/**
 * GhostScrib Report TypeScript Contract
 * Mirrors ghostscrib.schema.Report (Pydantic) exactly.
 */

export interface SentenceScore {
  text: string;
  score: number;
}

export type ParagraphLabel = "ai" | "uncertain" | "human" | "not_assessed";

export interface Paragraph {
  text: string;
  words: number;
  section: string;
  label: ParagraphLabel;
  score?: number | null;
  sentences: SentenceScore[];
  reason?: string | null;
}

export interface SectionStats {
  assessed_words: number;
  n_ai: number;
  n_uncertain: number;
  share_ai: number;
  share_uncertain: number;
}

export type SectionBand = "low" | "medium" | "high" | "not_assessed";

export interface Section {
  id?: string;
  name: string;
  paragraphs: Paragraph[];
  band: SectionBand;
  stats: SectionStats;
  notes?: string | null;
}

export type AcademicField = "cs_eng" | "other";

export interface ParsedDocument {
  sections: Section[];
  references: string[];
  disclosure_text?: string | null;
  field: AcademicField;
  n_words: number;
  parse_warnings: string[];
}

export interface StructureTrait {
  trait: string;
  value: number;
  human_mean: number;
  z: number;
}

export interface DescriptiveStylometry {
  mean_sentence_length: number;
  std_sentence_length: number;
  burstiness: number;
  type_token_ratio: number;
  passive_voice_rate?: number | null;
}

export interface StylometrySignal {
  structure_traits: StructureTrait[];
  n_extreme_traits: number;
  agreement: "supports" | "neutral";
  section_metrics: Record<string, DescriptiveStylometry>;
  structure_verdict?: string | null;
  structure_distance?: number | null;
  structure_p99?: number | null;
  structure_level?: string | null;
}

export interface CandidateScore {
  label: string;
  similarity: number;
}

export interface AttributionResult {
  status: "ok" | "unavailable";
  reason?: string | null;
  ranked_candidates: CandidateScore[];
  margin?: number | null;
  method: "TRACE" | "TRACE-inspired";
  experimental: boolean;
  total_tokens?: number | null;
}

export type CitationItemStatus = "verified" | "partial" | "unverified" | "not_checked";

export interface ReferenceDetail {
  raw: string;
  matched_title?: string | null;
  matched_doi?: string | null;
  status: CitationItemStatus;
  similarity: number;
  reason?: string | null;
}

export interface CitationResult {
  total: number;
  verified: number;
  partial: number;
  unverified: number;
  not_checked: number;
  per_reference: ReferenceDetail[];
  out_of_range_intext_citations: number[];
}

export type DisclosureStatementClass = "none" | "no_ai" | "editing_only" | "substantial" | "unspecified";
export type DisclosureConsistency = "consistent" | "possible_mismatch" | "cannot_assess";

export interface DisclosureResult {
  statement_class: DisclosureStatementClass;
  consistency: DisclosureConsistency;
  explanation: string;
}

export type DocumentBand = "Low" | "Medium" | "High" | "Insufficient text";
export type ProvenanceConfidence = "Low" | "Medium" | "High";

export interface JournalTransparencyReport {
  human_contribution: [number, number];
  ai_contribution: [number, number];
  provenance_confidence: ProvenanceConfidence;
  confidence_reasons: string[];
  disclosure_consistency: "Consistent" | "Possible mismatch" | "Cannot assess";
  disclosure_explanation: string;
  citation_summary: string;
  flagged_sections: string[];
  document_band: DocumentBand;
  banner: string;
  footnote: string;
}

export interface AssessmentStats {
  paragraphs_total: number;
  paragraphs_assessed: number;
  paragraphs_skipped: number;
  words_total: number;
  words_assessed: number;
  skipped_share: number;
  insufficient_text: boolean;
}

export interface Report {
  document: ParsedDocument;
  transparency_report: JournalTransparencyReport;
  stylometry: StylometrySignal;
  attribution: AttributionResult;
  citation_integrity: CitationResult;
  disclosure: DisclosureResult;
  detector_reference_verdict?: string | null;
  limitations: string[];
  metadata: Record<string, unknown>;

  // Additive contract fields
  synthetic: boolean;
  assessment: AssessmentStats;
}
