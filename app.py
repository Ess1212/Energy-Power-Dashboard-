# =============================================================================
# ENERGY POWER DASHBOARD
# PART 1 — DATA SCIENCE DASHBOARD + LIVE CLOCK (FIXED)
# =============================================================================

# =============================================================================
# IMPORTS
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Tuple
from streamlit.components.v1 import html

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Energy Power Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# GLOBAL CONSTANTS
# =============================================================================

APP_TITLE = "Energy Power Dashboard"

SWG_LIST = ["SWG1", "SWG2", "SWG3"]

POWER_MIN, POWER_MAX = -150.0, 150.0
SOC_MIN, SOC_MAX = 0.0, 100.0

LOCAL_TZ = ZoneInfo("Asia/Phnom_Penh")
DISPLAY_DT_FORMAT = "%m/%d/%Y %I:%M:%S %p"

# =============================================================================
# REMOVE STREAMLIT DEFAULT UI
# =============================================================================

st.markdown(
    """
<style>
header[data-testid="stHeader"] {display: none;}
div[data-testid="stToolbar"] {display: none;}
#MainMenu {display: none;}
section.main > div {padding-top: 0rem;}
</style>
""",
    unsafe_allow_html=True
)

# =============================================================================
# DASHBOARD CSS — DATA SCIENCE STYLE
# =============================================================================

st.markdown(
    """
<style>

/* Base */
html, body {
    background-color: #f3f6fb;
    font-family: Inter, sans-serif;
    color: #1f2937;
}

/* Header */
.dashboard-header {
    background: #1f3a8a;
    color: white;
    padding: 26px;
    border-radius: 14px;
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 6px;
    text-align: center;
}

/* Card */
.card {
    background: white;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    margin-bottom: 24px;
}

/* Titles */
.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #1f3a8a;
    margin-bottom: 14px;
}

.swg-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 8px;
}

/* Buttons */
button[kind="primary"] {
    background-color: #2563eb;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 600;
}

/* Tables */
[data-testid="stDataFrame"] {
    border-radius: 10px;
}

</style>
""",
    unsafe_allow_html=True
)

# =============================================================================
# HEADER
# =============================================================================

st.markdown(
    f'<div class="dashboard-header">{APP_TITLE}</div>',
    unsafe_allow_html=True
)

# =============================================================================
# LIVE CLOCK (RELIABLE — COMPONENTS.HTML)
# =============================================================================

html(
    """
    <div style="
        text-align:center;
        font-size:17px;
        font-weight:600;
        color:#475569;
        margin-bottom:26px;
    ">
        <span id="dashboard-clock"></span>
    </div>

    <script>
    function updateDashboardClock() {
        const now = new Date();
        const options = {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        };
        document.getElementById("dashboard-clock").innerHTML =
            now.toLocaleString([], options);
    }
    setInterval(updateDashboardClock, 1000);
    updateDashboardClock();
    </script>
    """,
    height=40
)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_state():
    for swg in SWG_LIST:
        key = f"{swg}_data"
        if key not in st.session_state:
            st.session_state[key] = pd.DataFrame(
                columns=[
                    f"{swg}_DateTime",
                    f"{swg}_Power(MW)",
                    f"{swg}_SOC(%)"
                ]
            )

init_state()

# =============================================================================
# VALIDATION
# =============================================================================

def validate_input(power: float, soc: float) -> Tuple[bool, str]:
    if power is None or soc is None:
        return False, "Power and SOC are required"
    if not (POWER_MIN <= power <= POWER_MAX):
        return False, "Power out of range"
    if not (SOC_MIN <= soc <= SOC_MAX):
        return False, "SOC out of range"
    return True, ""

# =============================================================================
# INSERT DATA
# =============================================================================

def insert_row(swg: str, power: float, soc: float):
    now = datetime.now(tz=LOCAL_TZ)
    row = {
        f"{swg}_DateTime": now,
        f"{swg}_Power(MW)": power,
        f"{swg}_SOC(%)": soc
    }
    st.session_state[f"{swg}_data"] = pd.concat(
        [st.session_state[f"{swg}_data"], pd.DataFrame([row])],
        ignore_index=True
    )

