from __future__ import annotations

import copy
import json
import math
import os
from pathlib import Path

import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv


# =========================================================
# CONFIGURATION
# =========================================================

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")

MOCK = os.getenv("MOCK", "true").strip().lower() in {
    "1", "true", "yes", "on"
}
API_URL = os.getenv("API_URL", "http://localhost:8080").rstrip("/")

MOCK_FILE = BASE / "mock_data" / "sample.json"

if not MOCK_FILE.exists():
    st.error(f"Required data file not found: {MOCK_FILE}")
    st.stop()

MOCK_DATA = json.loads(MOCK_FILE.read_text(encoding="utf-8"))

FAULTS = {
    "normal": {
        "name": "Healthy",
        "short": "NORMAL",
        "color": "#31c48d",
        "description": "No fault indicated in this assessment.",
    },
    "inner_race": {
        "name": "Inner-race fault",
        "short": "INNER RACE",
        "color": "#ff6b6b",
        "description": "Potential damage on the bearing's inner ring.",
    },
    "outer_race": {
        "name": "Outer-race fault",
        "short": "OUTER RACE",
        "color": "#ff6b6b",
        "description": "Potential damage on the bearing's outer ring.",
    },
    "ball": {
        "name": "Rolling-ball fault",
        "short": "BALL FAULT",
        "color": "#ff6b6b",
        "description": "Potential damage to a rolling element.",
    },
}

