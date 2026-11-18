"""Shared helpers: config loading, HTTP, dates, atomic JSON IO."""
from __future__ import annotations

import glob
import json
import os
import statistics
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config.json")
USER_AGENT = "it-job-trends/1.0 (+https://github.com/GideonNkrumah/it-job-trends)"


def log(message):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), message), flush=True)


def load_dotenv(path=None):
    """Populate os.environ from a .env file (never overriding real env vars)."""
    path = path or os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            name = name.strip()
            if name and name not in os.environ:
                os.environ[name] = value.strip().strip('"').strip("'")


def load_config(path=None):
    load_dotenv()
    with open(path or CONFIG_PATH, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def http_json(url, data=None, headers=None, timeout=45, retries=3):
    """GET (or POST when ``data`` is given) and decode JSON, with retries."""
    request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        request_headers.update(headers)

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    last_error = "unknown error"
    for attempt in range(1, retries + 1):
        request = urllib.request.Request(url, data=body, headers=request_headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read()[:300].decode("utf-8", "replace")
            except Exception:
                pass
            last_error = "HTTP %s %s" % (exc.code, detail.strip())
            if exc.code in (400, 401, 403, 404):
                break
        except Exception as exc:  # noqa: BLE001 - reported to the caller
            last_error = "%s: %s" % (type(exc).__name__, exc)
        if attempt < retries:
            time.sleep(2 * attempt)
    raise RuntimeError(last_error)


def utc_today():
    return time.strftime("%Y-%m-%d", time.gmtime())


def utc_stamp():
    return time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())


def write_json(path, payload):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def read_json(path):
    # utf-8-sig tolerates a BOM, which Windows editors like to add.
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def load_snapshots(data_dir):
    snapshots = []
    for path in sorted(glob.glob(os.path.join(data_dir, "20*.json"))):
        try:
            snapshots.append(read_json(path))
        except Exception as exc:  # noqa: BLE001 - never let one bad file break a run
            log("skipping unreadable snapshot %s: %s" % (os.path.basename(path), exc))
    return snapshots


def median(values):
    usable = [value for value in values if value is not None]
    if not usable:
        return None
    return float(statistics.median(usable))
