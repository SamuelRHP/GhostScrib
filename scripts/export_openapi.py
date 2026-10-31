"""Export OpenAPI JSON specification from the FastAPI application."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.main import app


def export_openapi() -> Path:
    openapi_schema = app.openapi()
    output_path = ROOT / "docs" / "openapi.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(openapi_schema, indent=2), encoding="utf-8")
    print(f"OpenAPI schema successfully exported to {output_path}")
    return output_path


if __name__ == "__main__":
    export_openapi()
