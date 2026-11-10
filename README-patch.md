# README edits to apply with this bundle

Three edits. Paste the block, delete the old lines.

---

## 1. Replace the title line (line 1)

**Delete**

```
#### MatProGPT: Achieving Near-Perfect Fidelity in Materials Property Extraction via Multi-Modal LLMs and Dynamic Prompt Engineering
```

**Insert**

```
# MatProGPT

**A literature-mined database of battery materials properties with record-level quality control**

Code and retrieval tooling for MatProGPT, a sequential LLM pipeline that extracts
battery-materials properties from the literature. The database itself is deposited
separately on Zenodo: **https://doi.org/10.5281/zenodo.23862298** (CC-BY-4.0).
```

---

## 2. Fix the clone directory in *Installation*

**Delete**

```
$ cd LLM-text
```

**Insert**

```
$ cd MatProGPT
```

---

## 3. Add a data / text-mining section (after *Fine-tuning*, before *Citation*)

```
## Data and text-mining terms

This repository does not redistribute publisher full texts. `DOIs/DOIs.txt`
lists the 47,022 screened DOIs, and `scripts/fetch_fulltext.py` retrieves the
full text at run time under your own text-mining agreement:

    export ELSEVIER_API_KEY=...        # https://dev.elsevier.com
    export ELSEVIER_INSTTOKEN=...      # optional, for licensed full text
    python scripts/fetch_fulltext.py --out data/cache --limit 20 --dry-run
    python scripts/fetch_fulltext.py --out data/cache

Elsevier articles (about 90% of the corpus) are fetched as full-text XML from
the Article Retrieval API; other DOIs fall back to an open-access copy via
Unpaywall when `--unpaywall-email` is given. Fetched files land in `data/cache/`,
which is git-ignored. A per-DOI status manifest is written to
`data/cache/fetch_manifest.csv`.

Shipped JSONL/CSV artefacts contain fingerprints and short evidence spans
instead of verbatim paragraphs. To check or re-apply that:

    python scripts/sanitize_jsonl.py --jsonl finetune/property_inclusion_test.jsonl --check
    python scripts/sanitize_jsonl.py --audit-csv extracted_results_audited.csv --max-chars 200
```

---

## 4. Replace the *License* section (last line of the file)

**Delete**

```
## License
MIT License
```

**Insert**

```
## License

Code: MIT — see [LICENSE](LICENSE). Portions of `llm_miner/` derive from
[L2M3](https://github.com/Yeonghun1675/L2M3) (MIT, Copyright (c) 2023
Yeonghun Kang).

Data: the MatProGPT database is licensed CC-BY-4.0 at
https://doi.org/10.5281/zenodo.23862298. Publisher full texts are not included
in either licence and are not redistributed here.

## Citation

Ait Tamerd, M. et al. MatProGPT: a literature-mined database of battery
materials properties with record-level quality control. (2026).
Database: https://doi.org/10.5281/zenodo.23862298
```

The empty `## Citation` heading currently in the file should be removed; the
block above replaces it.

