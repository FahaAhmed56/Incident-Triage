# IncidentIQ — AI Incident Similarity & Triage

**An offline, GitHub-ready AI/NLP project inspired by ServiceNow incident management.** Search similar historical incidents before creating duplicates and get explainable assignment-group suggestions.

## Features
- TF-IDF (word unigrams + bigrams) and cosine-similarity ranking
- Possible-duplicate indicator at a configurable **0.65 similarity threshold** (heuristic, not a calibrated probability)
- Keyword-based assignment group recommendations with matched keywords exposed
- Streamlit dashboard, sortable matches, CSV export
- FastAPI endpoint with interactive Swagger docs
- 25 synthetic sample incidents (no personal/customer information)
- Automated pytest tests and GitHub Actions CI
- No cloud credentials, paid APIs, Docker or database needed

## Quick start — Windows PowerShell
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app/streamlit_app.py
```
If PowerShell blocks activation, use `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py` instead.

Dashboard: http://localhost:8501

## Run the API (in a second terminal)
```powershell
python -m uvicorn api.main:app --reload
```
API documentation: http://127.0.0.1:8000/docs

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"short_description":"VPN disconnects after login","description":"MFA completes but VPN drops","top_k":3}'
```

## Run tests
```bash
python -m pytest -q
```

## Project structure
```text
incidentiq-ai/
  app/streamlit_app.py        # Interactive dashboard
  api/main.py                # REST API + validation
  src/engine.py              # Text normalization, TF-IDF, similarity, routing
  data/incidents.csv         # 25 synthetic historical incidents
  tests/                     # Unit and API tests
  .github/workflows/ci.yml   # CI checks
  requirements.txt
  .gitignore
  .env.example
  LICENSE
  README.md
```

## How it works
1. The incident history is loaded from `data/incidents.csv`.
2. Short and full descriptions are combined, cleaned and converted to TF-IDF vectors.
3. A query is converted using the same fitted vectorizer.
4. Cosine similarity scores (0 to 1) rank prior incidents by related wording.
5. A highest score >= 0.65 flags a **possible** duplicate for human investigation.
6. Separate keyword rules suggest an assignment group and show the triggering words.

**Example:** Input `VPN disconnects after login` with `VPN keeps dropping after MFA` returns similar VPN incidents and may recommend Network Support.

## Limitations & responsible use
- Data is entirely synthetic. This is a demonstration, not validated operational AI.
- TF-IDF may miss synonyms and semantic matches. Scores are similarity metrics, **not calibrated probabilities**.
- Routing suggestions use keyword rules; they are **not a learned ML classifier**.
- The app does not connect to ServiceNow, create incidents, update records or make autonomous decisions.
- For production, use approved ServiceNow APIs/authentication, RBAC, privacy controls, audit logs, supervised evaluation, and human approval before changes.

## Extend it
Integrate the ServiceNow Table API to fetch `incident` records, replace the synthetic CSV, add incremental indexing, evaluate precision@k with labeled duplicates, and add role-based access.

## GitHub
Suggested repository name: `IncidentIQ-AI`
Suggested description: `AI-assisted incident duplicate detection and assignment suggestions using Python, TF-IDF, Streamlit, and FastAPI.`

MIT licensed.
