"""Citation integrity engine for GhostScrib (Layer 3).

Verifies references against Crossref and OpenAlex APIs, computes fuzzy title similarities,
flags unverified records with neutral terminology, and audits numeric in-text citations.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional

from ghostscrib.config import settings
from ghostscrib.integrity.cache import CitationCache
from ghostscrib.integrity.matcher import (
    calculate_title_similarity,
    extract_doi,
    extract_search_query_from_reference,
)
from ghostscrib.parsing.references import find_out_of_range_citations
from ghostscrib.schema import CitationResult, ReferenceDetail

logger = logging.getLogger(__name__)


class CitationVerifier:
    """Verifies bibliographic references against scholarly APIs with on-disk caching."""

    def __init__(
        self,
        cache: Optional[CitationCache] = None,
        contact_email: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        self.cache = cache or CitationCache()
        self.contact_email = contact_email or settings.CONTACT_EMAIL
        self.timeout = timeout or settings.CITATION_TIMEOUT
        self.headers = {
            "User-Agent": f"GhostScrib/0.1.0 (mailto:{self.contact_email})",
            "Accept": "application/json",
        }

    def _query_crossref_by_doi(self, doi: str) -> Optional[dict]:
        url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    message = data.get("message", {})
                    title_list = message.get("title", [])
                    title = title_list[0] if title_list else ""
                    return {"doi": doi, "title": title}
        except Exception as e:
            logger.debug(f"Crossref DOI query failed for {doi}: {e}")
        return None

    def _query_crossref_by_title(self, query: str) -> Optional[dict]:
        params = urllib.parse.urlencode({"query.bibliographic": query, "rows": 1})
        url = f"https://api.crossref.org/works?{params}"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    items = data.get("message", {}).get("items", [])
                    if items:
                        item = items[0]
                        title_list = item.get("title", [])
                        title = title_list[0] if title_list else ""
                        return {"doi": item.get("DOI"), "title": title}
        except Exception as e:
            logger.debug(f"Crossref title query failed for '{query}': {e}")
        return None

    def _query_openalex(self, query: str) -> Optional[dict]:
        params = urllib.parse.urlencode({"search": query, "per-page": 1})
        url = f"https://api.openalex.org/works?{params}"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    results = data.get("results", [])
                    if results:
                        res = results[0]
                        return {"doi": res.get("doi"), "title": res.get("display_name", "")}
        except Exception as e:
            logger.debug(f"OpenAlex query failed for '{query}': {e}")
        return None

    def verify_single_reference(self, ref_text: str, online: bool = True) -> ReferenceDetail:
        """Verify an individual reference string against cached or remote registries."""
        cached = self.cache.get(ref_text)
        if cached:
            return ReferenceDetail(**cached)

        if not online:
            detail = ReferenceDetail(raw=ref_text, status="not_checked", similarity=0.0)
            return detail

        doi = extract_doi(ref_text)
        search_query = extract_search_query_from_reference(ref_text)
        metadata = None

        try:
            # 1. Try Crossref with DOI if present
            if doi:
                metadata = self._query_crossref_by_doi(doi)

            # 2. Try Crossref bibliographic title search
            if not metadata and search_query:
                metadata = self._query_crossref_by_title(search_query)

            # 3. Fallback to OpenAlex
            if not metadata and search_query:
                metadata = self._query_openalex(search_query)

        except Exception as e:
            logger.warning(f"Network error verifying citation '{ref_text[:40]}...': {e}")
            return ReferenceDetail(raw=ref_text, status="not_checked", similarity=0.0)

        if not metadata or not metadata.get("title"):
            detail = ReferenceDetail(
                raw=ref_text,
                matched_doi=doi,
                status="unverified",
                similarity=0.0,
            )
            self.cache.set(ref_text, detail.model_dump())
            return detail

        matched_title = metadata.get("title", "")
        matched_doi = metadata.get("doi") or doi
        similarity = calculate_title_similarity(search_query, matched_title)

        # Categorize status based on thresholds
        if doi and similarity >= settings.CITATION_VERIFIED_DOI_SIM:
            status = "verified"
        elif not doi and similarity >= settings.CITATION_VERIFIED_TITLE_SIM:
            status = "verified"
        elif similarity >= settings.CITATION_PARTIAL_MIN_SIM:
            status = "partial"
        else:
            status = "unverified"

        detail = ReferenceDetail(
            raw=ref_text,
            matched_title=matched_title,
            matched_doi=matched_doi,
            status=status,
            similarity=similarity,
        )
        self.cache.set(ref_text, detail.model_dump())
        return detail

    def verify_references(
        self,
        references: List[str],
        body_text: str = "",
        online: bool = True,
    ) -> CitationResult:
        """Verify all bibliography items and evaluate in-text citation index validity."""
        details: List[ReferenceDetail] = []
        verified_count = 0
        partial_count = 0
        unverified_count = 0
        not_checked_count = 0

        for ref in references:
            det = self.verify_single_reference(ref, online=online)
            details.append(det)
            if det.status == "verified":
                verified_count += 1
            elif det.status == "partial":
                partial_count += 1
            elif det.status == "unverified":
                unverified_count += 1
            else:
                not_checked_count += 1

        out_of_range = find_out_of_range_citations(body_text, len(references))

        return CitationResult(
            total=len(references),
            verified=verified_count,
            partial=partial_count,
            unverified=unverified_count,
            not_checked=not_checked_count,
            per_reference=details,
            out_of_range_intext_citations=out_of_range,
        )

