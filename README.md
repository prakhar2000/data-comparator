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

## tool.yaml

The portal builds the run screen from this file. It does not special-case the language.

| Field | What the portal does |
|---|---|
| `inputs[].type` | `file` or `text`. One control per input. |
| `inputs[].label` | The label on that control. |
| `inputs[].bind.path` | Where the container receives that input. |
| `outputs[].type` | `table`, `file`, or `text`. Picks the result view. |
| `outputs[].bind.path` | Where the container writes the result. |
| `outputs[].bind.format` | `json` is an object with `columns` and `rows`. |

`tool.yaml` asks for 1 vCPU, 2 GB, no GPU, and a 60 second limit. The sample files are the holdings diff from the portal: NVDA added, TLT removed, AAPL and MSFT changed.
