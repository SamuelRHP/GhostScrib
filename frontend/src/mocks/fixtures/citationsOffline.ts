import type { Report } from "@/types/report";
import { demoReport } from "@/mocks/demoReport";
import { createFixture } from "./helpers";

export const citationsOffline: Report = createFixture({
  synthetic: true,
  citation_integrity: {
    total: 4,
    verified: 0,
    partial: 0,
    unverified: 0,
    not_checked: 4,
    out_of_range_intext_citations: [],
    per_reference: [
      {
        raw: "[1] A. Vaswani et al., 'Attention is all you need,' NeurIPS, 2017.",
        matched_title: null,
        matched_doi: null,
        status: "not_checked",
        similarity: 0.0,
      },
      {
        raw: "[2] J. Devlin et al., 'BERT: Pre-training of deep bidirectional transformers,' NAACL, 2019.",
        matched_title: null,
        matched_doi: null,
        status: "not_checked",
        similarity: 0.0,
      },
      {
        raw: "[3] T. Brown et al., 'Language models are few-shot learners,' NeurIPS, 2020.",
        matched_title: null,
        matched_doi: null,
        status: "not_checked",
        similarity: 0.0,
      },
      {
        raw: "[4] H. Touvron et al., 'Llama: Open and efficient foundation language models,' arXiv, 2023.",
        matched_title: null,
        matched_doi: null,
        status: "not_checked",
        similarity: 0.0,
      },
    ],
  },
  transparency_report: {
    ...demoReport.transparency_report,
    citation_summary: "0 of 4 checked (4 offline / not checked)",
  },
});
