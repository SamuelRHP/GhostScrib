"""Standardized GhostScrib API error classes and responses."""

from __future__ import annotations
from typing import Dict, Any
from fastapi import HTTPException
from fastapi.responses import JSONResponse


class APIError(HTTPException):
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
            }
        }

    def to_response(self) -> JSONResponse:
        return JSONResponse(status_code=self.status_code, content=self.to_dict())


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )
