import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import DevSandbox from "./DevSandbox";
import { fixtures } from "@/mocks/fixtures";

describe("DevSandbox Component", () => {
  it("renders sandbox header and controls", () => {
    render(<DevSandbox />);
    expect(screen.getByText("Developer Sandbox (Member 3)")).toBeDefined();
    expect(screen.getByLabelText("Select Fixture")).toBeDefined();
    expect(screen.getByLabelText("Select View Tab")).toBeDefined();
    expect(screen.getByText("SYNTHETIC DEMO DATA")).toBeDefined();
  });

  it("can switch between all fixtures without crashing", () => {
    const { container } = render(<DevSandbox />);
    const fixtureSelect = screen.getByLabelText("Select Fixture");

    for (const key of Object.keys(fixtures)) {
      fireEvent.change(fixtureSelect, { target: { value: key } });
      expect(container).toBeDefined();
    }
  });

  it("can switch between all tabs without crashing", () => {
    render(<DevSandbox />);
    const tabSelect = screen.getByLabelText("Select View Tab");

    const tabs = ["document", "attribution", "citations", "breakdown", "limitations", "overview"];
    for (const tab of tabs) {
      fireEvent.change(tabSelect, { target: { value: tab } });
      expect(screen.getByRole("region", { name: "Tab Preview" })).toBeDefined();
    }
  });

  it("renders hostile text fixture safely without executing or creating scripts", () => {
    const { container } = render(<DevSandbox />);
    const fixtureSelect = screen.getByLabelText("Select Fixture");
    fireEvent.change(fixtureSelect, { target: { value: "Hostile Text (XSS / RTL / Unicode)" } });

    // Ensure no <script> tags were injected into the document body
    const scriptTags = container.querySelectorAll("script");
    expect(scriptTags.length).toBe(0);
  });
});

