"""Render README.md and data/history.csv from stored daily snapshots."""
from __future__ import annotations

import csv
import os

from common import log

BEGIN = "<!-- BEGIN:GENERATED -->"
END = "<!-- END:GENERATED -->"

ACCENT = "#2da44e"
MUTED = "#57606a"
GRID = "#d0d7de"
FONT = "-apple-system,Segoe UI,Helvetica,Arial,sans-serif"

CURRENCY_SYMBOLS = {
    "USD": "$",
    "GBP": "\u00a3",
    "EUR": "\u20ac",
    "CAD": "C$",
    "AUD": "A$",
    "NZD": "NZ$",
    "INR": "\u20b9",
    "ZAR": "R",
    "SGD": "S$",
    "PLN": "z\u0142",
    "BRL": "R$",
    "CHF": "CHF ",
    "JPY": "\u00a5",
}

HISTORY_FIELDS = [
    "date",
    "adzuna_total_postings",
    "adzuna_unique_postings",
    "adzuna_median_salary",
    "hn_posts",
    "hn_remote_share",
    "bls_info_openings",
    "bls_info_hires",
    "bls_info_quits",
    "bls_info_layoffs",
    "bls_info_employment",
    "bls_info_share_pct",
]


# --------------------------------------------------------------------------- #
# formatting
# --------------------------------------------------------------------------- #
def esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def fmt_int(value):
    if value is None:
        return "\u2014"
    return "{:,}".format(int(round(float(value))))


def fmt_pct(fraction):
    if fraction is None:
        return "\u2014"
    return "{:.0f}%".format(float(fraction) * 100)


def fmt_money(value, currency):
    if value is None:
        return "\u2014"
    symbol = CURRENCY_SYMBOLS.get((currency or "").upper(), (currency or "") + " ")
    rounded = int(round(float(value) / 100.0)) * 100
    return "%s%s" % (symbol, "{:,}".format(rounded))


def fmt_k(value):
    if value is None:
        return "\u2014"
    value = float(value)
    if abs(value) >= 1000:
        return "%.1fM" % (value / 1000)
    return "%sk" % fmt_int(value)


def fmt_delta_k(value):
    if value is None:
        return "\u2014"
    sign = "+" if value > 0 else ("-" if value < 0 else "")
    return sign + fmt_k(abs(value))


def csv_number(value):
    """Keep the CSV readable in a spreadsheet: 116.0 -> 116, 0.556 -> 0.556."""
    if value is None or value == "":
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return value
    if number.is_integer():
        return int(number)
    return round(number, 3)


# --------------------------------------------------------------------------- #
# charts (inline SVG: small, diffable, renders on GitHub)
# --------------------------------------------------------------------------- #
def _svg_open(width, height):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d" font-family="%s">' % (width, height, width, height, FONT)
    )


def svg_line(points, width=760, height=200, color=ACCENT, suffix=""):
    if len(points) < 2:
        return ""
    left, right, top, bottom = 58, 18, 16, 26
    plot_w = width - left - right
    plot_h = height - top - bottom

    values = [float(value) for _, value in points]
    low, high = min(values), max(values)
    if high == low:
        high = low + max(1.0, abs(high) * 0.1)
    padding = (high - low) * 0.15
    low -= padding
    high += padding

    def x_of(index):
        return left + (plot_w * index / (len(points) - 1))

    def y_of(value):
        return top + plot_h * (1 - (float(value) - low) / (high - low))

    parts = [_svg_open(width, height)]
    for fraction in (0.0, 0.5, 1.0):
        level = low + (high - low) * fraction
        y = y_of(level)
        parts.append(
            '<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>'
            % (left, y, left + plot_w, y, GRID)
        )
        parts.append(
            '<text x="%d" y="%.1f" font-size="11" fill="%s" text-anchor="end">%s%s</text>'
            % (left - 6, y + 3.5, MUTED, fmt_int(level), suffix)
        )

    coords = " ".join(
        "%.1f,%.1f" % (x_of(index), y_of(value)) for index, (_, value) in enumerate(points)
    )
    parts.append(
        '<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
        'stroke-linejoin="round" stroke-linecap="round"/>' % (coords, color)
    )
    if len(points) <= 45:
        for index, (_, value) in enumerate(points):
            parts.append(
                '<circle cx="%.1f" cy="%.1f" r="2.6" fill="%s"/>'
                % (x_of(index), y_of(value), color)
            )

    parts.append(
        '<text x="%d" y="%d" font-size="11" fill="%s">%s</text>'
        % (left, height - 7, MUTED, esc(points[0][0]))
    )
    parts.append(
        '<text x="%d" y="%d" font-size="11" fill="%s" text-anchor="end">%s</text>'
        % (left + plot_w, height - 7, MUTED, esc(points[-1][0]))
    )
    parts.append("</svg>")
    return "".join(parts)


