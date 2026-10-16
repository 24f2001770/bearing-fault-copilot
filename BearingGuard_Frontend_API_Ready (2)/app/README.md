# BearingGuard Frontend

A Streamlit + Plotly prototype for the AMD ACT III Intelligent Industry hackathon. It presents bearing vibration data, a fault assessment, an explanation, maintenance actions with citations, and a technician confirmation/escalation step.

## Requirements
- Python 3.10 or newer
- Internet access only for package installation (the dashboard itself can run locally)

## Run on Windows PowerShell
From the `amd_frontend` folder:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r app\requirements.txt
Copy-Item app\.env.example app\.env
.\.venv\Scripts\python.exe -m streamlit run app\app.py
```

If your terminal is already inside the `app` folder, use:

```powershell
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
..\.venv\Scripts\python.exe -m streamlit run app.py
```

Open `http://localhost:8501`.

## Modes
- `MOCK=true`: optional offline demo. Uses local illustrative data and synthetic waveforms so frontend work can proceed before the backend is ready.
- `MOCK=false`: calls the API configured by `API_URL` (default `http://localhost:8080`). Expected endpoints: `GET /recordings`, `GET /signal?recording_id=...&window_index=...`, `POST /analyze` with `recording_id` and `window_index`, and `POST /confirm` with `request_id` and `decision` (`confirmed` or `escalated`). Confirm request/response details with the backend owner before integration.

## Important demo limitations
Mock predictions, confidence scores, latency, AMD serving status and citations are simulated. The generated vibration waveform is synthetic, not actual CWRU data. Placeholder source links must be replaced with verified references. The app must not be represented as performing real AMD inference until the backend is connected and verified.

## Included interface
- Four demo categories: healthy, inner-race fault, outer-race fault, and rolling-ball fault
- Vibration waveform and experimental frequency-spectrum visualization
- Fault severity, confidence and uncertainty display
- Explanation and likely causes
- Recommended actions with citation details
- Confirm / escalate decision controls
- Responsive dark industrial theme

## Backend integration checklist

1. Start the backend from the repository root with `python -m app` and verify `http://localhost:8080/docs`.
2. Copy `app/.env.example` to `app/.env` (MOCK=false).
3. Run the Streamlit frontend and choose a recording.
4. Analyze: the spinner remains visible while the API request is pending.
5. Verify the uncertainty level/note and safety-critical badges.
6. Click Confirm reviewed; only a successful POST `/confirm` response with `status: stored` displays acceptance.
7. Capture a screenshot of the live API-backed result and confirmation status.

**Important:** Verify request/response shapes against the backend `docs/contract.md` before merging. This ZIP did not include that contract or the backend, so end-to-end API compatibility is not yet verified.
