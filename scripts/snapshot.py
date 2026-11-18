"""Collect one snapshot of the IT job market and refresh the README.

Usage:
    python scripts/snapshot.py                  # live fetch + commit-ready files
    python scripts/snapshot.py --date 2026-11-18
    python scripts/snapshot.py --fixtures tests/fixtures --data-dir .tmp/data --readme .tmp/README.md

Exit code is 0 when at least one source succeeded, 1 when every source failed.
"""
from __future__ import annotations

import argparse
import os
import traceback

import fetch_adzuna
import fetch_bls
import fetch_hn
import render
from common import (
    load_config,
    load_snapshots,
    log,
    read_json,
    utc_stamp,
    utc_today,
    write_json,
)

SOURCES = ("adzuna", "hn", "bls")
FETCHERS = {"adzuna": fetch_adzuna.fetch, "hn": fetch_hn.fetch, "bls": fetch_bls.fetch}


def _fixture(folder, name):
    if not folder:
        return None
    path = os.path.join(folder, name + ".json")
    return read_json(path) if os.path.exists(path) else None


def collect(cfg, fixtures=None):
    snapshot = {}
    for name in SOURCES:
        try:
            data = FETCHERS[name](cfg, _fixture(fixtures, name))
        except Exception as exc:  # noqa: BLE001 - one bad source must not stop the run
            log("%s: unhandled error: %s" % (name, exc))
            traceback.print_exc()
            data = {"status": "error", "reason": "%s: %s" % (type(exc).__name__, exc)}
        detail = " - %s" % data["reason"] if data.get("reason") else ""
        log("%s: %s%s" % (name, data.get("status"), detail))
        snapshot[name] = data
    return snapshot


def _write_step_summary(snapshot):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    adz = snapshot.get("adzuna") or {}
    hn = snapshot.get("hn") or {}
    bls = snapshot.get("bls") or {}
    series = bls.get("series") or {}
    headlines = [
        (
            "Adzuna",
            adz.get("status"),
            "%s unique postings sampled"
            % render.fmt_int(adz.get("unique_postings"))
            if adz.get("status") == "ok"
            else adz.get("reason", ""),
        ),
        (
            "Hacker News",
            hn.get("status"),
            "%s posts, %s remote"
            % (render.fmt_int(hn.get("posts")), render.fmt_pct(hn.get("remote_share")))
            if hn.get("status") == "ok"
            else hn.get("reason", ""),
        ),
        (
            "BLS",
            bls.get("status"),
            "%s info openings (%s)"
            % (
                render.fmt_k((series.get("info_openings") or {}).get("value")),
                (series.get("info_openings") or {}).get("period", ""),
            )
            if bls.get("status") == "ok"
            else bls.get("reason", ""),
        ),
    ]
    lines = ["## IT job-market snapshot - %s" % snapshot.get("date"), ""]
    lines.append("| Source | Status | Headline |")
    lines.append("| --- | --- | --- |")
    for name, status, headline in headlines:
        lines.append("| %s | %s | %s |" % (name, status, headline))
    lines.append("")
    try:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
    except OSError as exc:
        log("could not write step summary: %s" % exc)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Collect one daily snapshot.")
    parser.add_argument("--date", default=None, help="snapshot date, default today (UTC)")
    parser.add_argument("--fixtures", default=None, help="directory of raw API fixtures")
    parser.add_argument("--data-dir", default=None, help="output directory, default data/")
    parser.add_argument("--readme", default=None, help="README to refresh, default ./README.md")
    parser.add_argument("--config", default=None, help="path to config.json")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    date = args.date or utc_today()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = args.data_dir or os.path.join(root, "data")
    readme_path = args.readme or os.path.join(root, "README.md")

    snapshot = collect(cfg, args.fixtures)
    snapshot["date"] = date
    snapshot["collected_at"] = utc_stamp()

    path = os.path.join(data_dir, "%s.json" % date)
    write_json(path, snapshot)
    log("wrote %s" % path)

    snapshots = load_snapshots(data_dir)
    render.render_all(data_dir, readme_path, snapshots)
    _write_step_summary(snapshot)

    failed = [name for name in SOURCES if (snapshot.get(name) or {}).get("status") == "error"]
    skipped = [name for name in SOURCES if (snapshot.get(name) or {}).get("status") == "skipped"]
    succeeded = [name for name in SOURCES if (snapshot.get(name) or {}).get("status") == "ok"]
    if failed:
        log("failed sources: %s" % ", ".join(failed))
    if skipped:
        log("skipped sources: %s" % ", ".join(skipped))
    if not succeeded:
        log("no source produced data - refusing to report success")
        return 1
    log("snapshot complete for %s" % date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