def svg_bars(items, width=760, bar_height=24, gap=9, color=ACCENT, suffix=""):
    rows = [(label, value) for label, value in items if value is not None]
    if not rows:
        return ""
    label_w, value_w, top = 220, 76, 6
    plot_w = width - label_w - value_w
    height = top + len(rows) * (bar_height + gap) - gap + 10
    max_value = max(float(value) for _, value in rows) or 1.0

    parts = [_svg_open(width, height)]
    for index, (label, value) in enumerate(rows):
        y = top + index * (bar_height + gap)
        bar_w = max(3.0, plot_w * (float(value) / max_value))
        short = label if len(label) <= 30 else label[:29] + "\u2026"
        parts.append(
            '<text x="0" y="%.1f" font-size="12" fill="%s">%s</text>'
            % (y + bar_height * 0.7, MUTED, esc(short))
        )
        parts.append(
            '<rect x="%d" y="%.1f" width="%.1f" height="%d" rx="3" fill="%s" fill-opacity="0.85"/>'
            % (label_w, y, bar_w, bar_height, color)
        )
        parts.append(
            '<text x="%.1f" y="%.1f" font-size="12" fill="%s">%s%s</text>'
            % (label_w + bar_w + 7, y + bar_height * 0.7, MUTED, fmt_int(value), suffix)
        )
    parts.append("</svg>")
    return "".join(parts)


# --------------------------------------------------------------------------- #
# README sections
# --------------------------------------------------------------------------- #
def _adzuna_block(snapshots, latest):
    data = latest.get("adzuna") or {}
    out = ["### IT postings by title", ""]
    if data.get("status") != "ok":
        reason = data.get("reason") or "source unavailable"
        out.append(
            "> **Adzuna section skipped** \u2014 %s. Add `ADZUNA_APP_ID` and "
            "`ADZUNA_APP_KEY` repository secrets to populate it." % esc(reason)
        )
        out.append("")
        return out

    country = (data.get("country") or "us").upper()
    currency = data.get("currency") or "USD"
    window = data.get("window_days") or 30
    out.append(
        "_%s \u00b7 postings from the last %d days \u00b7 %s unique postings in the sample_"
        % (country, window, fmt_int(data.get("unique_postings")))
    )
    out.append("")
    out.append("| Title | Postings | Median salary | Remote | Top employers |")
    out.append("| --- | ---: | ---: | ---: | --- |")
    for row in data.get("titles") or []:
        if row.get("count") is None:
            out.append(
                "| %s | \u2014 | \u2014 | \u2014 | _query failed_ |" % esc(row.get("query"))
            )
            continue
        employers = ", ".join(row.get("top_companies") or []) or "\u2014"
        salary = fmt_money(row.get("median_salary"), currency)
        samples = row.get("salary_samples")
        if salary != "\u2014" and samples:
            # Show the sample size: some queries publish salaries on only a handful of posts.
            salary = "%s (n=%d)" % (salary, samples)
        out.append(
            "| %s | %s | %s | %s | %s |"
            % (
                esc(row.get("query")),
                fmt_int(row.get("count")),
                salary,
                fmt_pct(row.get("remote_share")),
                esc(employers),
            )
        )
    out.append("")
    out.append(
        svg_bars(
            [(str(row.get("query")), row.get("count")) for row in data.get("titles") or []]
        )
    )
    out.append("")
    out.append(
        "_Each query is an independent Adzuna search, so rows overlap and do not add up._"
    )
    out.append("")

    trend = []
    for snap in snapshots:
        adz = snap.get("adzuna") or {}
        if adz.get("status") == "ok" and adz.get("total_postings") is not None:
            trend.append((snap.get("date") or "", adz["total_postings"]))
    if len(trend) >= 2:
        out.append("#### Postings matching the queries, per run")
        out.append("")
        out.append(svg_line(trend, color=ACCENT))
        out.append("")
        out.append(
            "_The searches overlap, so this total double-counts jobs matching more than one title._"
        )
        out.append("")
    elif trend:
        out.append("_Trend chart appears once there are two snapshots._")
        out.append("")
    return out


