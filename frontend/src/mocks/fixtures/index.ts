import type { Report } from "@/types/report";
import { demoReport } from "@/mocks/demoReport";
import { mixedMedium } from "./mixedMedium";
import { highAi } from "./highAi";
import { allHuman } from "./allHuman";
import { zeroAssessed } from "./zeroAssessed";
import { mostlySkipped } from "./mostlySkipped";
import { attributionUnavailable } from "./attributionUnavailable";
import { attributionOk } from "./attributionOk";
import { citationsOffline } from "./citationsOffline";
import { citationsMixed } from "./citationsMixed";
import { hugeDocument } from "./hugeDocument";
import { hostileText } from "./hostileText";
import { emptySections } from "./emptySections";

export const fixtures: Record<string, Report> = {
  "Demo Manuscript (Default)": demoReport,
  "Mixed Medium Band": mixedMedium,
  "High AI Resemblance": highAi,
  "100% Human Authentic": allHuman,
  "Zero Assessed (Insufficient Text)": zeroAssessed,
  "Mostly Skipped (<40 words)": mostlySkipped,
  "Attribution: Unavailable": attributionUnavailable,
  "Attribution: Valid Candidates": attributionOk,
  "Citations: Offline / Unchecked": citationsOffline,
  "Citations: Mixed & Range Issues": citationsMixed,
  "Large Document (320+ Paragraphs)": hugeDocument,
  "Hostile Text (XSS / RTL / Unicode)": hostileText,
  "Empty Sections & Paragraphs": emptySections,
};

export {
  mixedMedium,
  highAi,
  allHuman,
  zeroAssessed,
  mostlySkipped,
  attributionUnavailable,
  attributionOk,
  citationsOffline,
  citationsMixed,
  hugeDocument,
  hostileText,
  emptySections,
};

export default fixtures;
