import type { Report } from "@/types/report";
import { demoReport } from "@/mocks/demoReport";
import { createFixture } from "./helpers";

export const citationsMixed: Report = createFixture({
  synthetic: true,
  citation_integrity: {
    total: 5,
    verified: 2,
    partial: 1,
    unverified: 1,
    not_checked: 1,
    out_of_range_intext_citations: [14, 27, 88],
    per_reference: [
      {
        raw: "[1] A. Vaswani et al., 'Attention is all you need,' in Advances in Neural Information Processing Systems, 2017.",
        matched_title: "Attention is All You Need",
        matched_doi: "10.5555/3295222.3295349",
        status: "verified",
        similarity: 0.96,
      },
      {
        raw: "[2] J. Devlin et al., 'BERT: Pre-training of deep bidirectional transformers for language understanding,' NAACL, 2019.",
        matched_title: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        matched_doi: "10.18653/v1/n19-1423",
        status: "verified",
        similarity: 0.98,
      },
      {
        raw: "[3] R. Kumar et al., 'Heuristic approximations in transformer latency evaluation,' IEEE Trans. Software Eng., 2024.",
        matched_title: "Latency Evaluation for Deep Neural Network Inference",
        matched_doi: "10.1109/TSE.2023.1098765",
        status: "partial",
        similarity: 0.68,
      },
      {
        raw: "[4] K. H. Wang and M. S. Miller, 'Fabricated and Hallucinatory Citations in Generative Biomedical Literature,' J. Sci. Comput., 2026.",
        matched_title: null,
        matched_doi: null,
        status: "unverified",
        similarity: 0.0,
      },
      {
        raw: "[5] Local Institutional Report on Computing Infrastructure Guidelines, Internal Memo 42, 2025.",
        matched_title: null,
        matched_doi: null,
        status: "not_checked",
        similarity: 0.0,
      },
    ],
  },
  transparency_report: {
    ...demoReport.transparency_report,
    citation_summary: "2 verified, 1 partial, 1 unverified, 1 not checked (3 out-of-range in-text citations)",
  },
});
