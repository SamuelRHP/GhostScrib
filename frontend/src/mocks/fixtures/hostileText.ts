import type { Report } from "@/types/report";
import { demoReport } from "@/mocks/demoReport";
import { createFixture } from "./helpers";

export const hostileText: Report = createFixture({
  synthetic: true,
  document: {
    field: "cs_eng",
    n_words: 280,
    parse_warnings: [
      "Warning: Detected raw HTML token: <script>alert('parse-warning')</script>",
      "Warning: Bidirectional text markers present in section headings.",
    ],
    references: [
      "[1] <script>alert('xss-citation')</script> John Doe et al., 2024.",
      "[2] <img src='x' onerror='alert(\"img-citation\")' /> Reference with raw HTML tags.",
      "[3] CJK Reference: 科学论文验证系统研究, 北京大学出版社, 2025.",
    ],
    sections: [
      {
        name: "1. Security & Sanitization: <script>alert('section-header')</script>",
        band: "high",
        stats: {
          assessed_words: 150,
          n_ai: 2,
          n_uncertain: 0,
          share_ai: 1.0,
          share_uncertain: 0.0,
        },
        notes: "Section with raw HTML: <em>Note with HTML tags</em> and <b onmouseover='alert(1)'>hover</b>",
        paragraphs: [
          {
            text: "<script>alert('paragraph-xss-1')</script><iframe src=\"javascript:alert('iframe')\"></iframe>This paragraph begins with malicious script tags that must render as inert text without executing. <style>body{display:none}</style>",
            words: 25,
            section: "1. Security & Sanitization: <script>alert('section-header')</script>",
            label: "ai",
            score: 1.55,
            sentences: [
              {
                text: "<script>alert('paragraph-xss-1')</script><iframe src=\"javascript:alert('iframe')\"></iframe>This paragraph begins with malicious script tags that must render as inert text without executing.",
                score: 1.55,
              },
              {
                text: "<style>body{display:none}</style>",
                score: 1.25,
              },
            ],
          },
          {
            text: "Unbroken token stress test: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA ensures word wrapping handles arbitrary strings.",
            words: 6,
            section: "1. Security & Sanitization: <script>alert('section-header')</script>",
            label: "ai",
            score: 1.15,
            sentences: [
              {
                text: "Unbroken token stress test: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA ensures word wrapping handles arbitrary strings.",
                score: 1.15,
              },
            ],
          },
        ],
      },
      {
        name: "2. Multilingual & RTL: مرحبا بالعالم שלום",
        band: "low",
        stats: {
          assessed_words: 130,
          n_ai: 0,
          n_uncertain: 1,
          share_ai: 0.0,
          share_uncertain: 1.0,
        },
        notes: null,
        paragraphs: [
          {
            text: "RTL and CJK test: هذا نص تجريبي باللغة العربية لاختبار اتجاه النص. ובנוסף משפט בדיקה בעברית לבדיקת תקינות. 以及中文和日本語の混合テスト。Special symbols: © ® ™ § ¶ † ‡ • ‰ ‱ € £ ¥ ₹.",
            words: 35,
            section: "2. Multilingual & RTL: مرحبا بالعالم שלום",
            label: "uncertain",
            score: 0.52,
            sentences: [
              {
                text: "RTL and CJK test: هذا نص تجريبي باللغة العربية لاختبار اتجاه النص.",
                score: 0.45,
              },
              {
                text: "ובנוסף משפט בדיקה בעברית לבדיקת תקינות. 以及中文和日本語の混合テスト。",
                score: 0.55,
              },
              {
                text: "Special symbols: © ® ™ § ¶ † ‡ • ‰ ‱ € £ ¥ ₹.",
                score: 0.50,
              },
            ],
          },
        ],
      },
    ],
  },
  transparency_report: {
    ...demoReport.transparency_report,
    banner: "SYNTHETIC DEMO DATA: Hostile boundary fixture containing unescaped HTML, script tags, RTL prose, and long tokens.",
  },
  citation_integrity: {
    total: 3,
    verified: 1,
    partial: 1,
    unverified: 1,
    not_checked: 0,
    out_of_range_intext_citations: [],
    per_reference: [
      {
        raw: "[1] <script>alert('xss-citation')</script> John Doe et al., 2024.",
        matched_title: "<script>alert('matched-title')</script>",
        matched_doi: "10.1000/182<script>alert(1)</script>",
        status: "unverified",
        similarity: 0.1,
      },
      {
        raw: "[2] <img src='x' onerror='alert(\"img-citation\")' /> Reference with raw HTML tags.",
        matched_title: "Clean Matched Title",
        matched_doi: "10.1000/182",
        status: "partial",
        similarity: 0.65,
      },
      {
        raw: "[3] CJK Reference: 科学论文验证系统研究, 北京大学出版社, 2025.",
        matched_title: "科学论文验证系统研究",
        matched_doi: "10.1000/cjk.2025",
        status: "verified",
        similarity: 0.95,
      },
    ],
  },
});
