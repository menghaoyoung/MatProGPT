# Cleaning the MatProGPT repository before submission

Target: `github.com/menghaoyoung/MatProGPT` — public, 10 commits, one branch,
no forks, no tags, no Software Heritage snapshot. That makes the clean rebuild
below zero-risk for external copies.

**Problem being fixed.** Eight files in the tree are publisher full text
(`elsevier_text/` 6 files, `elsevier_xml/` 1, `elsevier_json/` 1), and
`finetune/property_inclusion_test.jsonl` embeds 184 verbatim paragraphs.
`git rm` alone leaves all of it in history. There is also no LICENSE, so the
code is currently unlicensed, and the README claims MIT without a licence file.

---

## 0. Prepare (5 min)

```bash
git clone https://github.com/menghaoyoung/MatProGPT.git matprogpt-clean
cd matprogpt-clean
```

Copy the four items from this bundle into the clone:

```
LICENSE
.gitignore
scripts/fetch_fulltext.py
scripts/sanitize_jsonl.py
```

Apply `README-patch.md` (four edits).

---

## 1. Sanitise the training file (30–60 min, the slow step)

The 184 `user` messages are whole paragraphs. Replace them with a DOI, a
SHA-1 fingerprint and a 200-character evidence span:

```bash
python scripts/sanitize_jsonl.py \
    --jsonl finetune/property_inclusion_test.jsonl \
    --check                       # first look: expect ~184 passages, ~3.7k chars max
```

`--check` reports how many records have no DOI. If a `sha1,doi,paragraph_id`
mapping exists in your corpus index, pass it with `--map index.csv`; otherwise
DOI lookups are left blank. A submission copy should resolve every record:

```bash
python scripts/sanitize_jsonl.py \
    --jsonl finetune/property_inclusion_test.jsonl \
    --map paragraph_index.csv \
    --max-chars 200

mv finetune/property_inclusion_test.sanitized.jsonl \
   finetune/property_inclusion_test.jsonl
```

Do the same for the audit CSV before you upload it to Zenodo (it has the same
problem: `related_paragraph`, median 2,218 characters, longest 10,557):

```bash
python scripts/sanitize_jsonl.py --audit-csv extracted_results_audited.csv --max-chars 200
```

---

## 2. Remove the full texts (5 min)

```bash
git rm -r elsevier_text elsevier_xml elsevier_json
find . -name '__pycache__' -type d -prune -exec git rm -r --cached {} +
find . -name '*.pyc' -delete
printf 'data/cache/\n' >> .gitignore       # already in the shipped .gitignore
```

`DOIs/DOIs.txt` stays: 47,022 identifiers, no copyrightable text, and it is the
manifest the paper's "47,000 screened" figure refers to.

---

## 3. Rebuild the history (10 min)

Because there are no forks, tags or external mirrors, rebuild rather than
rewrite — that guarantees no blob survives in any commit:

```bash
git add -A
git commit -m "Remove publisher full text; add MIT licence, DOI manifest and retrieval tooling"
```

Then, on GitHub:

1. **Settings → Rename** the old repository to `MatProGPT-archive`, or delete it.
2. Create a new **public** repository named `MatProGPT` (same URL, so links in
   the manuscript keep working).
3. ```bash
   git remote set-url origin https://github.com/menghaoyoung/MatProGPT.git
   git push -u origin main
   ```

Alternative, if you must keep the commit history: `git filter-repo` with
`--invert-paths --path elsevier_text/ --path elsevier_xml/ --path elsevier_json/
--path-glob '*/__pycache__/*'`, then `git push --force --mirror`. Old blobs stay
reachable by SHA until GitHub garbage-collects, and only Support can force that,
which is why the rebuild is preferred.

---

## 4. Tag and archive (10 min)

```bash
git tag -a v1.0.0 -m "MatProGPT v1.0.0"
git push origin v1.0.0
```

Then enable the repository in Zenodo (Zenodo → Settings → GitHub → *Sync now*),
which mints a **code DOI**. Put that DOI in the manuscript's Code Availability
alongside the data DOI.

---

## 5. Verify before you call it done

```bash
# no full text in the tree
find . -name '*.xml' -o -name '*.text' -o -name '*.json' | grep -v data/cache   # expect: nothing

# no full text in any commit
git log --all --diff-filter=A --name-only --pretty=format: | sort -u | grep -E 'elsevier_(text|xml|json)/'   # expect: nothing

# licence is recognised by GitHub
curl -s https://api.github.com/repos/menghaoyoung/MatProGPT | grep -A2 '"license"'   # expect: "spdx_id": "MIT"

# no long verbatim passage left
python scripts/sanitize_jsonl.py --jsonl finetune/property_inclusion_test.jsonl --check   # expect: 0 passages >= limit

# the corpus can still be rebuilt
ELSEVIER_API_KEY=... python scripts/fetch_fulltext.py --limit 5
```

---

## 6. What this changes in the paper

One tracked insertion in *Code Availability*, supplied separately as an
MHY-marked Word file. Nothing else in the manuscript depends on the repository
layout, and the Data Availability paragraph already cites the Zenodo data DOI.

## Checklist

- [ ] `LICENSE` present, GitHub reports MIT, L2M3 notice retained
- [ ] `elsevier_*` gone from tree **and** from `git log --all`
- [ ] `__pycache__` gone
- [ ] `finetune/*.jsonl` sanitised, every record resolvable to a DOI
- [ ] audit CSV sanitised before the Zenodo upload
- [ ] `DOIs/DOIs.txt` retained, fetch script documented in README
- [ ] tag `v1.0.0` + Zenodo code DOI
- [ ] Code Availability updated in the manuscript

