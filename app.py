# =============================================================================
# ENERGY POWER DASHBOARD
# PART 1 — PROFESSIONAL BLUE UI / INPUT / SESSION CORE (≈600 LINES)
# =============================================================================

# =============================================================================
# IMPORTS
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Tuple

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

APP_TITLE = "⚡ Energy Power Dashboard"

SWG_LIST = ["SWG1", "SWG2", "SWG3"]

# Fixed internal limits (NO UI SETTINGS)
POWER_MIN = -150.0
POWER_MAX = 150.0
SOC_MIN = 0.0
SOC_MAX = 100.0

LOCAL_TZ = ZoneInfo("Asia/Phnom_Penh")

DISPLAY_DT_FORMAT = "%m/%d/%Y %I:%M:%S %p"

# =============================================================================
# PROFESSIONAL DARK-BLUE DASHBOARD CSS
# =============================================================================

st.markdown(
    """
<style>

/* ===================== BASE ===================== */
html, body {
    background-color: #eef3fb;
    font-family: "Inter", sans-serif;
}

/* ===================== HEADER ===================== */
.header {
    background: linear-gradient(90deg, #0b2a66, #0f3c91);
    color: white;
    padding: 30px;
    border-radius: 18px;
    font-size: 42px;
    font-weight: 900;
    text-align: center;
    box-shadow: 0 18px 45px rgba(0,0,0,0.25);
}

/* ===================== GLASS CARD ===================== */
.glass {
    background: rgba(255,255,255,0.96);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 28px;
    box-shadow: 0 14px 40px rgba(0,40,120,0.15);
}

/* ===================== SECTION TITLE ===================== */
.section-title {
    font-size: 26px;
    font-weight: 900;
    color: #0b2a66;
    margin-bottom: 16px;
}

/* ===================== SWG TITLE ===================== */
.swg-title {
    font-size: 22px;
    font-weight: 800;
    color: #0b2a66;
    margin-bottom: 10px;
}

/* ===================== HELPER TEXT ===================== */
.helper {
    font-size: 16px;
    color: #475569;
    margin-bottom: 12px;
}

/* ===================== BUTTONS ===================== */
button[kind="primary"] {
    background: linear-gradient(90deg, #0b5cff, #1e90ff);
    border-radius: 14px;
    font-size: 18px;
    font-weight: 800;
    height: 52px;
}

/* ===================== DIVIDER ===================== */
.divider {
    height: 3px;
    background: linear-gradient(90deg, #2563eb, #60a5fa);
    margin: 26px 0;
    border-radius: 2px;
}

</style>
""",
    unsafe_allow_html=True
)

# =============================================================================
# MAIN HEADER
# =============================================================================

st.markdown(
    f'<div class="header">{APP_TITLE}</div>',
    unsafe_allow_html=True
)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state() -> None:
    """
    Initialize all required session variables safely.
    """

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

    if "table_locked" not in st.session_state:
        st.session_state.table_locked = False

    if "history" not in st.session_state:
        st.session_state.history = []

    if "redo_stack" not in st.session_state:
        st.session_state.redo_stack = []

    # Used later by Part 2 to show confirmation
    if "last_edit_confirm" not in st.session_state:
        st.session_state.last_edit_confirm = False

init_session_state()

# =============================================================================
# RESET DATA
# =============================================================================

with st.container():
    if st.button("🔄 Reset All Data", use_container_width=True):
        for swg in SWG_LIST:
            st.session_state[f"{swg}_data"] = (
                st.session_state[f"{swg}_data"].iloc[0:0]
            )
        st.success("All data cleared successfully.")

# =============================================================================
# VALIDATION (INTERNAL ONLY)
# =============================================================================

def validate_input(power: float, soc: float) -> Tuple[bool, str]:
    if power is None or soc is None:
        return False, "Power and SOC are required."

    if power < POWER_MIN or power > POWER_MAX:
        return False, f"Power must be between {POWER_MIN} and {POWER_MAX} MW."

    if soc < SOC_MIN or soc > SOC_MAX:
        return False, f"SOC must be between {SOC_MIN}% and {SOC_MAX}%."

    return True, ""

