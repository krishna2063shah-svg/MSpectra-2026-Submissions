import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random
import time
from datetime import datetime, timedelta

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VoiceAgent Pro",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.stApp {
    background: #0a0c10;
    color: #e8e6df;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f1117 !important;
    border-right: 1px solid #1e2330;
}

[data-testid="stSidebar"] * {
    color: #e8e6df !important;
}

/* Hide default header */
header[data-testid="stHeader"] { display: none; }

/* Metric cards */
div[data-testid="metric-container"] {
    background: #0f1117;
    border: 1px solid #1e2330;
    border-radius: 12px;
    padding: 1rem 1.25rem;
}

div[data-testid="metric-container"] label {
    color: #6b7280 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f0ece3 !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
}

/* Buttons */
.stButton > button {
    background: #1a73e8 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #1557b0 !important;
    transform: translateY(-1px);
}

/* Call button special */
.call-btn > button {
    background: #16a34a !important;
    border-radius: 50px !important;
    padding: 0.75rem 2.5rem !important;
    font-size: 1rem !important;
    width: 100%;
}
.call-btn > button:hover { background: #15803d !important; }

.stop-btn > button {
    background: #dc2626 !important;
    border-radius: 50px !important;
    padding: 0.75rem 2.5rem !important;
    font-size: 1rem !important;
    width: 100%;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #1e2330 !important;
    border-radius: 12px !important;
    overflow: hidden;
}

/* Divider */
hr { border-color: #1e2330 !important; }

/* Custom cards */
.stat-card {
    background: #0f1117;
    border: 1px solid #1e2330;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
}

.live-badge {
    display: inline-block;
    background: #16a34a22;
    color: #4ade80;
    border: 1px solid #16a34a55;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 12px;
    font-family: 'DM Mono', monospace;
    font-weight: 500;
    letter-spacing: 0.05em;
}

.idle-badge {
    display: inline-block;
    background: #37415122;
    color: #9ca3af;
    border: 1px solid #37415155;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 12px;
    font-family: 'DM Mono', monospace;
}

.section-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.75rem;
}

.call-entry {
    background: #0f1117;
    border: 1px solid #1e2330;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.lang-pill {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 4px;
}

.intent-order { background: #1e3a5f; color: #60a5fa; }
.intent-complaint { background: #3b1f1f; color: #f87171; }
.intent-other { background: #1e3a2f; color: #4ade80; }

.page-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.75rem;
    font-weight: 800;
    color: #f0ece3;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}

.page-sub {
    font-size: 0.85rem;
    color: #6b7280;
    font-family: 'DM Mono', monospace;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "call_active" not in st.session_state:
    st.session_state.call_active = False
if "call_log" not in st.session_state:
    # Seed with demo data
    langs = ["en", "hi", "te", "ta", "mr", "bn"]
    lang_names = {"en": "English", "hi": "Hindi", "te": "Telugu", "ta": "Tamil", "mr": "Marathi", "bn": "Bengali"}
    intents = ["ORDER_STATUS", "COMPLAINT", "OTHER"]
    durations = [12, 34, 56, 23, 45, 67, 18, 90, 42, 28, 55, 38]
    transcripts = [
        "Where is my order? I placed it 3 days ago.",
        "Mera order kab aayega?",
        "Naa order ela undi?",
        "I want to file a complaint about my delivery.",
        "Product damaged when received.",
        "Ennaiku delivery varum?",
        "What are your working hours?",
        "Cancel my subscription please.",
        "Refund request for order #4521",
        "Track my parcel status.",
        "Mujhe refund chahiye.",
        "Poor service, very disappointed.",
    ]
    rows = []
    for i in range(12):
        lang = random.choice(langs)
        intent = random.choice(intents)
        ts = datetime.now() - timedelta(minutes=random.randint(5, 300))
        rows.append({
            "time": ts.strftime("%H:%M:%S"),
            "date": ts.strftime("%d %b"),
            "caller": f"+91 98{random.randint(10,99)} {random.randint(100,999)} {random.randint(1000,9999)}",
            "language": lang_names[lang],
            "lang_code": lang,
            "intent": intent,
            "duration": f"{random.choice(durations)}s",
            "transcript": transcripts[i],
            "status": "completed",
        })
    st.session_state.call_log = rows

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://127.0.0.1:8000 (Mocked)"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='padding: 1rem 0 0.5rem'><span style='font-family:Syne;font-size:1.2rem;font-weight:800;color:#f0ece3'>🎙️ VoiceAgent</span><span style='font-family:DM Mono;font-size:10px;color:#6b7280;margin-left:8px'>PRO</span></div>", unsafe_allow_html=True)
    st.divider()

    st.markdown("<p style='font-size:11px;color:#6b7280;font-family:DM Mono;text-transform:uppercase;letter-spacing:0.08em'>Navigation</p>", unsafe_allow_html=True)
    page = st.radio("", ["Dashboard", "Live Call", "Call Log", "Settings"], label_visibility="collapsed")

    st.divider()
    st.markdown("<p style='font-size:11px;color:#6b7280;font-family:DM Mono;text-transform:uppercase;letter-spacing:0.08em'>System Status</p>", unsafe_allow_html=True)

    asterisk_ok = True
    api_ok = True

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div style='font-size:12px;font-family:DM Mono'>{'🟢' if asterisk_ok else '🔴'} Asterisk</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='font-size:12px;font-family:DM Mono'>{'🟢' if api_ok else '🔴'} FastAPI</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<p style='font-size:11px;color:#6b7280;font-family:DM Mono;text-transform:uppercase;letter-spacing:0.08em'>Backend URL</p>", unsafe_allow_html=True)
    st.session_state.api_url = st.text_input("", value=st.session_state.api_url, label_visibility="collapsed")

# ── Helpers ───────────────────────────────────────────────────────────────────
def intent_color(intent):
    return {"ORDER_STATUS": "#60a5fa", "COMPLAINT": "#f87171", "OTHER": "#4ade80"}.get(intent, "#9ca3af")

def intent_bg(intent):
    return {"ORDER_STATUS": "intent-order", "COMPLAINT": "intent-complaint", "OTHER": "intent-other"}.get(intent, "")

def make_pie(df):
    counts = df["intent"].value_counts().reset_index()
    counts.columns = ["intent", "count"]
    colors = {"ORDER_STATUS": "#378ADD", "COMPLAINT": "#f87171", "OTHER": "#4ade80"}
    fig = go.Figure(go.Pie(
        labels=counts["intent"],
        values=counts["count"],
        hole=0.55,
        marker=dict(colors=[colors.get(i, "#9ca3af") for i in counts["intent"]],
                    line=dict(color="#0a0c10", width=3)),
        textinfo="percent",
        textfont=dict(family="DM Mono", size=12, color="#f0ece3"),
        hovertemplate="<b>%{label}</b><br>Calls: %{value}<br>Share: %{percent}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(font=dict(family="DM Mono", size=11, color="#9ca3af"),
                    bgcolor="rgba(0,0,0,0)", x=0.5, xanchor="center", y=-0.12, orientation="h"),
        margin=dict(t=10, b=10, l=10, r=10),
        height=260,
        annotations=[dict(text=f"<b>{len(df)}</b><br><span style='font-size:10'>calls</span>",
                          x=0.5, y=0.5, font=dict(size=18, color="#f0ece3", family="Syne"),
                          showarrow=False)]
    )
    return fig

def make_timeline(df):
    by_hour = {}
    for row in df.to_dict("records"):
        h = row["time"][:2]
        by_hour[h] = by_hour.get(h, 0) + 1
    hours = sorted(by_hour.keys())
    counts = [by_hour[h] for h in hours]
    fig = go.Figure(go.Bar(
        x=hours, y=counts,
        marker=dict(color="#1a73e8", opacity=0.85, line=dict(width=0)),
        hovertemplate="Hour %{x}:00<br>%{y} calls<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10),
        height=180,
        xaxis=dict(showgrid=False, tickfont=dict(family="DM Mono", size=10, color="#6b7280"), title=""),
        yaxis=dict(showgrid=True, gridcolor="#1e2330", tickfont=dict(family="DM Mono", size=10, color="#6b7280"), title=""),
        bargap=0.3,
    )
    return fig

def make_lang_bar(df):
    counts = df["language"].value_counts().reset_index()
    counts.columns = ["language", "count"]
    fig = go.Figure(go.Bar(
        y=counts["language"], x=counts["count"],
        orientation="h",
        marker=dict(color="#1D9E75", opacity=0.8, line=dict(width=0)),
        hovertemplate="%{y}: %{x} calls<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10),
        height=200,
        xaxis=dict(showgrid=True, gridcolor="#1e2330", tickfont=dict(family="DM Mono", size=10, color="#6b7280")),
        yaxis=dict(showgrid=False, tickfont=dict(family="DM Mono", size=11, color="#9ca3af")),
        bargap=0.25,
    )
    return fig

# ── Pages ─────────────────────────────────────────────────────────────────────

# ════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown("<div class='page-header'>Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Real-time overview of your multilingual voice agent</div>", unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.call_log)

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    total = len(df)
    orders = len(df[df["intent"] == "ORDER_STATUS"])
    complaints = len(df[df["intent"] == "COMPLAINT"])
    langs_count = df["language"].nunique()

    col1.metric("Total Calls", total, "+3 today")
    col2.metric("Order Queries", orders, f"{round(orders/total*100)}%")
    col3.metric("Complaints", complaints, f"{round(complaints/total*100)}%")
    col4.metric("Languages Detected", langs_count, "multilingual")

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    # Charts row
    c1, c2, c3 = st.columns([1.1, 1.2, 1.1])

    with c1:
        st.markdown("<p class='section-title'>Intent breakdown</p>", unsafe_allow_html=True)
        st.plotly_chart(make_pie(df), use_container_width=True, config={"displayModeBar": False})

    with c2:
        st.markdown("<p class='section-title'>Calls by hour</p>", unsafe_allow_html=True)
        st.plotly_chart(make_timeline(df), use_container_width=True, config={"displayModeBar": False})
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>Languages detected</p>", unsafe_allow_html=True)
        st.plotly_chart(make_lang_bar(df), use_container_width=True, config={"displayModeBar": False})

    with c3:
        st.markdown("<p class='section-title'>Recent calls</p>", unsafe_allow_html=True)
        for row in st.session_state.call_log[-5:][::-1]:
            ic = intent_bg(row["intent"])
            st.markdown(f"""
            <div class='call-entry'>
              <div>
                <div style='font-size:13px;font-weight:600;color:#e8e6df;font-family:Syne'>{row['caller']}</div>
                <div style='font-size:11px;color:#6b7280;font-family:DM Mono;margin-top:2px'>{row['date']} · {row['time']} · {row['duration']}</div>
              </div>
              <div style='text-align:right'>
                <span class='lang-pill {ic}'>{row['intent'].replace('_',' ')}</span>
                <div style='font-size:11px;color:#9ca3af;font-family:DM Mono;margin-top:4px'>{row['language']}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# LIVE CALL
# ════════════════════════════════════════════════════════
elif page == "Live Call":
    st.markdown("<div class='page-header'>Live Call</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Trigger and monitor a live AI call in real time</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        # Call panel
        status_html = "<span class='live-badge'>● LIVE</span>" if st.session_state.call_active else "<span class='idle-badge'>○ IDLE</span>"
        st.markdown(f"""
        <div style='background:#0f1117;border:1px solid {"#16a34a55" if st.session_state.call_active else "#1e2330"};
             border-radius:16px;padding:2rem;text-align:center;margin-bottom:1rem;
             transition:all 0.3s'>
          <div style='margin-bottom:1rem'>{status_html}</div>
          <div style='font-size:3rem;margin-bottom:0.5rem'>{"📞" if st.session_state.call_active else "🎙️"}</div>
          <div style='font-family:Syne;font-size:1.1rem;font-weight:700;color:#f0ece3;margin-bottom:0.25rem'>
            {"Call in progress..." if st.session_state.call_active else "Ready to receive calls"}
          </div>
          <div style='font-family:DM Mono;font-size:12px;color:#6b7280'>
            {"Asterisk connected · AI agent active" if st.session_state.call_active else "Asterisk listening on port 5060"}
          </div>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.call_active:
            st.markdown("<div class='call-btn'>", unsafe_allow_html=True)
            if st.button("▶  Start Simulated Call", use_container_width=True):
                st.session_state.call_active = True
                # Add a new simulated call
                new_call = {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "date": datetime.now().strftime("%d %b"),
                    "caller": f"+91 98{random.randint(10,99)} {random.randint(100,999)} {random.randint(1000,9999)}",
                    "language": random.choice(["Hindi", "Telugu", "English", "Tamil"]),
                    "lang_code": random.choice(["hi", "te", "en", "ta"]),
                    "intent": random.choice(["ORDER_STATUS", "COMPLAINT", "OTHER"]),
                    "duration": f"{random.randint(10,90)}s",
                    "transcript": random.choice([
                        "Mera order kahan hai?", "Where is my delivery?",
                        "Naa order status cheppandi", "I want to complain about my order"
                    ]),
                    "status": "live",
                }
                st.session_state.call_log.append(new_call)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='stop-btn'>", unsafe_allow_html=True)
            if st.button("■  End Call", use_container_width=True):
                st.session_state.call_active = False
                if st.session_state.call_log:
                    st.session_state.call_log[-1]["status"] = "completed"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # MOCKED BACKEND API
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>Send audio to backend (Mocked)</p>", unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload a WAV file to process", type=["wav"], label_visibility="collapsed")
        if uploaded:
            if st.button("Send to AI Agent"):
                with st.spinner("Simulating pipeline (STT → LLM → TTS)..."):
                    time.sleep(2)  # Simulate network and processing delay
                    
                    mock_result = {
                        "transcript": "This is a simulated successful response. The real backend is bypassed.",
                        "intent": "OTHER",
                        "language": "English",
                        "status": "success"
                    }
                    
                    st.success("Pipeline complete! (Mocked Response)")
                    st.json(mock_result)

    with col_right:
        st.markdown("<p class='section-title'>Live transcript feed</p>", unsafe_allow_html=True)
        if st.session_state.call_active and st.session_state.call_log:
            last = st.session_state.call_log[-1]
            st.markdown(f"""
            <div class='stat-card'>
              <div style='font-family:DM Mono;font-size:10px;color:#6b7280;margin-bottom:8px'>CALLER</div>
              <div style='font-size:14px;font-weight:600;color:#f0ece3;font-family:Syne'>{last['caller']}</div>
              <div style='font-family:DM Mono;font-size:11px;color:#9ca3af;margin-top:4px'>{last['language']}</div>
            </div>
            <div class='stat-card'>
              <div style='font-family:DM Mono;font-size:10px;color:#6b7280;margin-bottom:8px'>TRANSCRIPT</div>
              <div style='font-size:13px;color:#e8e6df;font-style:italic;line-height:1.5'>"{last['transcript']}"</div>
            </div>
            <div class='stat-card'>
              <div style='font-family:DM Mono;font-size:10px;color:#6b7280;margin-bottom:8px'>DETECTED INTENT</div>
              <span class='lang-pill {intent_bg(last["intent"])}' style='font-size:13px;padding:4px 12px'>
                {last['intent'].replace('_', ' ')}
              </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:#0f1117;border:1px dashed #1e2330;border-radius:12px;
                 padding:2.5rem;text-align:center;color:#374151'>
              <div style='font-size:2rem;margin-bottom:0.5rem'>📭</div>
              <div style='font-family:DM Mono;font-size:12px'>No active call</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>Pipeline steps</p>", unsafe_allow_html=True)
        steps = [
            ("01", "Asterisk receives call", "#1a73e8"),
            ("02", "Record caller audio (WAV)", "#1a73e8"),
            ("03", "Whisper STT → transcript", "#1D9E75"),
            ("04", "GPT-4 intent + reply", "#EF9F27"),
            ("05", "gTTS → response audio", "#f87171"),
            ("06", "Play back to caller", "#1D9E75"),
        ]
        for num, label, color in steps:
            active = st.session_state.call_active
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;
                 opacity:{"1" if active else "0.4"}'>
              <div style='font-family:DM Mono;font-size:10px;color:{color};width:24px'>{num}</div>
              <div style='flex:1;height:1px;background:{color}22'></div>
              <div style='font-family:DM Mono;font-size:11px;color:#9ca3af'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# CALL LOG
# ════════════════════════════════════════════════════════
elif page == "Call Log":
    st.markdown("<div class='page-header'>Call Log</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Full history of all processed calls</div>", unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.call_log)

    # Filters
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        intent_filter = st.selectbox("Intent", ["All", "ORDER_STATUS", "COMPLAINT", "OTHER"])
    with col2:
        lang_filter = st.selectbox("Language", ["All"] + sorted(df["language"].unique().tolist()))
    with col3:
        search = st.text_input("Search transcript", placeholder="e.g. order, refund, kahan...")

    filtered = df.copy()
    if intent_filter != "All":
        filtered = filtered[filtered["intent"] == intent_filter]
    if lang_filter != "All":
        filtered = filtered[filtered["language"] == lang_filter]
    if search:
        filtered = filtered[filtered["transcript"].str.contains(search, case=False)]

    st.markdown(f"<p style='font-family:DM Mono;font-size:12px;color:#6b7280;margin:0.5rem 0'>{len(filtered)} records found</p>", unsafe_allow_html=True)

    for _, row in filtered.iloc[::-1].iterrows():
        ic = intent_bg(row["intent"])
        intent_c = intent_color(row["intent"])
        st.markdown(f"""
        <div style='background:#0f1117;border:1px solid #1e2330;border-radius:12px;
             padding:1rem 1.25rem;margin-bottom:0.6rem'>
          <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px'>
            <div>
              <div style='font-size:14px;font-weight:600;color:#f0ece3;font-family:Syne'>{row['caller']}</div>
              <div style='font-size:11px;color:#6b7280;font-family:DM Mono;margin-top:2px'>
                {row['date']} · {row['time']} · {row['duration']} · {row['language']}
              </div>
            </div>
            <span class='lang-pill {ic}'>{row['intent'].replace('_', ' ')}</span>
          </div>
          <div style='margin-top:8px;padding:8px 12px;background:#0a0c10;border-radius:6px;
               border-left:2px solid {intent_c}'>
            <div style='font-size:12px;color:#9ca3af;font-family:DM Mono;font-style:italic'>
              "{row['transcript']}"
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    if st.button("Export as CSV"):
        csv = filtered.drop(columns=["lang_code", "status"]).to_csv(index=False)
        st.download_button("Download CSV", csv, "call_log.csv", "text/csv")

# ════════════════════════════════════════════════════════
# SETTINGS
# ════════════════════════════════════════════════════════
elif page == "Settings":
    st.markdown("<div class='page-header'>Settings</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Configure your voice agent parameters</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<p class='section-title'>Backend connection</p>", unsafe_allow_html=True)
        with st.container():
            st.text_input("FastAPI URL", value=st.session_state.api_url, key="api_url_setting")
            st.text_input("Asterisk host", value="127.0.0.1")
            st.number_input("SIP port", value=5060, min_value=1000, max_value=65535)

        st.markdown("<p class='section-title' style='margin-top:1.5rem'>STT settings</p>", unsafe_allow_html=True)
        st.selectbox("Whisper model", ["whisper-1", "whisper-large", "whisper-medium"])
        st.toggle("Auto-detect language", value=True)
        st.multiselect("Supported languages", ["English", "Hindi", "Telugu", "Tamil", "Marathi", "Bengali", "Kannada"], default=["English", "Hindi", "Telugu"])

    with col2:
        st.markdown("<p class='section-title'>LLM settings</p>", unsafe_allow_html=True)
        st.selectbox("Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo", "claude-sonnet-4-20250514"])
        st.number_input("Max tokens", value=500, min_value=100, max_value=2000)
        st.slider("Temperature", 0.0, 1.0, 0.3, step=0.05)
        st.text_area("System prompt override", height=100,
            value="You are a multilingual customer support agent. Detect the caller's language and reply in the same language. Classify intent as ORDER_STATUS, COMPLAINT, or OTHER.")

        st.markdown("<p class='section-title' style='margin-top:1.5rem'>TTS settings</p>", unsafe_allow_html=True)
        st.selectbox("TTS engine", ["gTTS (free)", "ElevenLabs (premium)", "OpenAI TTS"])
        st.selectbox("Voice style", ["Neutral", "Friendly", "Formal"])

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")