def _hn_block(latest):
    data = latest.get("hn") or {}
    out = ["### What Hacker News is hiring for", ""]
    if data.get("status") != "ok":
        reason = data.get("reason") or "source unavailable"
        out.append("> **Hacker News section skipped** \u2014 %s" % esc(reason))
        out.append("")
        return out

    title = data.get("story_title") or "Who is hiring?"
    out.append(
        "_[%s](%s) \u00b7 %s comments indexed \u00b7 %s substantive posts \u00b7 %s mention remote_"
        % (
            esc(title),
            data.get("thread_url") or "",
            fmt_int(data.get("comments_indexed")),
            fmt_int(data.get("posts")),
            fmt_pct(data.get("remote_share")),
        )
    )
    out.append("")

    tracks = [(name, count) for name, count in (data.get("tracks") or {}).items() if count]
    if tracks:
        out.append("| Track | Posts mentioning it |")
        out.append("| --- | ---: |")
        for name, count in tracks:
            out.append("| %s | %s |" % (esc(name), fmt_int(count)))
        out.append("")
        out.append(svg_bars(tracks, bar_height=22))
        out.append("")

    mentions = list((data.get("mentions") or {}).items())
    if mentions:
        rendered = " \u00b7 ".join("`%s` %s" % (esc(word), fmt_int(count)) for word, count in mentions)
        out.append("Most-mentioned tools and platforms: %s" % rendered)
        out.append("")
    return out


def _bls_block(latest):
    data = latest.get("bls") or {}
    out = ["### US information sector (BLS)", ""]
    if data.get("status") != "ok":
        reason = data.get("reason") or "source unavailable"
        out.append("> **BLS section skipped** \u2014 %s" % esc(reason))
        out.append("")
        return out

    series = data.get("series") or {}
    period = data.get("latest_period") or ""
    out.append("_Monthly, seasonally adjusted \u00b7 reference month %s_" % esc(period))
    out.append("")
    out.append("| Series | Latest | MoM | YoY |")
    out.append("| --- | ---: | ---: | ---: |")
    order = [
        "info_openings",
        "info_hires",
        "info_quits",
        "info_layoffs",
        "info_employment",
        "all_openings",
    ]
    for name in order:
        entry = series.get(name)
        if not entry:
            continue
        out.append(
            "| %s | %s | %s | %s |"
            % (
                esc(entry.get("label")),
                fmt_k(entry.get("value")),
                fmt_delta_k(entry.get("mom_change")),
                fmt_delta_k(entry.get("yoy_change")),
            )
        )
    out.append("")

    share = data.get("info_share_of_openings")
    if share is not None:
        out.append(
            "Information-sector postings are **%.1f%%** of all US job openings." % share
        )
        out.append("")

    history = (series.get("info_openings") or {}).get("history") or []
    points = [(row.get("period") or "", row.get("value")) for row in history if row.get("value") is not None]
    if len(points) >= 2:
        out.append("#### Information-sector job openings, last %d months" % len(points))
        out.append("")
        out.append(svg_line(points, height=180, suffix="k"))
        out.append("")
    return out


