# Bearing Fault Copilot

A "detect, explain, act" maintenance assistant for factory bearings, built for the AMD Developer Hackathon: ACT III (Track 1, Intelligent Industry).

1. A classifier reads a slice of vibration data from the CWRU Bearing Dataset and predicts the fault type and severity.
2. The prediction becomes a search over public bearing maintenance guides (retrieval-augmented generation).
3. An LLM served on AMD GPUs explains the fault and recommends actions, citing the retrieved passages.
4. A human confirms any safety-critical step.

**Status:** work in progress. This README is a placeholder and will be replaced with run instructions before submission.

## Repo layout

| Folder | What lives here |
| --- | --- |
| `sensor/` | Fault classifier |
| `rag/` | Retrieval pipeline over the bearing guides |
| `app/` | API, orchestrator and user interface |
| `data/` | Download scripts, source links and data notes (no raw data) |
| `docs/` | Data contract, dependency graph, demo script, submission text |

## Working on this repo

- Nobody pushes to `main`. Create a branch named `area/yourname-short-task`, for example `sensor/harshit-baseline`.
- Open a pull request into `main`, fill in the template, and get one approval before merging.
- Never commit secrets (use `.env`, copy from `.env.example`), raw data, source PDFs or model weights.
- The shapes of the data passed between parts are in [`docs/contract.md`](docs/contract.md). Who waits on whom is in [`docs/dependency-graph.md`](docs/dependency-graph.md).

## Data

CWRU Bearing Dataset (Case Western Reserve University Bearing Data Center): https://engineering.case.edu/bearingdatacenter. Raw files are not stored in this repo; see `data/README.md` for how to fetch them.

## Licence

MIT. See [LICENSE](LICENSE).
