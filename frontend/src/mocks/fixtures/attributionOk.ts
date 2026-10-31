import type { Report } from "@/types/report";
import { createFixture } from "./helpers";

export const attributionOk: Report = createFixture({
  synthetic: true,
  attribution: {
    status: "ok",
    reason: null,
    method: "TRACE-inspired",
    experimental: true,
    margin: 0.14,
    ranked_candidates: [
      { label: "Llama-3-70B-Instruct", similarity: 0.88 },
      { label: "GPT-4o-2024-05-13", similarity: 0.74 },
      { label: "Claude-3.5-Sonnet", similarity: 0.62 },
      { label: "Mistral-Large-2407", similarity: 0.51 },
      { label: "Qwen-2.5-72B-Instruct", similarity: 0.43 },
    ],
  },
});

