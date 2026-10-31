import type { Report } from "@/types/report";
import { createFixture } from "./helpers";

export const attributionUnavailable: Report = createFixture({
  synthetic: true,
  attribution: {
    status: "unavailable",
    reason: "Document contains 1,240 words (~1,600 tokens), falling below the 10,000-token threshold required for statistical transition matrix estimation.",
    ranked_candidates: [],
    margin: null,
    method: "TRACE-inspired",
    experimental: true,
  },
});

