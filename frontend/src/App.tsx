import React from "react";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import LandingPage from "@/pages/LandingPage";
import HomePage from "@/pages/HomePage";
import AnalyzingPage from "@/pages/AnalyzingPage";
import ReportPage from "@/pages/ReportPage";
import AboutPage from "@/pages/AboutPage";
import DevSandbox from "@/pages/DevSandbox";

function NavigationHeader(): React.ReactElement {
  const location = useLocation();

  const navItems = [
    { label: "Home", path: "/" },
    { label: "Analyse", path: "/analyze" },
    { label: "Demo Report", path: "/report/demo" },
    { label: "About", path: "/about" },
    { label: "Dev Sandbox", path: "/dev/sandbox" },
  ];

  return (
    <header
      style={{
        borderBottom: "1px solid var(--color-border)",
        backgroundColor: "var(--color-bg-card)",
        position: "sticky",
        top: 0,
        zIndex: 100,
      }}
    >
      <div
        style={{
          maxWidth: "var(--container-max)",
          margin: "0 auto",
          padding: "var(--spacing-3) var(--spacing-6)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "var(--spacing-3)",
        }}
      >
        <Link
          to="/"
          style={{
            textDecoration: "none",
            display: "inline-flex",
            alignItems: "center",
            gap: "var(--spacing-2)",
          }}
        >
          <div
            style={{
              width: "30px",
              height: "32px",
              borderRadius: "var(--radius-control)",
              backgroundColor: "var(--color-primary)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--color-text-on-dark)",
              fontWeight: "var(--font-weight-bold)",
              fontSize: "var(--font-size-base)",
            }}
          >
            GS
          </div>
          <span
            style={{
              color: "var(--color-text)",
              fontWeight: "var(--font-weight-bold)",
              fontSize: "var(--font-size-lg)",
              letterSpacing: "-0.5px",
            }}
          >
            GhostScrib
          </span>
        </Link>
        <nav style={{ display: "flex", gap: "var(--spacing-2)", alignItems: "center", fontSize: "var(--font-size-sm)" }}>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  textDecoration: "none",
                  padding: "var(--spacing-1) var(--spacing-3)",
                  borderRadius: "var(--radius-pill)",
                  fontWeight: isActive ? "var(--font-weight-semibold)" : "var(--font-weight-medium)",
                  backgroundColor: isActive ? "var(--color-mint-pale)" : "transparent",
                  color: isActive ? "var(--color-primary)" : "var(--color-text-muted)",
                  transition: "background-color 0.15s, color 0.15s",
                }}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}

export default function App(): React.ReactElement {
  return (
    <BrowserRouter>
      {/* Global Navigation Header */}
      <NavigationHeader />

      {/* Main Content Viewport */}
      <main style={{ minHeight: "calc(100vh - 70px)" }}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/analyze" element={<HomePage />} />
          <Route path="/upload" element={<HomePage />} />
          <Route path="/analyzing/:jobId" element={<AnalyzingPage />} />
          <Route path="/report/:jobId" element={<ReportPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/dev/sandbox" element={<DevSandbox />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
