import streamlit as st
import fastf1
import matplotlib.pyplot as plt
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Fi Telemetry Replay",
    page_icon="🏎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── FastF1 cache ────────────────────────────────────────────────
CACHE_DIR = "/tmp/fastf1_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

# ── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
html, body, [class*="css"] { font-family: 'Titillium Web', sans-serif; }
.stApp { background: #0a0e1a; color: #e2e8f0; }
[data-testid="stSidebar"] { background: #0f1629 !important; border-right: 2px solid #e10600; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.hero {
  background: linear-gradient(135deg, #0f1629 0%, #1b2b4b 50%, #0f1629 100%);
  border: 1px solid #1e3a5f; border-left: 4px solid #e10600;
  border-radius: 4px; padding: 28px 32px 20px; margin-bottom: 24px; position: relative; overflow: hidden;
}
.hero::before {
  content: "F1"; position: absolute; right: 24px; top: 50%; transform: translateY(-50%);
  font-size: 96px; font-weight: 900; color: rgba(225,6,0,0.07); letter-spacing: -4px;
}
.hero h1 { font-size: 2.4rem; font-weight: 900; letter-spacing: 2px; color: #fff; margin: 0 0 4px; text-transform: uppercase; }
.hero h1 span { color: #e10600; }
.hero p { color: #94a3b8; font-size: 0.95rem; margin: 0; }
.metric-row { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.metric-card { flex: 1; min-width: 120px; background: #0f1629; border: 1px solid #1e3a5f; border-top: 3px solid #e10600; border-radius: 4px; padding: 14px 16px; }
.metric-card .label { font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }
.metric-card .value { font-size: 1.5rem; font-weight: 700; color: #fff; font-family: 'JetBrains Mono', monospace; }
.metric-card .sub { font-size: 0.75rem; color: #94a3b8; margin-top: 2px; }
.section-title { font-size: 0.7rem; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: #e10600; border-bottom: 1px solid #1e3a5f; padding-bottom: 6px; margin: 20px 0 14px; }
.stButton > button { background: #e10600 !important; color: white !important; border: none !important; border-radius: 3px !important; font-weight: 700 !important; letter-spacing: 1px !important; text-transform: uppercase !important; }
.stButton > button:hover { background: #b80500 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Constants ───────────────────────────────────────────────────
TEAM_COLORS = {
    "Red Bull Racing": "#3671C6", "Ferrari": "#E8002D", "Mercedes": "#27F4D2",
    "McLaren": "#FF8000", "Aston Martin": "#229971", "Alpine": "#FF87BC",
    "Williams": "#64C4FF", "RB": "#6692FF", "Kick Sauber": "#52E252", "Haas F1 Team": "#B6BABD",
}

# ── Helpers ─────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_session(year, gp, session_type):
    session = fastf1.get_session(year, gp, session_type)
    session.load(telemetry=True, laps=True, weather=False)
    return session

def format_laptime(td):
    if pd.isnull(td): return "N/A"
    total = td.total_seconds()
    m = int(total // 60)
    s = total % 60
    return f"{m}:{s:06.3f}"

def driver_color(driver, session):
    try:
        team = session.get_driver(driver)["TeamName"]
        return TEAM_COLORS.get(team, "#e10600")
    except:
        return "#e10600"

# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">Session Setup</div>', unsafe_allow_html=True)
    year = st.selectbox("Season", list(range(2024, 2017, -1)), index=0)
    gp_options = [
        "Bahrain", "Saudi Arabia", "Australia", "Japan", "China", "Miami",
        "Emilia Romagna", "Monaco", "Canada", "Spain", "Austria", "Britain",
        "Hungary", "Belgium", "Netherlands", "Italy", "Azerbaijan", "Singapore",
        "United States", "Mexico", "Brazil", "Las Vegas", "Qatar", "Abu Dhabi",
    ]
    gp = st.selectbox("Grand Prix", gp_options, index=7)
    session_type = st.selectbox("Session", ["R", "Q", "FP1", "FP2", "FP3"],
                                format_func=lambda x: {"R":"Race","Q":"Qualifying","FP1":"Practice 1","FP2":"Practice 2","FP3":"Practice 3"}[x])
    st.markdown('<div class="section-title">Load Data</div>', unsafe_allow_html=True)
    load_btn = st.button("🏁  Load Session", use_container_width=True)
    st.markdown("---")
    st.markdown("""<div style="font-size:0.8rem;color:#64748b;line-height:1.6">
    Fi Telemetry Replay<br>Built with FastF1 + Streamlit<br><br>
    <a href="https://github.com/Karthik9512/Fi_telemetry-replay" style="color:#e10600">GitHub →</a>
    </div>""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────
st.markdown("""<div class="hero">
  <h1>Fi <span>Telemetry</span> Replay</h1>
  <p>Formula 1 Race Data Visualization &amp; Analysis &nbsp;·&nbsp; Powered by FastF1</p>
</div>""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────
if "session" not in st.session_state:
    st.session_state.session = None
if "session_info" not in st.session_state:
    st.session_state.session_info = None

# ── Load session ─────────────────────────────────────────────────
if load_btn:
    with st.spinner(f"Loading {year} {gp} {session_type}..."):
        try:
            session = load_session(year, gp, session_type)
            st.session_state.session = session
            st.session_state.session_info = {"year": year, "gp": gp, "type": session_type}
            st.success(f"✅  Loaded: {year} {gp} Grand Prix — {session_type}")
        except Exception as e:
            st.error(f"❌  Could not load session: {e}")
            st.info("Try a different year or event.")

session = st.session_state.session

if session is None:
    col1, col2, col3 = st.columns(3)
    for col, emoji, title, desc in [
        (col1, "📡", "Live Telemetry", "Speed · Throttle · Brake · Gear · RPM"),
        (col2, "🏎", "Race Replay",    "Lap progression · Car positions · Sector times"),
        (col3, "📊", "Driver Compare", "Fastest lap overlay · Head-to-head delta"),
    ]:
        col.markdown(f"""<div style="background:#0f1629;border:1px solid #1e3a5f;border-top:3px solid #e10600;
                    border-radius:4px;padding:24px;text-align:center;height:140px">
          <div style="font-size:2rem">{emoji}</div>
          <div style="font-weight:700;color:#fff;margin:8px 0 4px">{title}</div>
          <div style="font-size:0.8rem;color:#64748b">{desc}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("""<br><div style="background:#0f1629;border:1px solid #1e3a5f;border-radius:4px;padding:20px 24px">
      <div class="section-title" style="margin-top:0">How to use</div>
      <ol style="color:#94a3b8;font-size:0.9rem;line-height:2">
        <li>Select a <b style="color:#fff">Season</b>, <b style="color:#fff">Grand Prix</b>, and <b style="color:#fff">Session</b> in the sidebar</li>
        <li>Click <b style="color:#e10600">Load Session</b> — data streams in from FastF1</li>
        <li>Pick drivers and telemetry channels to visualize</li>
        <li>Explore speed traces, throttle maps, and head-to-head comparisons</li>
      </ol>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Session loaded ───────────────────────────────────────────────
laps = session.laps
drivers = sorted(laps["Driver"].unique().tolist())
info = st.session_state.session_info

try:
    fastest = laps.pick_fastest()
    fl_driver = fastest["Driver"]
    fl_time = format_laptime(fastest["LapTime"])
    fl_team = session.get_driver(fl_driver).get("TeamName", "")
    total_laps = int(laps["LapNumber"].max())
    n_drivers = len(drivers)
except:
    fl_driver, fl_time, fl_team, total_laps, n_drivers = "N/A", "N/A", "", "N/A", len(drivers)

st.markdown(f"""<div class="metric-row">
  <div class="metric-card"><div class="label">Event</div><div class="value" style="font-size:1.1rem">{info['gp']}</div><div class="sub">{info['year']} · {info['type']}</div></div>
  <div class="metric-card"><div class="label">Fastest Lap</div><div class="value">{fl_time}</div><div class="sub">{fl_driver} · {fl_team}</div></div>
  <div class="metric-card"><div class="label">Total Laps</div><div class="value">{total_laps}</div><div class="sub">In session</div></div>
  <div class="metric-card"><div class="label">Drivers</div><div class="value">{n_drivers}</div><div class="sub">Loaded</div></div>
</div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📈 Telemetry", "🏎 Lap Times", "⚡ Driver Compare", "📋 Lap Data"])

# ── TAB 1: TELEMETRY ─────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Telemetry Channels</div>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([2, 2, 2])
    with col_a: driver1 = st.selectbox("Driver", drivers, key="tel_driver")
    with col_b:
        lap_options = ["Fastest"] + [str(i) for i in range(1, int(total_laps) + 1)]
        lap_sel = st.selectbox("Lap", lap_options, key="tel_lap")
    with col_c:
        channels = st.multiselect("Channels", ["Speed", "Throttle", "Brake", "Gear", "RPM"],
                                  default=["Speed", "Throttle", "Brake"])

    if st.button("📊 Plot Telemetry", key="plot_tel"):
        try:
            if lap_sel == "Fastest":
                lap = session.laps.pick_driver(driver1).pick_fastest()
            else:
                driver_laps = session.laps.pick_driver(driver1)
                lap = driver_laps[driver_laps["LapNumber"] == int(lap_sel)].iloc[0]

            tel = lap.get_telemetry()
            color = driver_color(driver1, session)
            n = len(channels)
            if n == 0:
                st.warning("Select at least one channel.")
            else:
                fig, axes = plt.subplots(n, 1, figsize=(12, 2.8 * n), facecolor="#0a0e1a")
                if n == 1: axes = [axes]
                fig.subplots_adjust(hspace=0.35)
                channel_map = {
                    "Speed":    ("Speed",    "km/h", color),
                    "Throttle": ("Throttle", "%",    "#22c55e"),
                    "Brake":    ("Brake",    "%",    "#e10600"),
                    "Gear":     ("nGear",    "gear", "#f59e0b"),
                    "RPM":      ("RPM",      "rpm",  "#a78bfa"),
                }
                for i, ch in enumerate(channels):
                    ax = axes[i]
                    col_key, unit, c = channel_map[ch]
                    if col_key in tel.columns:
                        ax.plot(tel["Distance"], tel[col_key], color=c, linewidth=1.8, alpha=0.95)
                        ax.fill_between(tel["Distance"], tel[col_key], alpha=0.08, color=c)
                    ax.set_facecolor("#0f1629")
                    ax.set_ylabel(f"{ch} ({unit})", color="#94a3b8", fontsize=9)
                    ax.tick_params(colors="#64748b", labelsize=8)
                    for spine in ax.spines.values(): spine.set_edgecolor("#1e3a5f")
                    ax.grid(True, color="#1e3a5f", linewidth=0.5, alpha=0.7)
                    if i < n - 1: ax.set_xticklabels([])
                axes[-1].set_xlabel("Distance (m)", color="#94a3b8", fontsize=9)
                lap_label = "Fastest Lap" if lap_sel == "Fastest" else f"Lap {lap_sel}"
                fig.suptitle(f"{driver1} — {lap_label} | {info['year']} {info['gp']} GP",
                             color="#fff", fontsize=13, fontweight="bold", y=1.01)
                st.pyplot(fig)
                plt.close(fig)
        except Exception as e:
            st.error(f"Error loading telemetry: {e}")

# ── TAB 2: LAP TIMES ─────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Lap Time Progression</div>', unsafe_allow_html=True)
    sel_drivers_lt = st.multiselect("Select drivers", drivers,
                                    default=drivers[:3] if len(drivers) >= 3 else drivers, key="lt_drivers")
    if st.button("📈 Plot Lap Times", key="plot_lt"):
        try:
            fig, ax = plt.subplots(figsize=(12, 5), facecolor="#0a0e1a")
            ax.set_facecolor("#0f1629")
            colors_pool = ["#e10600","#3671C6","#27F4D2","#FF8000","#229971","#FF87BC","#64C4FF","#f59e0b","#a78bfa","#22c55e"]
            for idx, drv in enumerate(sel_drivers_lt):
                drv_laps = laps.pick_driver(drv).copy()
                drv_laps = drv_laps[drv_laps["LapTime"].notna()]
                drv_laps["LapTimeSec"] = drv_laps["LapTime"].dt.total_seconds()
                drv_laps = drv_laps[drv_laps["LapTimeSec"] < drv_laps["LapTimeSec"].quantile(0.97)]
                c = driver_color(drv, session)
                ax.plot(drv_laps["LapNumber"], drv_laps["LapTimeSec"],
                        marker="o", markersize=4, linewidth=1.8, color=c, label=drv, alpha=0.9)
            ax.set_xlabel("Lap Number", color="#94a3b8", fontsize=10)
            ax.set_ylabel("Lap Time (seconds)", color="#94a3b8", fontsize=10)
            ax.tick_params(colors="#64748b")
            for spine in ax.spines.values(): spine.set_edgecolor("#1e3a5f")
            ax.grid(True, color="#1e3a5f", linewidth=0.5, alpha=0.7)
            ax.legend(facecolor="#0f1629", edgecolor="#1e3a5f", labelcolor="#e2e8f0", fontsize=9)
            ax.set_title(f"Lap Times — {info['year']} {info['gp']} GP", color="#fff", fontsize=13, fontweight="bold")
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.error(f"Error: {e}")

# ── TAB 3: DRIVER COMPARE ────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">Head-to-Head Telemetry Comparison</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: drv_a = st.selectbox("Driver A", drivers, index=0, key="cmp_a")
    with col2: drv_b = st.selectbox("Driver B", drivers, index=min(1, len(drivers)-1), key="cmp_b")

    if st.button("⚡ Compare Drivers", key="plot_cmp"):
        try:
            lap_a = session.laps.pick_driver(drv_a).pick_fastest()
            lap_b = session.laps.pick_driver(drv_b).pick_fastest()
            tel_a = lap_a.get_telemetry().add_distance()
            tel_b = lap_b.get_telemetry().add_distance()
            color_a = driver_color(drv_a, session)
            color_b = driver_color(drv_b, session)

            fig, axes = plt.subplots(3, 1, figsize=(12, 9), facecolor="#0a0e1a")
            fig.subplots_adjust(hspace=0.4)
            for ax, (col_key, ylabel) in zip(axes, [("Speed","Speed (km/h)"),("Throttle","Throttle (%)"),("Brake","Brake (%)")]):
                ax.set_facecolor("#0f1629")
                if col_key in tel_a.columns: ax.plot(tel_a["Distance"], tel_a[col_key], color=color_a, lw=1.8, label=drv_a)
                if col_key in tel_b.columns: ax.plot(tel_b["Distance"], tel_b[col_key], color=color_b, lw=1.8, label=drv_b, linestyle="--")
                ax.set_ylabel(ylabel, color="#94a3b8", fontsize=9)
                ax.tick_params(colors="#64748b", labelsize=8)
                for spine in ax.spines.values(): spine.set_edgecolor("#1e3a5f")
                ax.grid(True, color="#1e3a5f", lw=0.5, alpha=0.7)
                ax.legend(facecolor="#0f1629", edgecolor="#1e3a5f", labelcolor="#e2e8f0", fontsize=9)
            axes[-1].set_xlabel("Distance (m)", color="#94a3b8", fontsize=9)
            fig.suptitle(f"Fastest Lap — {drv_a} vs {drv_b} | {info['year']} {info['gp']} GP",
                         color="#fff", fontsize=13, fontweight="bold")
            st.pyplot(fig)
            plt.close(fig)

            st.markdown('<div class="section-title">Fastest Lap Summary</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            for col, drv, lap in [(c1, drv_a, lap_a), (c2, drv_b, lap_b)]:
                col.markdown(f"""<div style="background:#0f1629;border:1px solid #1e3a5f;
                  border-top:3px solid {driver_color(drv,session)};border-radius:4px;padding:16px">
                  <div style="font-size:1.1rem;font-weight:700;color:#fff;margin-bottom:8px">{drv}</div>
                  <div style="color:#94a3b8;font-size:0.85rem">Fastest Lap: <b style="color:#fff">{format_laptime(lap['LapTime'])}</b></div>
                  <div style="color:#94a3b8;font-size:0.85rem;margin-top:4px">Lap #: <b style="color:#fff">{int(lap['LapNumber'])}</b></div>
                </div>""", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error comparing: {e}")

# ── TAB 4: LAP DATA TABLE ────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">Session Lap Data</div>', unsafe_allow_html=True)
    col_f1, col_f2 = st.columns(2)
    with col_f1: filter_driver = st.selectbox("Filter by driver", ["All"] + drivers, key="tbl_drv")
    with col_f2: n_rows = st.selectbox("Rows to show", [20, 50, 100, 200], key="tbl_rows")

    display_cols = ["Driver", "LapNumber", "LapTime", "Sector1Time", "Sector2Time", "Sector3Time", "Compound", "TyreLife"]
    available_cols = [c for c in display_cols if c in laps.columns]
    tbl = laps[available_cols].copy()
    if filter_driver != "All": tbl = tbl[tbl["Driver"] == filter_driver]
    for tc in ["LapTime", "Sector1Time", "Sector2Time", "Sector3Time"]:
        if tc in tbl.columns: tbl[tc] = tbl[tc].apply(format_laptime)
    st.dataframe(tbl.head(n_rows).reset_index(drop=True), use_container_width=True, height=400)
