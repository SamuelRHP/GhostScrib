import React, { useRef, useState } from "react";

export interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  disabledReason?: string;
  accept?: string;
  maxSizeBytes?: number;
}

const DEFAULT_MAX_SIZE_BYTES = 20 * 1024 * 1024; // 20 MB
const DEFAULT_ACCEPT = ".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain";

const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"];
const ALLOWED_MIME_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text/plain",
];

export default function UploadZone({
  onFileSelect,
  disabled = false,
  disabledReason,
  accept = DEFAULT_ACCEPT,
  maxSizeBytes = DEFAULT_MAX_SIZE_BYTES,
}: UploadZoneProps): React.ReactElement {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const validateFile = (file: File): boolean => {
    setErrorMessage(null);

    // 1. Check empty file
    if (file.size === 0) {
      setErrorMessage("The selected file is empty (0 bytes). Please select a valid document.");
      return false;
    }

    // 2. Check file type / extension
    const extMatch = file.name.match(/\.[^.]+$/);
    const extension = extMatch ? extMatch[0].toLowerCase() : "";
    const isExtensionValid = ALLOWED_EXTENSIONS.includes(extension);
    const isMimeValid = ALLOWED_MIME_TYPES.includes(file.type);

    if (!isExtensionValid && !isMimeValid) {
      setErrorMessage(
        "Unsupported file type. Please upload a PDF (.pdf), Word document (.docx), or plain text file (.txt)."
      );
      return false;
    }

    // 3. Check file size
    if (file.size > maxSizeBytes) {
      const maxMb = (maxSizeBytes / (1024 * 1024)).toFixed(0);
      const actualMb = (file.size / (1024 * 1024)).toFixed(1);
      setErrorMessage(`File is too large (${actualMb} MB). Maximum allowed size is ${maxMb} MB.`);
      return false;
    }

    return true;
  };

  const handleFile = (file: File) => {
    if (disabled) return;
    if (validateFile(file)) {
      onFileSelect(file);
    }
  };

  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      // Clear value so re-selecting same file triggers onChange
      fileInputRef.current.value = "";
      fileInputRef.current.click();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (disabled) return;
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleClick();
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled && !isDragging) {
      setIsDragging(true);
    }
  };

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled && !isDragging) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    // Only unset dragging if left the container itself
    if (e.currentTarget.contains(e.relatedTarget as Node)) {
      return;
    }
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (disabled) return;

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  return (
    <div style={{ width: "100%" }}>
      {/* Real HTML file input: Visually hidden but accessible via click/keyboard forwarding */}
      <input
        type="file"
        ref={fileInputRef}
        data-testid="file-input"
        onChange={handleInputChange}
        accept={accept}
        tabIndex={-1}
        aria-hidden="true"
        style={{ display: "none" }}
      />

      {/* Drop Zone Box */}
      <div
        role="button"
        data-testid="upload-dropzone"
        tabIndex={disabled ? -1 : 0}
        aria-label="Upload manuscript file (PDF, DOCX, or TXT)"
        aria-disabled={disabled}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        style={{
          border: isDragging
            ? "2px dashed var(--color-primary)"
            : "2px dashed var(--color-border)",
          borderRadius: "var(--radius-card)",
          padding: "var(--spacing-8)",
          backgroundColor: isDragging
            ? "var(--color-mint-pale)"
            : disabled
            ? "var(--color-surface)"
            : "var(--color-bg-card)",
          cursor: disabled ? "not-allowed" : "pointer",
          opacity: disabled ? 0.65 : 1,
          textAlign: "center",
          transition: "all 0.15s ease-in-out",
          boxShadow: "var(--shadow-card)",
          outline: "none",
        }}
      >
        <div style={{ marginBottom: "var(--spacing-4)" }}>
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke={isDragging ? "var(--color-primary)" : "var(--color-primary)"}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ display: "inline-block" }}
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="12" y1="18" x2="12" y2="12" />
            <polyline points="9 15 12 12 15 15" />
          </svg>
        </div>

        <h3
          style={{
            margin: "0 0 var(--spacing-2) 0",
            fontSize: "var(--font-size-lg)",
            fontWeight: "var(--font-weight-semibold)",
            color: "var(--color-text)",
          }}
        >
          {isDragging ? "Drop your manuscript here" : "Click to select or drag & drop a manuscript"}
        </h3>

        <p
          style={{
            margin: "0 0 var(--spacing-4) 0",
            fontSize: "var(--font-size-sm)",
            color: "var(--color-text-muted)",
          }}
        >
          Supports PDF (.pdf), Word (.docx), or plain text (.txt) &middot; Up to 20 MB
        </p>

        {disabledReason && (
          <div
            style={{
              display: "inline-block",
              padding: "var(--spacing-1) var(--spacing-3)",
              backgroundColor: "var(--color-amber-bg)",
              color: "var(--color-amber-text)",
              border: "1px solid var(--color-amber-border)",
              borderRadius: "var(--radius-chip)",
              fontSize: "var(--font-size-xs)",
              fontWeight: "var(--font-weight-medium)",
            }}
          >
            {disabledReason}
          </div>
        )}

        {!disabled && (
          <div>
            <span
              style={{
                display: "inline-block",
                padding: "var(--spacing-2) var(--spacing-4)",
                backgroundColor: "var(--color-primary)",
                color: "var(--color-text-on-dark)",
                borderRadius: "var(--radius-control)",
                fontSize: "var(--font-size-sm)",
                fontWeight: "var(--font-weight-medium)",
                pointerEvents: "none",
              }}
            >
              Browse Files
            </span>
          </div>
        )}
      </div>

      {/* Validation Error Message Alert */}
      {errorMessage && (
        <div
          role="alert"
          data-testid="upload-error"
          style={{
            marginTop: "var(--spacing-3)",
            padding: "var(--spacing-3) var(--spacing-4)",
            backgroundColor: "var(--color-amber-bg)",
            border: "1px solid var(--color-amber-border)",
            borderRadius: "var(--radius-control)",
            color: "var(--color-amber-text)",
            fontSize: "var(--font-size-sm)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <span>{errorMessage}</span>
          <button
            type="button"
            onClick={() => setErrorMessage(null)}
            style={{
              background: "none",
              border: "none",
              color: "var(--color-amber-text)",
              cursor: "pointer",
              fontWeight: "var(--font-weight-bold)",
              fontSize: "var(--font-size-base)",
              padding: "0 var(--spacing-1)",
            }}
            aria-label="Dismiss error"
          >
            &times;
          </button>
        </div>
      )}
    </div>
  );
}