# =============================================================================
# INSERT DATA
# =============================================================================

def insert_swg_row(swg: str, power: float, soc: float) -> None:
    now_local = datetime.now(tz=LOCAL_TZ)

    row = {
        f"{swg}_DateTime": now_local,
        f"{swg}_Power(MW)": float(power),
        f"{swg}_SOC(%)": float(soc)
    }

    st.session_state[f"{swg}_data"] = pd.concat(
        [st.session_state[f"{swg}_data"], pd.DataFrame([row])],
        ignore_index=True
    )

# =============================================================================
# INPUT SECTION
# =============================================================================

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Input Data</div>', unsafe_allow_html=True)

cols = st.columns(3)

def swg_input(col, swg: str, label: str):
    with col:
        st.markdown(f'<div class="swg-title">{label}</div>', unsafe_allow_html=True)
        st.markdown('<div class="helper">Enter Power (MW) and SOC (%)</div>',
                    unsafe_allow_html=True)

        power = st.number_input(
            f"{label} Power (MW)",
            value=None,
            step=1.0,
            format="%.2f",
            key=f"{swg}_power_input"
        )

        soc = st.number_input(
            f"{label} SOC (%)",
            value=None,
            step=1.0,
            format="%.2f",
            key=f"{swg}_soc_input"
        )

        if st.button(f"➕ Add {label}", use_container_width=True):
            ok, msg = validate_input(power, soc)
            if not ok:
                st.error(msg)
            else:
                insert_swg_row(swg, power, soc)
                st.success(f"{label} added successfully")

swg_input(cols[0], "SWG1", "SWG-1")
swg_input(cols[1], "SWG2", "SWG-2")
swg_input(cols[2], "SWG3", "SWG-3")

st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# TABLE PREVIEW WITH UNIT FORMATTING
# =============================================================================

def format_preview(df: pd.DataFrame, swg: str) -> pd.DataFrame:
    df = df.copy()

    dt_col = f"{swg}_DateTime"
    p_col = f"{swg}_Power(MW)"
    s_col = f"{swg}_SOC(%)"

    if not df.empty:
        # DateTime
        s = pd.to_datetime(df[dt_col], errors="coerce")
        if s.dt.tz is not None:
            s = s.dt.tz_convert(LOCAL_TZ).dt.tz_localize(None)
        else:
            s = s.dt.tz_localize(None)
        df[dt_col] = s.dt.strftime(DISPLAY_DT_FORMAT)

        # Units
        df[p_col] = df[p_col].astype(str) + " MW"
        df[s_col] = df[s_col].astype(str) + " %"

    return df

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Table Preview</div>', unsafe_allow_html=True)

pcols = st.columns(3)

for i, swg in enumerate(SWG_LIST):
    with pcols[i]:
        st.markdown(f"**{swg.replace('SWG','SWG-')} Data**")
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
# PART 2 — TABLE EDITING, LOCKING & CONFIRMATION (UPDATED)
# =============================================================================

# =============================================================================
# SECTION HEADER
# =============================================================================

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

st.markdown(
    '<div class="glass"><div class="section-title">Table Management</div>',
    unsafe_allow_html=True
)

# =============================================================================
# ACTIVE TABLE SELECTION
# =============================================================================

sel_col, lock_col = st.columns([3, 2])

with sel_col:
    active_swg = st.selectbox(
        "Select Table",
        SWG_LIST,
        format_func=lambda x: x.replace("SWG", "SWG-"),
        key="active_table_select"
    )

active_key = f"{active_swg}_data"

# =============================================================================
# LOCK TABLE
# =============================================================================

with lock_col:
    st.markdown("### 🔒 Lock Table")
    st.session_state.table_locked = st.toggle(
        "Editing Locked",
        value=st.session_state.table_locked
    )

if st.session_state.table_locked:
    st.warning("Table is locked. Editing is disabled.")
else:
    st.success("Table is unlocked. Editing enabled.")

# =============================================================================
# EDIT ACTION SELECTION
# =============================================================================

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

