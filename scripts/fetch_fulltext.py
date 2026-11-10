#!/usr/bin/env python3
"""Retrieve publisher full text for the DOIs listed in DOIs/DOIs.txt.

Why this script exists
----------------------
The MatProGPT repository does not redistribute publisher full texts. It ships
the DOI manifest (DOIs/DOIs.txt) and this retriever, so that anyone can rebuild
the corpus under their own text-mining agreement with each publisher and then
run the extraction pipeline unchanged.

    python scripts/fetch_fulltext.py --list DOIs/DOIs.txt --out data/cache
    python scripts/fetch_fulltext.py --limit 20 --dry-run        # smoke test

What it fetches and how
-----------------------
* Elsevier (DOI prefix 10.1016)  -> Elsevier Article Retrieval API, full-text XML.
  Needs a key from https://dev.elsevier.com and, for full text rather than
  abstracts, an institutional TDM entitlement.
* Everything else               -> an open-access copy via Unpaywall, if
  --unpaywall-email is given; otherwise recorded as "skipped".

Only stdlib is used, so the script runs without installing anything.

Output
------
data/cache/<publisher>/<doi_with_underscores>.xml|pdf
data/cache/fetch_manifest.csv     one row per DOI: status, bytes, url
data/cache/fetch_manifest.log     skipped / failed DOIs with the reason

Resumable: files already on disk are skipped unless --force is given.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ELSEVIER_API = "https://api.elsevier.com/content/article/doi/{doi}"
UNPAYWALL_API = "https://api.unpaywall.org/v2/{doi}?email={email}"
USER_AGENT = "MatProGPT-fulltext-fetcher/1.0 (academic text mining)"


# --------------------------------------------------------------------------- #
# DOI handling
# --------------------------------------------------------------------------- #
def normalise(doi: str) -> str:
    """DOIs/DOIs.txt stores DOIs with '/' replaced by '_'. Restore the real DOI."""
    doi = doi.strip()
    if not doi:
        return ""
    if doi.startswith("10."):
        first, _, rest = doi.partition("_")
        if rest:
            return f"{first}/{rest}"
    return doi


def prefix(doi: str) -> str:
    """Return the registrant prefix, e.g. '10.1016'."""
    head, _, _ = doi.partition("/")
    return head


def slug(doi: str) -> str:
    return doi.replace("/", "_")


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def http_get(url: str, headers: dict, timeout: int = 60) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={**headers, "User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() or b""
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, str(e).encode()


def get_with_retry(url: str, headers: dict, attempts: int = 4,
                   base_delay: float = 2.0) -> tuple[int, bytes]:
    delay = base_delay
    for i in range(attempts):
        status, body = http_get(url, headers)
        if status == 200:
            return status, body
        if status in (429, 500, 502, 503, 504) or status == 0:
            if i < attempts - 1:
                time.sleep(delay)
                delay *= 2
                continue
        return status, body
    return status, body


# --------------------------------------------------------------------------- #
# Publisher handlers
# --------------------------------------------------------------------------- #
def fetch_elsevier(doi: str, key: str, insttoken: str | None) -> tuple[int, bytes, str]:
    url = ELSEVIER_API.format(doi=urllib.parse.quote(doi, safe="/")) + "?httpAccept=text%2Fxml"
    headers = {"X-ELS-APIKey": key, "Accept": "text/xml"}
    if insttoken:
        headers["X-ELS-Insttoken"] = insttoken
    return (*get_with_retry(url, headers), url)


def fetch_oa(doi: str, email: str) -> tuple[int, bytes, str, str] | None:
    """Ask Unpaywall for a legal open-access copy. Returns (status, body, url, ext)."""
    status, body = get_with_retry(UNPAYWALL_API.format(
        doi=urllib.parse.quote(doi, safe="/"), email=urllib.parse.quote(email)), {})
    if status != 200:
        return None
    import json
    try:
        rec = json.loads(body)
    except json.JSONDecodeError:
        return None
    loc = rec.get("best_oa_location") or {}
    link = loc.get("url_for_pdf") or loc.get("url")
    if not link:
        return None
    ext = "pdf" if link.lower().endswith(".pdf") else "xml"
    st, data = get_with_retry(link, {})
    return st, data, link, ext


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", default="DOIs/DOIs.txt", help="DOI manifest (one per line)")
    ap.add_argument("--out", default="data/cache", help="output directory")
    ap.add_argument("--limit", type=int, default=0, help="stop after N DOIs (0 = all)")
    ap.add_argument("--offset", type=int, default=0, help="skip the first N DOIs")
    ap.add_argument("--delay", type=float, default=0.5, help="seconds between requests")
    ap.add_argument("--force", action="store_true", help="re-download existing files")
    ap.add_argument("--dry-run", action="store_true", help="list what would be fetched")
    ap.add_argument("--unpaywall-email", default=os.environ.get("UNPAYWALL_EMAIL", ""),
                    help="contact email for Unpaywall (required for non-Elsevier DOIs)")
    args = ap.parse_args(argv)

    src = Path(args.list)
    if not src.exists():
        print(f"error: {src} not found. Run from the repository root.", file=sys.stderr)
        return 2

    dois = [normalise(l) for l in src.read_text(encoding="utf-8").splitlines()]
    dois = [d for d in dois if d]
    if args.offset:
        dois = dois[args.offset:]
    if args.limit:
        dois = dois[: args.limit]

    key = os.environ.get("ELSEVIER_API_KEY", "")
    insttoken = os.environ.get("ELSEVIER_INSTTOKEN") or None
    if not key and not args.dry_run:
        print("error: set ELSEVIER_API_KEY (https://dev.elsevier.com), "
              "or use --dry-run.", file=sys.stderr)
        return 2
    if not args.unpaywall_email and not args.dry_run:
        print("note: --unpaywall-email not set; non-Elsevier DOIs will be skipped.",
              file=sys.stderr)

    out = Path(args.out)
    (out / "elsevier_xml").mkdir(parents=True, exist_ok=True)
    (out / "open_access").mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    counts = {"fetched": 0, "exists": 0, "skipped": 0, "failed": 0}

    for i, doi in enumerate(dois, 1):
        pfx = prefix(doi)
        tag = f"[{i}/{len(dois)}] {doi}"

        if args.dry_run:
            route = "elsevier" if pfx == "10.1016" else ("unpaywall" if args.unpaywall_email else "skip")
            print(f"{tag}  -> {route}")
            continue

        if pfx == "10.1016":
            dest = out / "elsevier_xml" / f"{slug(doi)}.xml"
            if dest.exists() and not args.force:
                rows.append({"doi": doi, "route": "elsevier", "status": "exists",
                             "bytes": dest.stat().st_size, "url": ""})
                counts["exists"] += 1
                continue
            status, body, url = fetch_elsevier(doi, key, insttoken)
            if status == 200 and len(body) > 2000:
                dest.write_bytes(body)
                rows.append({"doi": doi, "route": "elsevier", "status": "fetched",
                             "bytes": len(body), "url": url})
                counts["fetched"] += 1
                print(f"{tag}  fetched {len(body)//1024} kB")
            else:
                reason = f"HTTP {status}" if status else "network error"
                if status in (401, 403):
                    reason += " (no full-text TDM entitlement?)"
                if status == 404:
                    reason += " (DOI not in Elsevier's full-text index)"
                rows.append({"doi": doi, "route": "elsevier", "status": "failed",
                             "bytes": 0, "url": url})
                counts["failed"] += 1
                print(f"{tag}  FAILED {reason}", file=sys.stderr)

        elif args.unpaywall_email:
            dest_dir = out / "open_access"
            got = fetch_oa(doi, args.unpaywall_email)
            if not got:
                rows.append({"doi": doi, "route": "unpaywall", "status": "skipped",
                             "bytes": 0, "url": ""})
                counts["skipped"] += 1
                print(f"{tag}  no open-access copy")
            else:
                status, body, link, ext = got
                dest = dest_dir / f"{slug(doi)}.{ext}"
                if status == 200 and body:
                    if dest.exists() and not args.force:
                        rows.append({"doi": doi, "route": "unpaywall", "status": "exists",
                                     "bytes": dest.stat().st_size, "url": link})
                        counts["exists"] += 1
                    else:
                        dest.write_bytes(body)
                        rows.append({"doi": doi, "route": "unpaywall", "status": "fetched",
                                     "bytes": len(body), "url": link})
                        counts["fetched"] += 1
                        print(f"{tag}  fetched OA copy")
                else:
                    rows.append({"doi": doi, "route": "unpaywall", "status": "failed",
                                 "bytes": 0, "url": link})
                    counts["failed"] += 1

        else:
            rows.append({"doi": doi, "route": "none", "status": "skipped",
                         "bytes": 0, "url": ""})
            counts["skipped"] += 1

        time.sleep(args.delay)

    if not args.dry_run:
        manifest = out / "fetch_manifest.csv"
        with manifest.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["doi", "route", "status", "bytes", "url"])
            w.writeheader()
            w.writerows(rows)
        print("\n" + "  ".join(f"{k}={v}" for k, v in counts.items()))
        print(f"manifest: {manifest}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

