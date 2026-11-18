"""Adzuna: real posting counts and salary samples for IT job titles."""
from __future__ import annotations

import os
import urllib.parse
from collections import Counter

from common import http_json, log, median

BASE = "https://api.adzuna.com/v1/api/jobs/{country}/search/1"


def _mid_salary(hit):
    low = hit.get("salary_min")
    high = hit.get("salary_max")
    try:
        if low and high:
            return (float(low) + float(high)) / 2
        if low or high:
            return float(low or high)
    except (TypeError, ValueError):
        return None
    return None


def _summarise(query, payload, top_n=5):
    hits = payload.get("results") or []
    salaries = [value for value in (_mid_salary(hit) for hit in hits) if value]
    companies = Counter(
        ((hit.get("company") or {}).get("display_name") or "").strip() for hit in hits
    )
    remote = 0
    for hit in hits:
        blob = "%s %s" % (hit.get("title") or "", hit.get("description") or "")
        if "remote" in blob.lower():
            remote += 1
    return {
        "query": query,
        "count": payload.get("count"),
        "sampled": len(hits),
        "salary_samples": len(salaries),
        "median_salary": median(salaries),
        "remote_share": round(remote / len(hits), 3) if hits else None,
        "top_companies": [name for name, _ in companies.most_common(top_n) if name],
    }


def parse(payloads, cfg):
    section = cfg["adzuna"]
    titles = []
    seen = {}
    for query in section["queries"]:
        payload = payloads.get(query)
        if payload is None:
            continue
        titles.append(_summarise(query, payload))
        for hit in payload.get("results") or []:
            key = hit.get("id") or hit.get("redirect_url")
            if key:
                seen.setdefault(str(key), hit)

    salaries = [value for value in (_mid_salary(hit) for hit in seen.values()) if value]
    companies = Counter(
        ((hit.get("company") or {}).get("display_name") or "").strip()
        for hit in seen.values()
    )
    titles.sort(key=lambda row: (row.get("count") is None, -(row.get("count") or 0)))
    counts = [row["count"] for row in titles if row.get("count") is not None]
    return {
        "status": "ok",
        "country": section["country"],
        "currency": section.get("currency", "USD"),
        "window_days": section.get("max_days_old", 30),
        "titles": titles,
        "unique_postings": len(seen),
        "total_postings": sum(counts) if counts else None,
        "median_salary": median(salaries),
        "top_companies": [name for name, _ in companies.most_common(10) if name],
    }


def expand_fixture(fixture):
    """Build one raw Adzuna payload per query from a compact fixture."""
    template = fixture.get("template") or {}
    results = template.get("results") or []
    payloads = {}
    for query, count in (fixture.get("counts") or {}).items():
        payload = dict(template)
        payload["count"] = count
        payload["results"] = [
            dict(hit, id="%s-%d" % (query.replace(" ", "-"), index))
            for index, hit in enumerate(results)
        ]
        payloads[query] = payload
    return payloads


def fetch(cfg, fixture=None):
    if fixture is not None:
        return parse(expand_fixture(fixture), cfg)

    section = cfg["adzuna"]
    app_id = (os.environ.get("ADZUNA_APP_ID") or "").strip()
    app_key = (os.environ.get("ADZUNA_APP_KEY") or "").strip()
    if not app_id or not app_key:
        return {
            "status": "skipped",
            "reason": "ADZUNA_APP_ID / ADZUNA_APP_KEY are not set",
            "country": section["country"],
            "titles": [],
            "unique_postings": None,
        }

    payloads = {}
    for query in section["queries"]:
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": str(section.get("results_per_page", 50)),
            "max_days_old": str(section.get("max_days_old", 30)),
            "what": query,
        }
        if section.get("where"):
            params["where"] = section["where"]
        url = BASE.format(country=section["country"]) + "?" + urllib.parse.urlencode(params)
        try:
            payloads[query] = http_json(url)
        except Exception as exc:  # noqa: BLE001 - keep other queries running
            log("adzuna: %r failed: %s" % (query, exc))

    if not payloads:
        return {"status": "error", "reason": "all Adzuna queries failed", "titles": []}
    return parse(payloads, cfg)
