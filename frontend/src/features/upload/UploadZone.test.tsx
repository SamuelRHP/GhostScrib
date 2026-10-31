import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import UploadZone from "./UploadZone";

describe("UploadZone Component", () => {
  it("renders upload zone and hidden file input", () => {
    const onFileSelect = vi.fn();
    render(<UploadZone onFileSelect={onFileSelect} />);

    expect(screen.getByTestId("upload-dropzone")).toBeDefined();
    const input = screen.getByTestId("file-input") as HTMLInputElement;
    expect(input).toBeDefined();
    expect(input.type).toBe("file");
    expect(input.style.display).toBe("none");
  });

  it("click on drop zone activates the file input click()", () => {
    const onFileSelect = vi.fn();
    render(<UploadZone onFileSelect={onFileSelect} />);

    const input = screen.getByTestId("file-input");
    const clickSpy = vi.spyOn(input, "click");

    const dropzone = screen.getByTestId("upload-dropzone");
    fireEvent.click(dropzone);

    expect(clickSpy).toHaveBeenCalledTimes(1);
  });

  it("keyboard Enter and Space activate the file input click()", () => {
    const onFileSelect = vi.fn();
    render(<UploadZone onFileSelect={onFileSelect} />);

    const input = screen.getByTestId("file-input");
    const clickSpy = vi.spyOn(input, "click");

    const dropzone = screen.getByTestId("upload-dropzone");

    // Enter key
    fireEvent.keyDown(dropzone, { key: "Enter" });
    expect(clickSpy).toHaveBeenCalledTimes(1);

    // Space key
    fireEvent.keyDown(dropzone, { key: " " });
    expect(clickSpy).toHaveBeenCalledTimes(2);

    // Other key should not trigger click
    fireEvent.keyDown(dropzone, { key: "Tab" });
    expect(clickSpy).toHaveBeenCalledTimes(2);
  });

  it("handles valid file drop and calls onFileSelect", () => {
    const onFileSelect = vi.fn();
    render(<UploadZone onFileSelect={onFileSelect} />);

    const dropzone = screen.getByTestId("upload-dropzone");
    const file = new File(["dummy content"], "manuscript.pdf", { type: "application/pdf" });

    // Drag over activates visual state
    fireEvent.dragOver(dropzone);
    expect(screen.getByText("Drop your manuscript here")).toBeDefined();

    // Drop file
    fireEvent.drop(dropzone, {
      dataTransfer: {
        files: [file],
      },
    });

    expect(onFileSelect).toHaveBeenCalledTimes(1);
    expect(onFileSelect).toHaveBeenCalledWith(file);
    expect(screen.queryByTestId("upload-error")).toBeNull();
  });

  it("handles valid DOCX and TXT via file input change", () => {
    const onFileSelect = vi.fn();
    render(<UploadZone onFileSelect={onFileSelect} />);

    const input = screen.getByTestId("file-input");

    const docxFile = new File(["docx content"], "paper.docx", {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });
    fireEvent.change(input, { target: { files: [docxFile] } });
    expect(onFileSelect).toHaveBeenCalledWith(docxFile);

    const txtFile = new File(["text content"], "paper.txt", { type: "text/plain" });
    fireEvent.change(input, { target: { files: [txtFile] } });
    expect(onFileSelect).toHaveBeenCalledWith(txtFile);
  });

  it("rejects wrong file type with clear client-side error message", () => {
    const onFileSelect = vi.fn();
    render(<UploadZone onFileSelect={onFileSelect} />);

    const input = screen.getByTestId("file-input");
    const invalidFile = new File(["binary"], "malicious.exe", { type: "application/x-msdownload" });

    fireEvent.change(input, { target: { files: [invalidFile] } });

    expect(onFileSelect).not.toHaveBeenCalled();
    const errorAlert = screen.getByTestId("upload-error");
    expect(errorAlert).toBeDefined();
    expect(errorAlert.textContent).toContain("Unsupported file type");
  });

  it("rejects oversized file (>20 MB) with clear client-side error message", () => {
    const onFileSelect = vi.fn();
    render(<UploadZone onFileSelect={onFileSelect} />);

    const input = screen.getByTestId("file-input");
    // 25 MB dummy file
    const oversizedFile = new File(["x".repeat(100)], "huge_paper.pdf", { type: "application/pdf" });
    Object.defineProperty(oversizedFile, "size", { value: 25 * 1024 * 1024 });

    fireEvent.change(input, { target: { files: [oversizedFile] } });

    expect(onFileSelect).not.toHaveBeenCalled();
    const errorAlert = screen.getByTestId("upload-error");
    expect(errorAlert).toBeDefined();
    expect(errorAlert.textContent).toContain("File is too large (25.0 MB)");
  });

  it("rejects empty file (0 bytes) with clear error message", () => {
    const onFileSelect = vi.fn();
    render(<UploadZone onFileSelect={onFileSelect} />);

    const input = screen.getByTestId("file-input");
    const emptyFile = new File([], "empty.txt", { type: "text/plain" });
    Object.defineProperty(emptyFile, "size", { value: 0 });

    fireEvent.change(input, { target: { files: [emptyFile] } });

    expect(onFileSelect).not.toHaveBeenCalled();
    const errorAlert = screen.getByTestId("upload-error");
    expect(errorAlert).toBeDefined();
    expect(errorAlert.textContent).toContain("empty (0 bytes)");
  });

  it("does not activate when disabled", () => {
    const onFileSelect = vi.fn();
    render(<UploadZone onFileSelect={onFileSelect} disabled={true} disabledReason="Detector is offline" />);

    const input = screen.getByTestId("file-input");
    const clickSpy = vi.spyOn(input, "click");
    const dropzone = screen.getByTestId("upload-dropzone");

    fireEvent.click(dropzone);
    expect(clickSpy).not.toHaveBeenCalled();

    fireEvent.keyDown(dropzone, { key: "Enter" });
    expect(clickSpy).not.toHaveBeenCalled();

    expect(screen.getByText("Detector is offline")).toBeDefined();
  });
});

