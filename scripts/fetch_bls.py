"""BLS: monthly information-sector labour market context (JOLTS + CES)."""
from __future__ import annotations

import os
import time

from common import http_json, log

V1_URL = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
V2_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
MAX_HISTORY = 24


def _rows_of(series):
    rows = []
    for point in series.get("data") or []:
        period = point.get("period") or ""
        if not period.startswith("M") or period == "M13":
            continue
        try:
            value = float(point.get("value"))
        except (TypeError, ValueError):
            continue
        rows.append(
            {
                "year": int(point.get("year")),
                "month": int(period[1:]),
                "value": value,
                "period_name": point.get("periodName") or "",
            }
        )
    rows.sort(key=lambda row: (row["year"], row["month"]))
    return rows


def _year_ago(rows, latest):
    for row in rows:
        if row["year"] == latest["year"] - 1 and row["month"] == latest["month"]:
            return row
    return None


def parse(response, cfg):
    section = cfg["bls"]
    names_by_id = {
        (spec.get("id") or "").strip(): name for name, spec in section["series"].items()
    }

    status = (response.get("status") or "").upper()
    if status != "REQUEST_SUCCEEDED":
        message = response.get("message") or ["unknown BLS error"]
        return {
            "status": "error",
            "reason": "; ".join(str(part) for part in message),
            "series": {},
        }

    out = {}
    for series in (response.get("Results") or {}).get("series") or []:
        series_id = (series.get("seriesID") or series.get("seriesid") or "").strip()
        name = names_by_id.get(series_id)
        if not name:
            continue
        rows = _rows_of(series)
        if not rows:
            continue
        latest = rows[-1]
        previous = rows[-2] if len(rows) > 1 else None
        last_year = _year_ago(rows, latest)
        spec = section["series"][name]
        out[name] = {
            "id": series_id,
            "label": spec.get("label", name),
            "unit": spec.get("unit", "thousands"),
            "value": latest["value"],
            "period": "%04d-%02d" % (latest["year"], latest["month"]),
            "period_label": latest["period_name"],
            "previous": previous["value"] if previous else None,
            "year_ago": last_year["value"] if last_year else None,
            "mom_change": (latest["value"] - previous["value"]) if previous else None,
            "yoy_change": (latest["value"] - last_year["value"]) if last_year else None,
            "history": [
                {"period": "%04d-%02d" % (row["year"], row["month"]), "value": row["value"]}
                for row in rows[-MAX_HISTORY:]
            ],
        }

    openings = (out.get("info_openings") or {}).get("value")
    all_openings = (out.get("all_openings") or {}).get("value")
    share = round(openings / all_openings * 100, 1) if openings and all_openings else None
    latest_period = out.get("info_openings", {}).get("period")

    payload = {
        "status": "ok" if out else "error",
        "series": out,
        "info_share_of_openings": share,
        "latest_period": latest_period,
    }
    missing = [name for name in section["series"] if name not in out]
    if missing:
        log("bls: series not returned: %s" % ", ".join(missing))
        payload["missing_series"] = missing
    if not out:
        payload["reason"] = "BLS returned no matching series"
    return payload


def fetch(cfg, fixture=None):
    if fixture is not None:
        return parse(fixture, cfg)

    section = cfg["bls"]
    now = time.gmtime()
    payload = {
        "seriesid": [spec["id"] for spec in section["series"].values()],
        "startyear": str(now.tm_year - 1),
        "endyear": str(now.tm_year),
    }
    api_key = (os.environ.get("BLS_API_KEY") or "").strip()
    if api_key:
        payload["registrationkey"] = api_key
        url = V2_URL
    else:
        url = V1_URL
    return parse(http_json(url, data=payload), cfg)