# =============================================================================
# INPUT SECTION
# =============================================================================

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Input Data</div>', unsafe_allow_html=True)

cols = st.columns(3)

for i, swg in enumerate(SWG_LIST):
    with cols[i]:
        label = swg.replace("SWG", "SWG-")
        st.markdown(f'<div class="swg-title">{label}</div>', unsafe_allow_html=True)

        power = st.number_input(
            f"{label} Power (MW)",
            value=None,
            step=1.0,
            format="%.2f",
            key=f"{swg}_p"
        )

        soc = st.number_input(
            f"{label} SOC (%)",
            value=None,
            step=1.0,
            format="%.2f",
            key=f"{swg}_s"
        )

        if st.button(f"Add {label}", key=f"add_{swg}", use_container_width=True):
            ok, msg = validate_input(power, soc)
            if not ok:
                st.error(msg)
            else:
                insert_row(swg, power, soc)
                st.success("Added successfully")

st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# TABLE PREVIEW
# =============================================================================

def format_preview(df: pd.DataFrame, swg: str) -> pd.DataFrame:
    df = df.copy()
    if df.empty:
        return df

    dt = pd.to_datetime(df[f"{swg}_DateTime"], errors="coerce")
    dt = dt.dt.tz_localize(None)

    df[f"{swg}_DateTime"] = dt.dt.strftime(DISPLAY_DT_FORMAT)
    df[f"{swg}_Power(MW)"] = df[f"{swg}_Power(MW)"].astype(str) + " MW"
    df[f"{swg}_SOC(%)"] = df[f"{swg}_SOC(%)"].astype(str) + " %"

    return df

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Table Preview</div>', unsafe_allow_html=True)

tcols = st.columns(3)

for i, swg in enumerate(SWG_LIST):
    with tcols[i]:
        st.dataframe(
            format_preview(st.session_state[f"{swg}_data"], swg),
            use_container_width=True,
            hide_index=True
        )

st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# END OF PART 1
# =============================================================================

# =============================================================================
# PART 2 — EDIT TABLE SYSTEM
# =============================================================================

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Edit Table</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# LOCK / UNLOCK TOGGLE
# -----------------------------------------------------------------------------

lock_col, info_col = st.columns([1, 3])

with lock_col:
    st.session_state.table_locked = st.toggle(
        "🔒 Lock Tables",
        value=st.session_state.get("table_locked", False)
    )

with info_col:
    if st.session_state.table_locked:
        st.info("Tables are locked. Unlock to edit data.")
    else:
        st.success("Tables are editable.")

st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# TABLE EDITOR (PER SWG)
# =============================================================================

def editable_table(swg: str):
    """
    Render editable table for a specific SWG.
    """

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-title">{swg.replace("SWG","SWG-")} Table Editor</div>',
        unsafe_allow_html=True
    )

    df_key = f"{swg}_data"
    df = st.session_state[df_key].copy()

    # Convert datetime to string for editing
    if not df.empty:
        df[f"{swg}_DateTime"] = pd.to_datetime(
            df[f"{swg}_DateTime"], errors="coerce"
        ).dt.strftime(DISPLAY_DT_FORMAT)

    # -------------------------------------------------------------------------
    # DATA EDITOR
    # -------------------------------------------------------------------------

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        disabled=st.session_state.table_locked,
        num_rows="dynamic",
        key=f"editor_{swg}"
    )

    # -------------------------------------------------------------------------
    # SAVE CHANGES
    # -------------------------------------------------------------------------

    if not st.session_state.table_locked:
        if not edited_df.equals(df):

            # Convert DateTime back to datetime
            try:
                edited_df[f"{swg}_DateTime"] = pd.to_datetime(
                    edited_df[f"{swg}_DateTime"],
                    format=DISPLAY_DT_FORMAT,
                    errors="coerce"
                ).dt.tz_localize(LOCAL_TZ)
            except Exception:
                st.error("Invalid DateTime format.")
                st.markdown('</div>', unsafe_allow_html=True)
                return

            st.session_state[df_key] = edited_df
            st.success("✅ Table updated successfully")

    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# RENDER ALL SWG EDITORS
