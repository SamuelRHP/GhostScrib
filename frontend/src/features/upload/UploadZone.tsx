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
    // Only set dragging false if leaving the container itself
    if (e.currentTarget.contains(e.relatedTarget as Node)) return;
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <div>
      {/* Hidden Native File Input */}
      <input
        ref={fileInputRef}
        id="manuscript-file-input"
        data-testid="file-input"
        type="file"
        accept={accept}
        onChange={handleInputChange}
        disabled={disabled}
        style={{ display: "none" }}
        tabIndex={-1}
      />

      {/* Accessible Interactive Drop Zone */}
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
            ? "2px dashed var(--color-primary, #2563eb)"
            : "2px dashed var(--color-border-subtle, #cbd5e1)",
          borderRadius: "var(--radius-lg, 12px)",
          padding: "var(--spacing-8, 32px)",
          backgroundColor: isDragging
            ? "rgba(37, 99, 235, 0.05)"
            : disabled
            ? "var(--color-bg-subtle, #f8f9fa)"
            : "var(--color-bg-card, #ffffff)",
          cursor: disabled ? "not-allowed" : "pointer",
          opacity: disabled ? 0.65 : 1,
          textAlign: "center",
          transition: "all 0.15s ease-in-out",
          outline: "none",
        }}
      >
        <div style={{ marginBottom: "var(--spacing-4, 16px)" }}>
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke={isDragging ? "var(--color-primary, #2563eb)" : "var(--color-text-secondary, #64748b)"}
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
            margin: "0 0 var(--spacing-2, 8px) 0",
            fontSize: "var(--font-size-lg, 18px)",
            fontWeight: "var(--font-weight-semibold, 600)",
            color: "var(--color-text-primary, #1e293b)",
          }}
        >
          {isDragging ? "Drop your manuscript here" : "Click to select or drag & drop a manuscript"}
        </h3>

        <p
          style={{
            margin: "0 0 var(--spacing-4, 16px) 0",
            fontSize: "var(--font-size-sm, 14px)",
            color: "var(--color-text-secondary, #64748b)",
          }}
        >
          Supports PDF (.pdf), Word (.docx), or plain text (.txt) &middot; Up to 20 MB
        </p>

        {disabledReason && (
          <div
            style={{
              display: "inline-block",
              padding: "4px 12px",
              backgroundColor: "rgba(239, 68, 68, 0.1)",
              color: "#dc2626",
              borderRadius: "var(--radius-sm, 6px)",
              fontSize: "var(--font-size-xs, 12px)",
              fontWeight: 500,
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
                padding: "8px 16px",
                backgroundColor: "var(--color-primary, #2563eb)",
                color: "#ffffff",
                borderRadius: "var(--radius-md, 8px)",
                fontSize: "var(--font-size-sm, 14px)",
                fontWeight: 500,
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
            marginTop: "var(--spacing-3, 12px)",
            padding: "var(--spacing-3, 12px) var(--spacing-4, 16px)",
            backgroundColor: "rgba(220, 38, 38, 0.08)",
            border: "1px solid rgba(220, 38, 38, 0.3)",
            borderRadius: "var(--radius-md, 8px)",
            color: "#b91c1c",
            fontSize: "var(--font-size-sm, 14px)",
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
              color: "#b91c1c",
              cursor: "pointer",
              fontWeight: "bold",
              fontSize: "16px",
              padding: "0 4px",
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