def _history_block(snapshots):
    recent = snapshots[-10:]
    if len(recent) < 2:
        return []
    out = ["### Recent runs", ""]
    out.append("| Date | Matching postings | HN posts | Info openings |")
    out.append("| --- | ---: | ---: | ---: |")
    for snap in reversed(recent):
        adz = snap.get("adzuna") or {}
        hn = snap.get("hn") or {}
        bls = (snap.get("bls") or {}).get("series") or {}
        openings = (bls.get("info_openings") or {}).get("value")
        out.append(
            "| %s | %s | %s | %s |"
            % (
                esc(snap.get("date")),
                fmt_int(adz.get("total_postings")) if adz.get("status") == "ok" else "\u2014",
                fmt_int(hn.get("posts")) if hn.get("status") == "ok" else "\u2014",
                fmt_k(openings),
            )
        )
    out.append("")
    out.append("Full time series: [`data/history.csv`](data/history.csv)")
    out.append("")
    return out


def build_block(snapshots):
    latest = snapshots[-1]
    count = len(snapshots)
    out = [
        "_Updated **%s** \u00b7 %d snapshot%s collected \u00b7 sources: Adzuna \u00b7 Hacker News \u00b7 US BLS_"
        % (latest.get("date") or "unknown", count, "" if count == 1 else "s"),
        "",
    ]
    out.extend(_adzuna_block(snapshots, latest))
    out.extend(_hn_block(latest))
    out.extend(_bls_block(latest))
    out.extend(_history_block(snapshots))
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# outputs
# --------------------------------------------------------------------------- #
def write_history_csv(data_dir, snapshots):
    path = os.path.join(data_dir, "history.csv")
    os.makedirs(data_dir, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HISTORY_FIELDS)
        writer.writeheader()
        for snap in snapshots:
            adz = snap.get("adzuna") or {}
            hn = snap.get("hn") or {}
            bls = snap.get("bls") or {}
            series = bls.get("series") or {}

            def value_of(name):
                return (series.get(name) or {}).get("value")

            writer.writerow(
                {
                    "date": snap.get("date") or "",
                    "adzuna_total_postings": csv_number(
                        adz.get("total_postings") if adz.get("status") == "ok" else ""
                    ),
                    "adzuna_unique_postings": csv_number(
                        adz.get("unique_postings") if adz.get("status") == "ok" else ""
                    ),
                    "adzuna_median_salary": csv_number(
                        adz.get("median_salary") if adz.get("status") == "ok" else ""
                    ),
                    "hn_posts": csv_number(hn.get("posts") if hn.get("status") == "ok" else ""),
                    "hn_remote_share": csv_number(
                        hn.get("remote_share") if hn.get("status") == "ok" else ""
                    ),
                    "bls_info_openings": csv_number(value_of("info_openings")),
                    "bls_info_hires": csv_number(value_of("info_hires")),
                    "bls_info_quits": csv_number(value_of("info_quits")),
                    "bls_info_layoffs": csv_number(value_of("info_layoffs")),
                    "bls_info_employment": csv_number(value_of("info_employment")),
                    "bls_info_share_pct": csv_number(bls.get("info_share_of_openings")),
                }
            )
    return path


def render_readme(readme_path, block):
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as handle:
            template = handle.read()
    else:
        template = "# IT Job Market Tracker\n"

    if BEGIN in template and END in template:
        head, rest = template.split(BEGIN, 1)
        _, tail = rest.split(END, 1)
        content = head + BEGIN + "\n\n" + block + "\n\n" + END + tail
    else:
        content = template.rstrip() + "\n\n" + BEGIN + "\n\n" + block + "\n\n" + END + "\n"

    with open(readme_path, "w", encoding="utf-8") as handle:
        handle.write(content)
    return readme_path


def render_all(data_dir, readme_path, snapshots):
    if not snapshots:
        log("render: nothing to render")
        return
    csv_path = write_history_csv(data_dir, snapshots)
    render_readme(readme_path, build_block(snapshots))
    log("render: wrote %s and %s" % (os.path.basename(csv_path), readme_path))