# =============================================================================

editable_table("SWG1")
editable_table("SWG2")
editable_table("SWG3")

# =============================================================================
# END PART 2
# =============================================================================

# =============================================================================
# PART 3 — FULL STATISTICS & ANALYTICS CARDS
# =============================================================================

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Statistics & Analytics</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HELPER: SAFE STAT CALCULATION
# -----------------------------------------------------------------------------

def calculate_stats(df: pd.DataFrame, swg: str) -> dict:
    """
    Safely calculate statistics for Power and SOC.
    Returns a dict with all required metrics.
    """

    stats = {
        "power": {
            "min": None,
            "max": None,
            "mean": None,
            "avg": None,
            "latest": None,
        },
        "soc": {
            "min": None,
            "max": None,
            "mean": None,
            "avg": None,
            "latest": None,
        },
    }

    if df.empty:
        return stats

    power_col = f"{swg}_Power(MW)"
    soc_col = f"{swg}_SOC(%)"
    dt_col = f"{swg}_DateTime"

    # Ensure correct dtypes
    df = df.copy()
    df[dt_col] = pd.to_datetime(df[dt_col], errors="coerce")

    # Sort by datetime to get latest
    df_sorted = df.sort_values(dt_col)

    # ---------------- POWER ----------------
    power_series = pd.to_numeric(df_sorted[power_col], errors="coerce").dropna()

    if not power_series.empty:
        stats["power"]["min"] = power_series.min()
        stats["power"]["max"] = power_series.max()
        stats["power"]["mean"] = power_series.mean()
        stats["power"]["avg"] = power_series.mean()
        stats["power"]["latest"] = power_series.iloc[-1]

    # ---------------- SOC ----------------
    soc_series = pd.to_numeric(df_sorted[soc_col], errors="coerce").dropna()

    if not soc_series.empty:
        stats["soc"]["min"] = soc_series.min()
        stats["soc"]["max"] = soc_series.max()
        stats["soc"]["mean"] = soc_series.mean()
        stats["soc"]["avg"] = soc_series.mean()
        stats["soc"]["latest"] = soc_series.iloc[-1]

    return stats


# -----------------------------------------------------------------------------
# HELPER: DISPLAY METRIC SAFELY
# -----------------------------------------------------------------------------

def display_metric(label: str, value, unit: str = ""):
    if value is None:
        st.metric(label, "—")
    else:
        st.metric(label, f"{value:.2f}{unit}")


# =============================================================================
# RENDER ANALYTICS PER SWG
# =============================================================================

for swg in SWG_LIST:
    df = st.session_state[f"{swg}_data"]
    stats = calculate_stats(df, swg)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-title">{swg.replace("SWG","SWG-")} Analytics</div>',
        unsafe_allow_html=True
    )

    # ---------------- POWER CARDS ----------------
    st.markdown("**⚡ Power (MW)**")

    p_cols = st.columns(5)
    with p_cols[0]:
        display_metric("Min", stats["power"]["min"], " MW")
    with p_cols[1]:
        display_metric("Max", stats["power"]["max"], " MW")
    with p_cols[2]:
        display_metric("Mean", stats["power"]["mean"], " MW")
    with p_cols[3]:
        display_metric("Average", stats["power"]["avg"], " MW")
    with p_cols[4]:
        display_metric("Latest", stats["power"]["latest"], " MW")

    # ---------------- SOC CARDS ----------------
    st.markdown("**🔋 State of Charge (%)**")

    s_cols = st.columns(5)
    with s_cols[0]:
        display_metric("Min", stats["soc"]["min"], " %")
    with s_cols[1]:
        display_metric("Max", stats["soc"]["max"], " %")
    with s_cols[2]:
        display_metric("Mean", stats["soc"]["mean"], " %")
    with s_cols[3]:
        display_metric("Average", stats["soc"]["avg"], " %")
    with s_cols[4]:
        display_metric("Latest", stats["soc"]["latest"], " %")

