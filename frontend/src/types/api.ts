/**
 * GhostScrib API Types Contract
 * Mirrors the REST specifications defined in docs/WEB_CONTRACT.md
 */

export interface HealthResponse {
  api: "ok";
  detector: "healthy" | "down";
  gpu: boolean | null;
  attribution_available: boolean;
  version: string;
}

export type JobStageName =
  | "parsing"
  | "detection"
  | "stylometry"
  | "attribution"
  | "citations"
  | "scoring";

export type JobStageStatus = "pending" | "running" | "done" | "skipped" | "error";

export interface JobStage {
  name: JobStageName;
  status: JobStageStatus;
}

export type JobOverallStatus = "queued" | "running" | "done" | "error";

export type ApiErrorCode =
  | "file_too_large"
  | "unsupported_type"
  | "empty_file"
  | "corrupt_file"
  | "no_text_extracted"
  | "detector_unavailable"
  | "job_not_found"
  | "job_not_ready"
  | "internal_error";

export interface ApiErrorDetail {
  code: ApiErrorCode | string;
  message: string;
}

export interface ApiErrorResponse {
  error: ApiErrorDetail;
}

export interface JobResponse {
  job_id: string;
  status: JobOverallStatus;
  stage: JobStageName | string | null;
  stages: JobStage[];
  progress: number;
  queue_position: number | null;
  error: ApiErrorDetail | null;
}

export interface AnalyzeResponse {
  job_id: string;
}

export interface AnalyzeRequestParams {
  file: File;
  field: "cs_eng" | "other";
  disclosure?: string;
  check_citations?: boolean;
  run_attribution?: boolean;
}