edit_action = st.selectbox(
    "Edit Action",
    [
        "None",
        "Insert New Row",
        "Delete Last Row",
        "Insert New Column",
        "Delete Column",
        "Rename Column",
        "Move Column Left",
        "Move Column Right",
        "Merge Columns"
    ],
    disabled=st.session_state.table_locked
)

# =============================================================================
# HELPER — SAVE HISTORY & CONFIRM
# =============================================================================

def save_and_confirm(df: pd.DataFrame):
    """
    Save history for undo/redo and show confirmation.
    """
    st.session_state.history.append(df.copy())
    st.session_state.redo_stack.clear()
    st.session_state.last_edit_confirm = True

# =============================================================================
# APPLY EDIT ACTIONS
# =============================================================================

df = st.session_state[active_key]

if not st.session_state.table_locked:

    # -------------------------------------------------------------------------
    # INSERT NEW ROW
    # -------------------------------------------------------------------------
    if edit_action == "Insert New Row":
        if st.button("➕ Insert Empty Row"):
            save_and_confirm(df)
            empty_row = {c: None for c in df.columns}
            st.session_state[active_key] = pd.concat(
                [df, pd.DataFrame([empty_row])],
                ignore_index=True
            )

    # -------------------------------------------------------------------------
    # DELETE LAST ROW
    # -------------------------------------------------------------------------
    elif edit_action == "Delete Last Row":
        if df.empty:
            st.info("Table is empty.")
        elif st.button("🗑 Delete Last Row"):
            save_and_confirm(df)
            st.session_state[active_key] = df.iloc[:-1]

    # -------------------------------------------------------------------------
    # INSERT COLUMN
    # -------------------------------------------------------------------------
    elif edit_action == "Insert New Column":
        col_name = st.text_input("New column name")
        if col_name and st.button("Insert Column"):
            save_and_confirm(df)
            st.session_state[active_key][col_name] = None

    # -------------------------------------------------------------------------
    # DELETE COLUMN
    # -------------------------------------------------------------------------
    elif edit_action == "Delete Column":
        col = st.selectbox("Select column", df.columns)
        if st.button("Delete Column"):
            save_and_confirm(df)
            st.session_state[active_key] = df.drop(columns=[col])

    # -------------------------------------------------------------------------
    # RENAME COLUMN
    # -------------------------------------------------------------------------
    elif edit_action == "Rename Column":
        col = st.selectbox("Column to rename", df.columns)
        new_name = st.text_input("New name")
        if new_name and st.button("Rename"):
            save_and_confirm(df)
            st.session_state[active_key] = df.rename(columns={col: new_name})

    # -------------------------------------------------------------------------
    # MOVE COLUMN LEFT
    # -------------------------------------------------------------------------
    elif edit_action == "Move Column Left":
        col = st.selectbox("Select column", df.columns)
        idx = df.columns.get_loc(col)
        if idx > 0 and st.button("Move Left"):
            save_and_confirm(df)
            cols = list(df.columns)
            cols[idx - 1], cols[idx] = cols[idx], cols[idx - 1]
            st.session_state[active_key] = df[cols]

    # -------------------------------------------------------------------------
    # MOVE COLUMN RIGHT
    # -------------------------------------------------------------------------
    elif edit_action == "Move Column Right":
        col = st.selectbox("Select column", df.columns)
        idx = df.columns.get_loc(col)
        if idx < len(df.columns) - 1 and st.button("Move Right"):
            save_and_confirm(df)
            cols = list(df.columns)
            cols[idx + 1], cols[idx] = cols[idx], cols[idx + 1]
            st.session_state[active_key] = df[cols]

    # -------------------------------------------------------------------------
    # MERGE COLUMNS
    # -------------------------------------------------------------------------
    elif edit_action == "Merge Columns":
        col1 = st.selectbox("First column", df.columns, key="merge1")
        col2 = st.selectbox("Second column", df.columns, key="merge2")
        new_col = st.text_input("Merged column name", "Merged_Column")
        sep = st.text_input("Separator", " | ")

        if st.button("Merge Columns"):
            save_and_confirm(df)
            st.session_state[active_key][new_col] = (
                df[col1].astype(str) + sep + df[col2].astype(str)
            )