st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# END PART 3
# =============================================================================

# =============================================================================
# PART 4A — ADVANCED CUSTOM CHART DASHBOARD (MATCHING SAMPLE UI)
# =============================================================================

import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# HELPER — PREPARE DATA
# -----------------------------------------------------------------------------

def prepare_chart_df(df: pd.DataFrame, swg: str) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    dt_col = f"{swg}_DateTime"

    df[dt_col] = pd.to_datetime(df[dt_col], errors="coerce").dt.tz_localize(None)
    df = df.sort_values(dt_col)

    return df


# =============================================================================
# CHART DASHBOARD PER SWG
# =============================================================================

for swg in SWG_LIST:

    df = prepare_chart_df(st.session_state[f"{swg}_data"], swg)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # HEADER
    # -------------------------------------------------------------------------

    st.markdown(
        f"### ⚡ {swg.replace('SWG','SWG-')}",
        unsafe_allow_html=True
    )

    if df.empty:
        st.info("No data available for visualization.")
        st.markdown('</div>', unsafe_allow_html=True)
        continue

    time_col = f"{swg}_DateTime"
    power_col = f"{swg}_Power(MW)"
    soc_col = f"{swg}_SOC(%)"

    # -------------------------------------------------------------------------
    # CONTROL PANEL + FOCUS CHART
    # -------------------------------------------------------------------------

    control_col, chart_col = st.columns([1, 4])

    with control_col:
        st.markdown("**Focus on step Line chart**")

        point_color = st.selectbox(
            "Color points",
            ["Indigo", "Emerald", "Cyan", "Orange"],
            key=f"{swg}_color"
        )

        point_size = st.slider(
            "Point size",
            4, 16, 8,
            key=f"{swg}_point_size"
        )

        show_grid = st.toggle(
            "Grid",
            value=True,
            key=f"{swg}_grid"
        )

    # Color mapping
    color_map = {
        "Indigo": "#6366f1",
        "Emerald": "#10b981",
        "Cyan": "#06b6d4",
        "Orange": "#f97316"
    }

    color = color_map[point_color]

    grid_cfg = dict(showgrid=show_grid)

    with chart_col:
        step_fig = go.Figure()

        step_fig.add_trace(
            go.Scatter(
                x=df[time_col],
                y=df[power_col],
                mode="lines+markers",
                line=dict(
                    shape="hv",
                    width=3,
                    color=color
                ),
                marker=dict(
                    size=point_size,
                    color=color
                ),
                name="Power (MW)"
            )
        )

        step_fig.update_layout(
            height=420,
            title="Step Line Chart (Power)",
            margin=dict(l=30, r=30, t=50, b=40),
            xaxis=dict(title="Time", **grid_cfg),
            yaxis=dict(title="Power (MW)", **grid_cfg),
            template="plotly_white",
            showlegend=False
        )

        st.plotly_chart(step_fig, use_container_width=True)

    # -------------------------------------------------------------------------
    # BOTTOM ROW — LINE / HISTOGRAM / BAR
    # -------------------------------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    # ================= LINE CHART =================
    with c1:
        line_fig = go.Figure()

        line_fig.add_trace(
            go.Scatter(
                x=df[time_col],
                y=df[power_col],
                mode="lines+markers",
                line=dict(color=color),
                marker=dict(size=point_size),
                name="Power"
            )
        )

        line_fig.update_layout(
            height=260,
            title="Line chart",
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(**grid_cfg),
            yaxis=dict(title="Power (MW)", **grid_cfg),
            template="plotly_white",
            showlegend=False
        )

        st.plotly_chart(line_fig, use_container_width=True)

    # ================= HISTOGRAM =================
    with c2:
        hist_fig = go.Figure()

        hist_fig.add_trace(
            go.Histogram(
                x=df[power_col],
                nbinsx=10,
                marker=dict(color=color),
                name="Power Distribution"
            )
        )

        hist_fig.update_layout(
            height=260,
            title="Histogram chart",
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(title="Power (MW)", **grid_cfg),
            yaxis=dict(title="Count", **grid_cfg),
            template="plotly_white",
            showlegend=False
        )

        st.plotly_chart(hist_fig, use_container_width=True)

    # ================= BAR PLOT =================
    with c3:
        bar_fig = go.Figure()

        bar_fig.add_trace(
            go.Bar(
                x=df[time_col],
                y=df[power_col],
                marker=dict(color=color),
                name="Power"
            )
        )

        bar_fig.update_layout(
            height=260,
            title="Bar plot chart",
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(title="Time", **grid_cfg),
            yaxis=dict(title="Power (MW)", **grid_cfg),
            template="plotly_white",
            showlegend=False
        )

        st.plotly_chart(bar_fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# END PART 4A
# =============================================================================

# =============================================================================
# PART 5 — DATA DOWNLOAD (CSV / XLSX / JSON)
# =============================================================================

import json
import io

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Download Data</div>', unsafe_allow_html=True)

st.caption(
    "Export all recorded data into CSV, XLSX, or JSON formats. "
    "• CSV and JSON are always available "
    "• XLSX is available only if openpyxl exists on the server "
    "• DateTime is exported in local time (human-readable)"
)

# -----------------------------------------------------------------------------
# HELPER — FORMAT DATETIME FOR EXPORT
# -----------------------------------------------------------------------------

def format_datetime_for_export(series: pd.Series) -> pd.Series:
    dt = pd.to_datetime(series, errors="coerce")
    dt = dt.dt.tz_localize(None)
    return dt.dt.strftime(DISPLAY_DT_FORMAT)

# -----------------------------------------------------------------------------
# HELPER — BUILD EXPORT DATAFRAME (MERGED)
# -----------------------------------------------------------------------------

def build_export_dataframe() -> pd.DataFrame:
    """
    Combine SWG1 / SWG2 / SWG3 tables side-by-side
    """
    dfs = []

    for swg in SWG_LIST:
        df = st.session_state[f"{swg}_data"].copy()

        if df.empty:
            dfs.append(
                pd.DataFrame(
                    columns=[
                        f"{swg}_DateTime",
                        f"{swg}_Power(MW)",
                        f"{swg}_SOC(%)",
                    ]
                )
            )
            continue

        df[f"{swg}_DateTime"] = format_datetime_for_export(
            df[f"{swg}_DateTime"]
        )

        dfs.append(df.reset_index(drop=True))

    # Align rows by index (Excel-style)
    max_len = max(len(d) for d in dfs)
    dfs = [d.reindex(range(max_len)) for d in dfs]

    export_df = pd.concat(dfs, axis=1)
    return export_df

# -----------------------------------------------------------------------------
# BUILD EXPORT DATA
# -----------------------------------------------------------------------------

export_df = build_export_dataframe()

# -----------------------------------------------------------------------------
# CSV DOWNLOAD
# -----------------------------------------------------------------------------

csv_bytes = export_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download CSV",
    data=csv_bytes,
    file_name="energy_power_data.csv",
    mime="text/csv",
    use_container_width=True,
)

# -----------------------------------------------------------------------------
# JSON DOWNLOAD
# -----------------------------------------------------------------------------

json_data = export_df.to_dict(orient="records")
json_bytes = json.dumps(json_data, indent=2).encode("utf-8")

st.download_button(
    "⬇ Download JSON",
    data=json_bytes,
    file_name="energy_power_data.json",
    mime="application/json",
    use_container_width=True,
)

# -----------------------------------------------------------------------------
# XLSX DOWNLOAD (SAFE — OPTIONAL)
# -----------------------------------------------------------------------------

def openpyxl_available() -> bool:
    try:
        import openpyxl  # noqa: F401
        return True
    except Exception:
        return False

if openpyxl_available():
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="EnergyData")

    buffer.seek(0)

    st.download_button(
        "⬇ Download XLSX",
        data=buffer,
        file_name="energy_power_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
else:
    st.info(
        "XLSX export unavailable. Install **openpyxl** to enable Excel downloads.",
        icon="ℹ️",
    )

st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# END PART 5 — DATA DOWNLOAD
# =============================================================================
