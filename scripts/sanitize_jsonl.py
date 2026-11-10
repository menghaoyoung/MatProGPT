#!/usr/bin/env python3
"""Remove publisher full text from shipped artefacts before they are published.

Two artefacts in the MatProGPT release embed verbatim publisher text:

  finetune/property_inclusion_test.jsonl   the `user` message of each of the 184
                                          records is a whole abstract/paragraph
                                          (median 1,774 characters)
  extracted_results_audited.csv           `related_paragraph` holds the source
                                          paragraph (median 2,218 characters,
                                          longest 10,557)

Redistributing those paragraphs is outside a text-mining agreement, even when
the *extracted values* are freely licensable. This script replaces each long
passage with a fingerprint plus a short evidence span, and keeps the record
answerable: the paragraph can be re-fetched from the DOI with
scripts/fetch_fulltext.py.

Typical use
-----------
    # 1. see what would change, change nothing
    python scripts/sanitize_jsonl.py --jsonl finetune/property_inclusion_test.jsonl --check

    # 2. write sanitised copies next to the originals
    python scripts/sanitize_jsonl.py \
        --jsonl finetune/property_inclusion_test.jsonl \
        --audit-csv extracted_results_audited.csv \
        --max-chars 200

    # 3. review, then replace
    mv finetune/property_inclusion_test.sanitized.jsonl finetune/property_inclusion_test.jsonl
    mv extracted_results_audited.sanitized.csv extracted_results_audited.csv

Resolving DOIs
--------------
A fingerprint alone cannot tell a reader which paper a paragraph came from, so
the script accepts a mapping:

    --map paragraph_index.csv      # columns: sha1,doi[,paragraph_id]

`sha1` is the first 16 hex characters of SHA-1 over the paragraph text exactly
as stored. Without a map the `doi` field is left empty and the record is
reported as unresolved -- that is a warning, not an error, but a submission
copy should have no unresolved records.

Only the Python standard library is used.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

TEXT_KEYS = ("content", "text", "paragraph", "related_paragraph", "input")
ELLIPSIS = " […]"


# --------------------------------------------------------------------------- #
def fingerprint(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def clip(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit].rstrip() + ELLIPSIS


def load_map(path: str | None) -> dict[str, dict]:
    if not path:
        return {}
    m: dict[str, dict] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = (row.get("sha1") or "").strip()
            if key:
                m[key] = row
    return m


# --------------------------------------------------------------------------- #
def sanitize_jsonl(src: Path, dst: Path, limit: int, index: dict[str, dict],
                   check_only: bool, roles: tuple[str, ...] = ("user",)) -> dict:
    stats = {"records": 0, "passages": 0, "unresolved": 0,
             "longest_before": 0, "longest_after": 0}
    out_lines: list[str] = []

    for raw in src.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        rec = json.loads(raw)
        stats["records"] += 1

        msgs = rec.get("messages")
        if isinstance(msgs, list):
            for m in msgs:
                body = m.get("content")
                if m.get("role") not in roles:
                    continue          # keep the system prompt and the label intact
                if not isinstance(body, str) or len(body) <= limit:
                    continue
                stats["passages"] += 1
                stats["longest_before"] = max(stats["longest_before"], len(body))
                fp = fingerprint(body)
                meta = index.get(fp, {})
                doi = (meta.get("doi") or "").strip()
                if not doi:
                    stats["unresolved"] += 1
                span = clip(body, limit)
                stats["longest_after"] = max(stats["longest_after"], len(span))
                rec.setdefault("doi", doi)
                rec.setdefault("paragraph_sha1", fp)
                if meta.get("paragraph_id"):
                    rec.setdefault("paragraph_id", meta["paragraph_id"])
                m["content"] = (
                    f"[paragraph text withheld; source doi={doi or 'UNRESOLVED'}, "
                    f"paragraph_sha1={fp}. First {limit} characters: {span}]"
                )
        else:
            # Fallback: any long string field in an unknown schema
            for key, val in list(rec.items()):
                if key in TEXT_KEYS and isinstance(val, str) and len(val) > limit:
                    stats["passages"] += 1
                    stats["longest_before"] = max(stats["longest_before"], len(val))
                    fp = fingerprint(val)
                    meta = index.get(fp, {})
                    if not meta.get("doi"):
                        stats["unresolved"] += 1
                    rec[key] = clip(val, limit)
                    rec["paragraph_sha1"] = fp

        out_lines.append(json.dumps(rec, ensure_ascii=False))

    if not check_only:
        dst.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return stats



def read_csv_rows(src: Path) -> tuple[list[str], list[dict]]:
    """Read a CSV, tolerating a UTF-8 BOM in the header (common from Excel)."""
    with src.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        fields = [f.lstrip("\ufeff") for f in (reader.fieldnames or [])]
        rows = []
        for row in reader:
            rows.append({(k or "").lstrip("\ufeff"): v for k, v in row.items()})
    return fields, rows


def sanitize_audit_csv(src: Path, dst: Path, limit: int, index: dict[str, dict],
                       check_only: bool) -> dict:
    stats = {"rows": 0, "passages": 0, "unresolved": 0,
             "longest_before": 0, "longest_after": 0}
    fields, rows = read_csv_rows(src)
    fieldnames = [f for f in fields if f != "related_paragraph_sha1"]
    fields = list(fieldnames)
    col = next((c for c in fields if c in TEXT_KEYS), None)
    if col is None:
        raise SystemExit(f"error: no paragraph column in {src}; looked for {TEXT_KEYS}")
    if "related_paragraph_sha1" not in fields:
        fields.append("related_paragraph_sha1")

    for row in rows:
        stats["rows"] += 1
        body = row.get(col) or ""
        if not body.strip():
            row["related_paragraph_sha1"] = ""
            continue
        fp = fingerprint(body)
        row["related_paragraph_sha1"] = fp          # always, for traceability
        meta = index.get(fp, {})
        if not (meta.get("doi") or row.get("doi")):
            stats["unresolved"] += 1
        if len(body) <= limit:
            continue                                 # short: nothing to withhold
        stats["passages"] += 1
        stats["longest_before"] = max(stats["longest_before"], len(body))
        row[col] = clip(body, limit)
        stats["longest_after"] = max(stats["longest_after"], len(row[col]))

    if not check_only:
        with dst.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
    return stats


# --------------------------------------------------------------------------- #
def report(name: str, st: dict, check_only: bool) -> int:
    print(f"\n{name}")
    print(f"  records        : {st.get('records', st.get('rows', 0))}")
    print(f"  passages >= limit: {st['passages']}")
    print(f"  longest before : {st['longest_before']} chars")
    print(f"  longest kept   : {st['longest_after']} chars")
    print(f"  unresolved doi : {st['unresolved']}")
    if check_only:
        print("  mode           : check only, nothing written")
    if st["unresolved"]:
        print("  WARNING: unresolved records have no DOI; supply --map so a reader "
              "can re-fetch the paragraph.")
    return 1 if st["unresolved"] else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jsonl", action="append", default=[],
                    help="JSONL file to sanitise (repeatable)")
    ap.add_argument("--audit-csv", action="append", default=[],
                    help="audit CSV with a verbatim paragraph column (repeatable)")
    ap.add_argument("--max-chars", type=int, default=200,
                    help="characters of evidence to keep (default 200)")
    ap.add_argument("--map", default=None,
                    help="CSV with columns sha1,doi[,paragraph_id]")
    ap.add_argument("--roles", default="user",
                    help="message roles to sanitise, comma separated (default: user)")
    ap.add_argument("--check", action="store_true",
                    help="report only, write nothing")
    args = ap.parse_args(argv)

    if not args.jsonl and not args.audit_csv:
        ap.error("give at least one --jsonl or --audit-csv")

    roles = tuple(r.strip() for r in args.roles.split(",") if r.strip())
    index = load_map(args.map)
    if args.map:
        print(f"loaded {len(index)} fingerprint(s) from {args.map}")
    elif not args.check:
        print("note: no --map given; DOIs will be left blank and reported as unresolved.")

    worst = 0
    for p in map(Path, args.jsonl):
        dst = p.with_suffix(".sanitized.jsonl")
        st = sanitize_jsonl(p, dst, args.max_chars, index, args.check, roles)
        worst |= report(f"{p} -> {dst.name}", st, args.check)
    for p in map(Path, args.audit_csv):
        dst = p.with_suffix(".sanitized.csv")
        st = sanitize_audit_csv(p, dst, args.max_chars, index, args.check)
        worst |= report(f"{p} -> {dst.name}", st, args.check)

    print()
    return worst


if __name__ == "__main__":
    raise SystemExit(main())