st.set_page_config(
    page_title="BearingGuard | Industrial Intelligence",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# DARK THEME
# =========================================================

st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
        --bg: #090e17;
        --panel: #111a28;
        --line: #263548;
        --text: #edf3fb;
        --muted: #91a2b8;
        --cyan: #69dcff;
    }

    html, body, [class*="css"] {
        color-scheme: dark;
        font-family: Arial, sans-serif;
    }

    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background-color: #090e17 !important;
        color: #edf3fb !important;
    }

    .stApp {
        background:
            radial-gradient(
                ellipse at 10% 0%,
                #14283b 0%,
                #090e17 48%,
                #090e17 100%
            ) !important;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    h1, h2, h3, h4, h5, h6,
    p, label, li,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p {
        color: #edf3fb;
    }

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        color: #91a2b8 !important;
    }

    .brand {
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -0.7px;
        color: #edf3fb;
    }

    .subtitle {
        color: #91a2b8 !important;
        font-size: 12px;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 5px;
    }

    .section {
        color: #69dcff !important;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin-top: 22px;
        margin-bottom: 12px;
    }

    .panel {
        background: #111a28 !important;
        border: 1px solid #263548;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
    }

    .fault {
        background: linear-gradient(110deg, #351e29, #171724) !important;
        border: 1px solid #713f4a;
        border-radius: 14px;
        padding: 22px;
        margin: 12px 0;
    }

    .healthy {
        background: linear-gradient(110deg, #10332e, #111b27) !important;
        border: 1px solid #28634f;
        border-radius: 14px;
        padding: 22px;
        margin: 12px 0;
    }

    .fault h2, .fault h3,
    .healthy h2, .healthy h3 {
        color: #ffffff !important;
    }

    .fault p, .healthy p {
        color: #c3d0df !important;
    }

    /* Dropdown */

    [data-testid="stSelectbox"] label,
    [data-testid="stSelectbox"] label p {
        color: #91a7bf !important;
        font-weight: 700 !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background: #111a28 !important;
        color: #edf3fb !important;
        border: 1px solid #34475b !important;
        border-radius: 9px !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] * {
        color: #edf3fb !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [data-baseweb="menu"] ul {
        background: #111a28 !important;
    }

    [role="option"] {
        background: #111a28 !important;
        color: #edf3fb !important;
    }

    [role="option"]:hover {
        background: #203449 !important;
    }

    /* Metric cards */

    [data-testid="stMetric"] {
        background: #101a27 !important;
        border: 1px solid #263649 !important;
        border-radius: 13px !important;
        padding: 15px !important;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        color: #91a7bf !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div,
    [data-testid="stMetricValue"] p {
        color: #edf3fb !important;
    }

    /* Buttons */

    .stButton > button {
        background: #122536 !important;
        color: #edf3fb !important;
        border: 1px solid #34475b !important;
        border-radius: 10px !important;
        min-height: 42px;
        font-weight: 700;
    }

    .stButton > button:hover {
        background: #203449 !important;
        border-color: #69dcff !important;
        color: #69dcff !important;
    }

    .stButton > button[kind="primary"] {
        background: #31bde8 !important;
        color: #07111b !important;
        border: 1px solid #31bde8 !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: #69dcff !important;
        color: #07111b !important;
    }

    /* Inputs */

    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,
    input, textarea {
        background: #111a28 !important;
        color: #edf3fb !important;
        border-color: #34475b !important;
    }

    /* Expanders */

    [data-testid="stExpander"] {
        background: #111a28 !important;
        border: 1px solid #263548 !important;
        border-radius: 10px !important;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {
        color: #edf3fb !important;
    }

    /* Safety labels */

    .safety {
        display: inline-block;
        color: #ffaaaa !important;
        background: #3c202a !important;
        border: 1px solid #81414c;
        border-radius: 5px;
        padding: 5px 8px;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.7px;
    }

    .warning {
        background: #322919 !important;
        border: 1px solid #9b7434;
        border-radius: 9px;
        padding: 12px;
        color: #ffe0a1 !important;
        margin: 10px 0;
    }

    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    [data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #31c48d, #69dcff) !important;
    }

    hr {
        border-color: #263548 !important;
    }

    @media (max-width: 800px) {
        .brand {
            font-size: 23px;
        }

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# API HELPERS
# =========================================================

def get_json(path: str, params: dict | None = None) -> dict:
    response = requests.get(
        f"{API_URL}{path}",
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, dict):
        raise ValueError(f"{path} returned an unexpected response.")

    return payload


def post_json(path: str, payload: dict) -> dict:
    response = requests.post(
        f"{API_URL}{path}",
        json=payload,
        timeout=90,
    )
    response.raise_for_status()

    result = response.json()

    if not isinstance(result, dict):
        raise ValueError(f"{path} returned an unexpected response.")

    return result


def recordings() -> list[dict]:
    payload = MOCK_DATA if MOCK else get_json("/recordings")
    rows = payload.get("recordings")

    if not isinstance(rows, list):
        raise ValueError(
            "The API response is missing its recordings list."
        )

    return [
        row for row in rows
        if isinstance(row, dict) and row.get("recording_id")
    ]


def true_fault(rec_id: str) -> str:
    for row in MOCK_DATA.get("recordings", []):
        if row.get("recording_id") == rec_id:
            return row.get("true_fault_type", "normal")

    return "normal"


# =========================================================
# SIGNAL RETRIEVAL
# =========================================================

def signal(rec_id: str, index: int = 12) -> dict:
    if not MOCK:
        payload = get_json(
            "/signal",
            {
                "recording_id": rec_id,
                "window_index": index,
            },
        )

        if not isinstance(payload.get("samples"), list):
            raise ValueError("The signal response is missing samples.")

        return payload

    # Synthetic waveform for interface testing only.
    fault = true_fault(rec_id)

    amplitudes = {
        "normal": 0.12,
        "inner_race": 0.65,
        "outer_race": 0.82,
        "ball": 0.5,
    }

    amp = amplitudes.get(fault, 0.3)

    samples = [
        round(
            0.12 * math.sin(i * 0.075)
            + amp * (math.sin(i * 0.39) ** 12)
            * math.sin(i * 1.12),
            5,
        )
        for i in range(2000)
    ]

    return {
        "recording_id": rec_id,
        "window_index": index,
        "sample_rate_hz": 12000,
        "samples": samples,
    }


# =========================================================
# ANALYSIS
# =========================================================

def analyze(rec_id: str, index: int = 12) -> dict:
    if not MOCK:
        return post_json(
            "/analyze",
            {
                "recording_id": rec_id,
                "window_index": index,
            },
        )

    if not isinstance(MOCK_DATA.get("analysis"), dict):
        raise ValueError("The analysis data is missing.")

    result = copy.deepcopy(MOCK_DATA["analysis"])
    fault = true_fault(rec_id)

    confidence_values = {
        "normal": 0.97,
        "inner_race": 0.91,
        "outer_race": 0.93,
        "ball": 0.88,
    }

    confidence = confidence_values.get(fault, 0.8)

    sensor = result.setdefault("sensor", {})
    sensor.update(
        recording_id=rec_id,
        window_index=index,
        fault_type=fault,
        severity=(
            "none"
            if fault == "normal"
            else "medium"
            if fault == "outer_race"
            else "small"
        ),
        confidence=confidence,
    )

    sensor["probabilities"] = {
        label: confidence if label == fault else 0.02
        for label in ("normal", "inner_race", "outer_race", "ball")
    }

    result["request_id"] = f"sample-{rec_id}-{index}"

    result["explanation"] = (
        "This assessment uses illustrative sample data. "
        "Review the vibration signal and verify findings with "
        "a qualified technician."
    )

    result["likely_causes"] = (
        []
        if fault == "normal"
        else [
            "Possible bearing wear or surface damage.",
            "Lubrication, contamination, or alignment issues "
            "may need inspection.",
        ]
    )

    if fault == "normal":
        result["recommended_actions"] = [
            {
                "step": (
                    "Continue routine monitoring and record "
                    "the next inspection reading."
                ),
                "safety_critical": False,
                "citation_ids": [],
            }
        ]
        result["needs_human_confirm"] = False
    else:
        result["recommended_actions"] = [
            {
                "step": (
                    "Review the vibration trace and inspect the "
                    "bearing housing using the approved procedure."
                ),
                "safety_critical": False,
                "citation_ids": [],
            },
            {
                "step": (
                    "Have a qualified technician decide whether "
                    "shutdown, removal, or replacement is required."
                ),
                "safety_critical": True,
                "citation_ids": [],
            },
        ]
        result["needs_human_confirm"] = True

    result["uncertainty"] = {
        "level": "medium" if fault == "ball" else "low",
        "note": (
            "This is simulated output, not a validated diagnosis."
        ),
    }

    result["meta"] = {
        "model": "sample-model",
        "served_on": "BearingGuard",
        "latency_ms": {"total": 1900},
    }

    return result


# =========================================================
# SIGNAL CHART
# =========================================================

def render_signal_chart(sig: dict, chart_key: str) -> None:
    samples = sig.get("samples") or []

    if not isinstance(samples, list) or not samples:
        st.warning("No vibration samples are available.")
        return

    samples = samples[:2000]
    rate = sig.get("sample_rate_hz") or 12000
    x_values = [i / rate for i in range(len(samples))]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=samples,
            mode="lines",
            line={"color": "#69dcff", "width": 1.35},
            hovertemplate=(
                "Time: %{x:.4f}s<br>"
                "Amplitude: %{y:.4f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        height=260,
        margin=dict(l=8, r=8, t=10, b=28),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(7,14,23,.35)",
        font={"color": "#edf3fb", "size": 10},
        xaxis_title="Time (seconds)",
        yaxis_title="Amplitude",
        showlegend=False,
        xaxis={"gridcolor": "#263548"},
        yaxis={"gridcolor": "#263548"},
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
        key=chart_key,
    )


# =========================================================
# FREQUENCY SPECTRUM
# =========================================================

def render_spectrum(
    samples: list[float],
    rate: int,
    chart_key: str,
) -> None:
    if len(samples) < 8:
        return

    n = min(len(samples), 512)
    values = samples[:n]
    average = sum(values) / len(values)
    centered = [value - average for value in values]

    frequencies = []
    magnitudes = []

    for k in range(1, min(70, n // 2)):
        real = sum(
            centered[t] * math.cos(2 * math.pi * k * t / n)
            for t in range(n)
        )
        imag = sum(
            centered[t] * math.sin(2 * math.pi * k * t / n)
            for t in range(n)
        )

        frequencies.append(k * rate / n)
        magnitudes.append(math.sqrt(real**2 + imag**2) / n)

    fig = go.Figure(
        go.Scatter(
            x=frequencies,
            y=magnitudes,
            mode="lines",
            line={"color": "#a78bfa", "width": 1.5},
        )
    )

    fig.update_layout(
        height=200,
        margin=dict(l=8, r=8, t=5, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(7,14,23,.35)",
        font={"color": "#edf3fb", "size": 10},
        xaxis_title="Frequency (Hz)",
        yaxis_title="Magnitude",
        showlegend=False,
        xaxis={"gridcolor": "#263548"},
        yaxis={"gridcolor": "#263548"},
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
        key=chart_key,
    )


# =========================================================
# RESULTS AND TECHNICIAN CONFIRMATION
# =========================================================

def render_result(
    data: dict,
    sig: dict,
    rec_id: str,
) -> None:
    sensor = data.get("sensor")
    if not isinstance(sensor, dict):
        sensor = {}

    fault = sensor.get("fault_type", "unknown")

    fault_info = FAULTS.get(
        fault,
        {
            "name": "Unknown condition",
            "short": "UNKNOWN",
            "description": "The API returned an unrecognized fault label.",
        },
    )

    severity = str(sensor.get("severity", "unknown")).upper()
    confidence = sensor.get("confidence")
    uncertainty = data.get("uncertainty") or {}
    meta = data.get("meta") or {}
    latency = (meta.get("latency_ms") or {}).get("total", "—")

    confidence_ok = (
        isinstance(confidence, (int, float))
        and 0 <= confidence <= 1
    )

    st.markdown(
        '<div class="section">01 / MACHINE ASSESSMENT</div>',
        unsafe_allow_html=True,
    )

    banner_class = "healthy" if fault == "normal" else "fault"

    st.markdown(
        f"""
        <div class="{banner_class}">
            <h2>{fault_info["short"]} DETECTED</h2>
            <h3>{fault_info["name"]}</h3>
            <p>{fault_info["description"]}</p>
            <p>Severity: {severity} · Recording: {rec_id}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "**Uncertainty level:** "
        + str(uncertainty.get("level", "Not supplied")).upper()
    )

    st.info(
        "Uncertainty note: "
        + str(
            uncertainty.get("note")
            or "The API did not provide an uncertainty note."
        )
    )

    if (
        str(uncertainty.get("level", "")).lower() in {"medium", "high"}
        or (confidence_ok and confidence < 0.7)
    ):
        st.warning(
            "Uncertain result — technician review is required before acting."
        )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "MODEL CONFIDENCE",
        f"{confidence:.0%}" if confidence_ok else "N/A",
    )
    col2.metric("SEVERITY", severity)
    col3.metric("RESPONSE TIME", f"{latency} ms")

    if confidence_ok:
        st.progress(float(confidence), text="Model confidence")

    st.markdown(
        '<div class="section">02 / SIGNAL DIAGNOSTICS</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="panel"><h3>Vibration waveform</h3>',
        unsafe_allow_html=True,
    )

    render_signal_chart(sig, f"result_signal_{rec_id}")

    rate = sig.get("sample_rate_hz") or 12000

    with st.expander("View frequency spectrum"):
        st.caption(
            "Visualization aid only, not a fault-frequency diagnosis."
        )
        render_spectrum(
            sig.get("samples") or [],
            rate,
            f"result_spectrum_{rec_id}",
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section">03 / EXPLANATION</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write(data.get("explanation") or "Explanation unavailable.")

    causes = data.get("likely_causes", [])

    if isinstance(causes, list) and causes:
        st.markdown("**Possible causes to inspect**")
        for cause in causes:
            st.markdown(f"- {cause}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section">04 / MAINTENANCE ACTIONS</div>',
        unsafe_allow_html=True,
    )

    actions = data.get("recommended_actions", [])

    if not isinstance(actions, list):
        actions = []

    for i, action in enumerate(actions, start=1):
        if not isinstance(action, dict):
            continue

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(
            f"**{i:02d}. {action.get('step', 'Action unavailable')}**"
        )

        if action.get("safety_critical"):
            st.markdown(
                '<span class="safety">SAFETY-CRITICAL</span>',
                unsafe_allow_html=True,
            )
            st.warning(
                "Review the approved site procedure before acting."
            )
        else:
            st.caption("Review recommended.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section">05 / TECHNICIAN DECISION</div>',
        unsafe_allow_html=True,
    )

    request_id = data.get("request_id")

    if st.session_state.get("decision_request") != request_id:
        st.session_state["decision_request"] = request_id
        st.session_state["decision"] = None

    has_safety_action = any(
        isinstance(action, dict) and action.get("safety_critical")
        for action in actions
    )

    if data.get("needs_human_confirm") or has_safety_action:
        st.markdown(
            '<div class="warning">Safety-critical action present. '
            "Review the approved procedure and site safety requirements "
            "before proceeding.</div>",
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns(2)

    with col1:
        confirm_clicked = st.button(
            "✓ Confirm reviewed",
            type="primary",
            use_container_width=True,
            key=f"confirm_{rec_id}",
        )

    with col2:
        escalate_clicked = st.button(
            "Escalate to specialist",
            use_container_width=True,
            key=f"escalate_{rec_id}",
        )

    decision = (
        "confirmed"
        if confirm_clicked
        else "escalated"
        if escalate_clicked
        else None
    )

    if decision:
        try:
            if MOCK:
                response = {"status": "stored"}
            else:
                response = post_json(
                    "/confirm",
                    {
                        "request_id": request_id,
                        "decision": decision,
                    },
                )

            if response.get("status") != "stored":
                raise ValueError(
                    "The backend did not confirm that the decision was stored."
                )

            st.session_state["decision"] = decision

        except (
            requests.RequestException,
            ValueError,
            KeyError,
        ) as exc:
            st.error(f"Could not save the decision: {exc}")

    saved_decision = st.session_state.get("decision")

    if saved_decision == "confirmed":
        st.success(
            "Technician review confirmed."
            + (
                " This confirmation is local to the sample interface."
                if MOCK
                else " Decision saved by backend."
            )
        )
    elif saved_decision == "escalated":
        st.warning(
            "Escalated for specialist review."
            + (
                " This action is local to the sample interface."
                if MOCK
                else " Decision saved by backend."
            )
        )
    else:
        st.caption(
            "PENDING — no action is accepted until confirmation "
            "is stored by the API."
        )

    with st.expander("Model class probabilities"):
        probabilities = sensor.get("probabilities", {})

        if isinstance(probabilities, dict) and probabilities:
            for label, value in probabilities.items():
                label_name = FAULTS.get(
                    label, {}
                ).get("name", label.replace("_", " ").title())

                if isinstance(value, (int, float)):
                    st.write(f"**{label_name}** · {value:.1%}")
                    st.progress(max(0.0, min(1.0, float(value))))
        else:
            st.caption("No probability breakdown was supplied.")

    if MOCK:
        st.info(
            "Illustrative results are being displayed. The waveform, "
            "confidence values and latency are simulated; connect the "
            "analysis backend for actual model predictions."
        )


# =========================================================
# MAIN APPLICATION
# =========================================================

st.markdown(
    '<div class="brand">⚙ BearingGuard<span style="color:#69dcff">.</span></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Industrial intelligence · Predictive maintenance</div>',
    unsafe_allow_html=True,
)

st.markdown("---")
st.title("Machine health console")

if MOCK:
    st.info("Sample data is being used.")
else:
    st.success(f"API configured: {API_URL}")

st.write(
    "Select a vibration recording to inspect its signal and review "
    "maintenance recommendations."
)

try:
    rows = recordings()

    if not rows:
        st.warning("No recordings are available.")
        st.stop()

    row_map = {row["recording_id"]: row for row in rows}
    ids = list(row_map)

    selected = st.selectbox(
        "RECORDING LIBRARY",
        ids,
        format_func=lambda rid: (
            f"{rid} · "
            f"{FAULTS.get(row_map[rid].get('true_fault_type'), {}).get('name', 'Unknown')}"
        ),
    )

    chosen = row_map[selected]

    col1, col2, col3 = st.columns(3)

    col1.metric("Motor speed", chosen.get("approx_rpm", "—"))
    col2.metric("Motor load", f"{chosen.get('load_hp', '—')} hp")
    col3.metric("Available windows", chosen.get("num_windows", "—"))

    run = st.button(
        "Analyze recording",
        type="primary",
        use_container_width=True,
    )

    if run:
        st.session_state.pop("result", None)
        st.session_state.pop("signal", None)
        st.session_state.pop("decision", None)

        try:
            with st.spinner("Reading vibration signal..."):
                signal_data = signal(selected)

            with st.spinner(
                "Analyzing... This may take approximately 10 seconds. "
                "Please wait for the response."
            ):
                result = analyze(selected)

            if not isinstance(result.get("sensor"), dict):
                raise ValueError(
                    "The analysis response is missing its sensor object."
                )

            st.session_state["result"] = result
            st.session_state["signal"] = signal_data
            st.session_state["recording"] = selected
            st.session_state["decision_request"] = None

        except (
            requests.RequestException,
            ValueError,
            KeyError,
            TypeError,
        ) as exc:
            st.session_state.pop("result", None)
            st.session_state.pop("signal", None)
            st.error(f"Analysis failed: {exc}")

    if (
        "result" in st.session_state
        and "signal" in st.session_state
    ):
        active_id = st.session_state.get("recording", selected)
        signal_data = st.session_state["signal"]

        left, right = st.columns([1, 1.08], gap="large")

        with left:
            st.markdown(
                '<div class="section">LIVE SIGNAL PREVIEW</div>',
                unsafe_allow_html=True,
            )

            st.markdown('<div class="panel">', unsafe_allow_html=True)

            # Unique key for the preview chart.
            render_signal_chart(
                signal_data,
                f"preview_signal_{active_id}",
            )

            st.caption(
                f"Recording: {active_id} · "
                f"Sample rate: {signal_data.get('sample_rate_hz', '—')} Hz"
            )

            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            render_result(
                st.session_state["result"],
                signal_data,
                active_id,
            )

    else:
        st.markdown(
            """
            <div class="panel">
                <h3>Ready to inspect a machine</h3>
                <p>
                    Choose a recording and select Analyze recording.
                    Your assessment, signal charts, uncertainty information,
                    and technician decision will appear here.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

except (
    requests.RequestException,
    ValueError,
    KeyError,
    TypeError,
) as exc:
    st.error(f"Could not load recordings: {exc}")
    st.caption(
        "Check the data file, API_URL and backend service configuration."
    )

st.markdown("---")

st.caption(
    "BEARINGGUARD · DECISION SUPPORT ONLY. This interface is not a "
    "substitute for inspection by a qualified technician. Follow approved "
    "maintenance documentation and site safety procedures. When sample "
    "data is used, results are illustrative rather than actual diagnoses."
)