# Data comparator

Base-case tool for the G.E.R.S.O.N. publish pipeline. One `tool.yaml` at the repo root. The portal clones this repo, builds the Dockerfile, and runs the container only when someone asks for a comparison.

It compares two CSV files on the first column (or `--key`) and reports rows added, removed, and changed.

## Run locally

```bash
python compare.py --older examples/older.csv --newer examples/newer.csv --out out/report.json
```

## Run the image

```bash
docker build -t data-comparator .
docker run --rm \
  -v "$PWD/examples/older.csv:/inputs/file_a:ro" \
  -v "$PWD/examples/newer.csv:/inputs/file_b:ro" \
  -v "$PWD/out:/outputs" \
  data-comparator
```

Stdout is the JSON report. The same JSON is written to `/outputs/report.json`.

## What the pipeline passes in

| Input | Default path | Env override |
|---|---|---|
| Older file (`file_a`) | `/inputs/file_a` | `FILE_A` or `INPUT_FILE_A` |
| Newer file (`file_b`) | `/inputs/file_b` | `FILE_B` or `INPUT_FILE_B` |
| Report | `/outputs/report.json` | `OUTPUT_REPORT` |

`tool.yaml` asks for 1 vCPU, 2 GB, no GPU, and a 60 second limit. The sample files are the holdings diff from the portal: NVDA added, TLT removed, AAPL and MSFT changed.