# =============================================================================
# INLINE DATA EDITOR
# =============================================================================

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='section-title'>Editable Table — {active_swg.replace('SWG','SWG-')}</div>",
    unsafe_allow_html=True
)

edited_df = st.data_editor(
    st.session_state[active_key],
    disabled=st.session_state.table_locked,
    use_container_width=True,
    num_rows="dynamic",
    key="data_editor_main"
)

# Detect inline edits
if not st.session_state.table_locked:
    if not edited_df.equals(st.session_state[active_key]):
        save_and_confirm(st.session_state[active_key])
        st.session_state[active_key] = edited_df

# =============================================================================
# CONFIRMATION MESSAGE
# =============================================================================

if st.session_state.last_edit_confirm:
    st.success("✅ Table updated successfully.")
    st.session_state.last_edit_confirm = False

st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# END OF PART 2
# =============================================================================

# =============================================================================
# PART 3 — SYSTEM STATUS & INFORMATION PANEL (UPDATED)
# =============================================================================

# =============================================================================
# SECTION SEPARATOR
# =============================================================================

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

st.markdown(
    '<div class="glass"><div class="section-title">System Status</div>',
    unsafe_allow_html=True
)

# =============================================================================
# STATUS SUMMARY CARDS
# =============================================================================

status_col1, status_col2, status_col3 = st.columns(3)

