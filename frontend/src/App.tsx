import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import HomePage from "@/pages/HomePage";
import AnalyzingPage from "@/pages/AnalyzingPage";
import ReportPage from "@/pages/ReportPage";
import AboutPage from "@/pages/AboutPage";
import DevSandbox from "@/pages/DevSandbox";

export default function App(): React.ReactElement {
  return (
    <BrowserRouter>
      {/* Global Navigation Header */}
      <header
        style={{
          borderBottom: "1px solid var(--color-border)",
          backgroundColor: "var(--color-bg-card)",
          padding: "var(--spacing-3) var(--spacing-6)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Link
          to="/"
          style={{
            textDecoration: "none",
            color: "var(--color-text-primary)",
            fontWeight: "var(--font-weight-bold)",
            fontSize: "var(--font-size-lg)",
            letterSpacing: "-0.5px",
          }}
        >
          GhostScrib
        </Link>
        <nav style={{ display: "flex", gap: "var(--spacing-4)", fontSize: "var(--font-size-sm)" }}>
          <Link
            to="/"
            style={{ textDecoration: "none", color: "var(--color-text-secondary)" }}
          >
            Upload
          </Link>
          <Link
            to="/report/demo"
            style={{ textDecoration: "none", color: "var(--color-text-secondary)" }}
          >
            Demo Report
          </Link>
          <Link
            to="/about"
            style={{ textDecoration: "none", color: "var(--color-text-secondary)" }}
          >
            About
          </Link>
          <Link
            to="/dev/sandbox"
            style={{ textDecoration: "none", color: "var(--color-primary)" }}
          >
            Dev Sandbox
          </Link>
        </nav>
      </header>

      {/* Main Content Viewport */}
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analyzing/:jobId" element={<AnalyzingPage />} />
          <Route path="/report/:jobId" element={<ReportPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/dev/sandbox" element={<DevSandbox />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
