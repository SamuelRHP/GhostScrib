import rawDemo from "./demo_report.json";
import type { Report } from "@/types/report";

export const demoReport: Report = {
  ...(rawDemo as unknown as Report),
  synthetic: true,
};

export default demoReport;