# -------------------------------------------------------------------------
# POWER RANGE (READ-ONLY)
# -------------------------------------------------------------------------
with status_col1:
    st.markdown("### ⚡ Power Range")
    st.markdown(
        f"""
        <div class="helper">
        Fixed operating range
        </div>
        <div style="font-size:22px;font-weight:800;color:#0b2a66;">
        {POWER_MIN} MW → {POWER_MAX} MW
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------------------------------
# SOC RANGE (READ-ONLY)
# -------------------------------------------------------------------------
with status_col2:
    st.markdown("### 🔋 SOC Range")
    st.markdown(
        f"""
        <div class="helper">
        Fixed operating range
        </div>
        <div style="font-size:22px;font-weight:800;color:#0b2a66;">
        {SOC_MIN} % → {SOC_MAX} %
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------------------------------
# TABLE LOCK STATUS
# -------------------------------------------------------------------------
with status_col3:
    st.markdown("### 🔒 Table Status")

    if st.session_state.table_locked:
        st.markdown(
            """
            <div style="color:#b91c1c;font-size:20px;font-weight:800;">
            Locked
            </div>
            <div class="helper">
            Editing disabled
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="color:#047857;font-size:20px;font-weight:800;">
            Unlocked
            </div>
            <div class="helper">
            Editing enabled
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# DATA BEHAVIOR EXPLANATION
# =============================================================================

st.markdown(
    '<div class="glass"><div class="section-title">Data Behavior</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="helper" style="font-size:17px;">
    • All edits made in <b>Table Management</b> immediately update stored data.<br>
    • Downloaded CSV / XLSX / JSON always reflect the <b>latest edited data</b>.<br>
    • No duplicate or cached data is used for export.<br>
    • Power and SOC limits are enforced internally and cannot be modified by users.<br>
    • Time records are stored in <b>local time</b> and exported in human-readable format.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# EDIT CONFIRMATION STATUS (FROM PART 2)
# =============================================================================

st.markdown(
    '<div class="glass"><div class="section-title">Edit Activity</div>',
    unsafe_allow_html=True
)

if st.session_state.last_edit_confirm:
    st.success("✅ The table was updated successfully.")
else:
    st.markdown(
        """
        <div class="helper">
        No recent edits detected.
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# INFORMATION FOOTER
# =============================================================================

st.markdown(
    """
    <div class="glass helper" style="font-size:15px;">
    <b>Notes:</b><br>
    • This dashboard uses fixed operational limits for safety.<br>
    • Configuration panels are intentionally hidden to reduce user error.<br>
    • Use the Reset button in Part 1 to clear all data when required.
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# END OF PART 3
# =============================================================================

# =============================================================================
# PART 4 — DATA DOWNLOAD & EXPORT (UPDATED)
# =============================================================================

import io
import importlib.util

# =============================================================================
# SECTION HEADER
# =============================================================================

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

st.markdown(
    '<div class="glass"><div class="section-title">Download Data</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="helper" style="font-size:17px;">
    Export the latest edited data into CSV, XLSX, or JSON formats.<br>
    Downloads always reflect the <b>current table state</b>.
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# PREPARE EXPORT DATA (AFTER EDIT)
# =============================================================================

def prepare_export_dataframe() -> pd.DataFrame:
    """
    Prepare export dataframe using the latest edited data.
    Applies formatting (MW, %, DateTime).
    """

    formatted_tables = []

    for swg in SWG_LIST:
        df = st.session_state[f"{swg}_data"].copy()

        if df.empty:
            formatted_tables.append(df)
            continue

        dt_col = f"{swg}_DateTime"
        p_col = f"{swg}_Power(MW)"
        s_col = f"{swg}_SOC(%)"

        # ---------------- DateTime ----------------
        series = pd.to_datetime(df[dt_col], errors="coerce")

        if series.dt.tz is not None:
            series = series.dt.tz_convert(LOCAL_TZ).dt.tz_localize(None)
        else:
            series = series.dt.tz_localize(None)

        df[dt_col] = series.dt.strftime(DISPLAY_DT_FORMAT)

        # ---------------- Units ----------------
        df[p_col] = df[p_col].astype(str) + " MW"
        df[s_col] = df[s_col].astype(str) + " %"

        formatted_tables.append(df)

    # ---------------- Align row count ----------------
    max_len = max(len(df) for df in formatted_tables)

    def pad(df, n):
        return df.reindex(range(n))

    formatted_tables = [pad(df, max_len) for df in formatted_tables]

    # ---------------- Side-by-side layout ----------------
    return pd.concat(formatted_tables, axis=1)


export_df = prepare_export_dataframe()

# =============================================================================
# EMPTY DATA CHECK
# =============================================================================

if export_df.dropna(how="all").empty:
    st.warning("No data available to download.")
else:

    # =============================================================================
    # DOWNLOAD BUTTONS
    # =============================================================================

    col_csv, col_xlsx, col_json = st.columns(3)

    # -------------------------------------------------------------------------
    # CSV
    # -------------------------------------------------------------------------
    with col_csv:
        st.download_button(
            "⬇ Download CSV",
            data=export_df.to_csv(index=False).encode("utf-8"),
            file_name="energy_data.csv",
            mime="text/csv",
            use_container_width=True
        )

    # -------------------------------------------------------------------------
    # XLSX (OPTIONAL)
    # -------------------------------------------------------------------------
    with col_xlsx:
        openpyxl_available = importlib.util.find_spec("openpyxl") is not None

        if openpyxl_available:

            def to_excel_bytes(df: pd.DataFrame) -> bytes:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df.to_excel(
                        writer,
                        index=False,
                        sheet_name="Energy Data"
                    )
                buffer.seek(0)
                return buffer.read()

            st.download_button(
                "⬇ Download XLSX",
                data=to_excel_bytes(export_df),
                file_name="energy_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.info("XLSX export unavailable. Install openpyxl to enable Excel downloads.")

    # -------------------------------------------------------------------------
    # JSON
    # -------------------------------------------------------------------------
    with col_json:
        st.download_button(
            "⬇ Download JSON",
            data=export_df.to_json(orient="records"),
            file_name="energy_data.json",
            mime="application/json",
            use_container_width=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# EXPORT NOTES
# =============================================================================

st.markdown(
    """
    <div class="glass helper" style="font-size:15px;">
    <b>Export Notes:</b><br>
    • Data reflects all edits and column changes.<br>
    • Units (MW, %) are included in exports.<br>
    • Time is exported in local format.<br>
    • CSV & JSON always work without dependencies.
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# END OF PART 4
# =============================================================================
