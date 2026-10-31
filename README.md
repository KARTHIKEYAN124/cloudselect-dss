# CloudSelect — Cloud Service Decision Support System

A complete local decision support application for comparing AWS, Microsoft Azure, and Google Cloud VM configurations. React + TypeScript + Recharts frontend, Flask API, CSV-backed SQLite repository, and a tested weighted decision engine. No cloud account, credentials, or paid API is required.

## Features

- Compare three cloud VM configurations against budget, CPU, memory, storage, region, and security requirements.
- Rank eligible configurations using five adjustable criteria: cost, security, scalability, performance, and management.
- Inspect monthly cost components, scoring contributions, evidence, and exclusion reasons.
- Explore three preset scenarios and five controlled sensitivity experiments.
- Export the evaluated decision and sensitivity results as JSON.
- Use a responsive dashboard backed by one consistent server-side scoring model.

## Prerequisites

- Python 3.10 or later (tested with Python 3.14).
- Node.js 20.19+ or 22.12+ and npm (tested with Node.js 24).
- Git for cloning the repository.

```powershell
git clone https://github.com/KARTHIKEYAN124/cloudselect-dss.git
cd cloudselect-dss
```

## Run on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r backend/requirements.txt
cd frontend
npm install
npm run build
cd ..
.\.venv\Scripts\python backend/app.py
```

Open **http://127.0.0.1:5000**. Flask serves the built frontend and API together. `start.ps1` performs installation, build, and startup. For frontend development, start the Python server and run `npm run dev` in `frontend`; Vite proxies `/api` to port 5000.

## Verify

```powershell
.\.venv\Scripts\python -m pytest backend/tests -q
cd frontend
npm run build
```

## Demo walkthrough

1. Evaluate the baseline: 2 vCPU, 8 GiB, 100 GB SSD, 730 hours, 100 GB egress, Europe, €100 budget.
2. Inspect provider cost breakdowns, exclusion reasons, criterion evidence, and official links using **View details**.
3. Choose the startup, security, and growth scenarios and click **Run evaluation**.
4. Open **Results** for weighted contributions, then **What-if analysis** for five controlled weight experiments.
5. Export the evaluated requirements, results, and sensitivity analysis as JSON. Edits are marked pending until evaluated; exports always represent the last evaluated snapshot.

## Data honesty

**This is a working academic prototype with an illustrative dataset, not a live cloud procurement tool.** Official specification pages support the baseline CPU/RAM choices. EUR prices, regional availability, disk limits, security fixtures, and qualitative ratings are demonstration assumptions. No comparable performance benchmarks were collected. Customer-managed keys appear only in the Azure fixture to exercise exclusion logic; this does not claim AWS or GCP lack that capability.

Replace seed rates with dated calculator exports before using recommendations for real spending. Sources and per-criterion explanations are inspectable in the UI and CSVs. Costs omit tax, support, public IPv4, backup, operations, and workload-specific fees. Disk prices use a linear educational model rather than exact provider billing tiers. Europe is the only dataset region. CPU/RAM equality does not establish performance equivalence.

Optional Terraform generation is deliberately outside this implementation; the application never deploys infrastructure.

## Structure

- `frontend/src`: accessible responsive forms, provider comparison, contributions chart, sensitivity table, evidence dialog, JSON export.
- `backend/dss/engine.py`: validation, costs, mandatory eligibility, normalized weights, scoring, ties, sensitivity.
- `backend/dss/repository.py`: atomically refresh SQLite from version-controlled CSVs on startup.
- `backend/data`: three VM records, 15 criterion explanations, three reproducible scenarios.
- `backend/tests`: engine, constraints, missing values, ties, API, scenario regression checks.
- `docs`: architecture, methodology, evaluation, visual concept.

Read the [architecture](docs/architecture.md), [decision methodology](docs/methodology.md), and [evaluation guide](docs/evaluation.md) for implementation details and limitations.

## REST API

`GET /api/health`, `/api/alternatives`, `/api/criteria`, `/api/scenarios`.

`POST /api/evaluate`, `/api/compare`, `/api/sensitivity` accept requirements JSON. Omitted fields use baseline defaults. Supplied weights must include all five criteria, be finite and non-negative, and have a positive total; the server normalizes them. Invalid inputs return HTTP 400 with an error. See `backend/dss/engine.py` for baseline fields and `backend/data/scenarios.json` for examples.
