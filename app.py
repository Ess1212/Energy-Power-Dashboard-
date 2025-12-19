# =============================================================================
# ENERGY POWER DASHBOARD
# PART 1 — CORE UI + INPUT + TIMEZONE SAFE FOUNDATION
# =============================================================================

# =============================================================================
# IMPORTS (STANDARD + SAFE ONLY)
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Tuple, Dict

# =============================================================================
# PAGE CONFIG (MUST BE FIRST STREAMLIT COMMAND)
# =============================================================================

st.set_page_config(
    page_title="Energy Power Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# GLOBAL CONFIGURATION
# =============================================================================

APP_TITLE = "⚡ Energy Power Dashboard"

SWG_LIST = ["SWG1", "SWG2", "SWG3"]

DEFAULT_LIMITS: Dict[str, Dict[str, float]] = {
    "power": {"min": -200.0, "max": 200.0},
    "soc": {"min": 0.0, "max": 100.0}
}

# Local timezone — deployment safe
LOCAL_TZ = ZoneInfo("Asia/Phnom_Penh")

# Display format (UI + export consistency)
DISPLAY_DT_FORMAT = "%m/%d/%Y %I:%M:%S %p"

# =============================================================================
# GLOBAL CSS — WHITE GLASS UI
# =============================================================================

st.markdown(
    """
<style>
html, body {
    background-color: #f4f6fb;
    font-family: "Inter", sans-serif;
}

.glass {
    background: rgba(255,255,255,0.88);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}

.header {
    font-size: 34px;
    font-weight: 800;
    text-align: center;
    color: #0a1a44;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #0a1a44;
    margin-bottom: 12px;
}

.swg-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 8px;
}

.helper-text {
    font-size: 13px;
    color: #6b7280;
    margin-bottom: 8px;
}

.divider {
    height: 1px;
    background: #e5e7eb;
    margin: 16px 0;
}

button[kind="primary"] {
    background: linear-gradient(90deg, #0a1a44, #102a72);
    border-radius: 10px;
}
</style>
""",
    unsafe_allow_html=True
)

# =============================================================================
# APP HEADER
# =============================================================================

st.markdown(
    f'<div class="glass header">{APP_TITLE}</div>',
    unsafe_allow_html=True
)

# =============================================================================
# SESSION STATE INITIALIZATION (DEFENSIVE)
# =============================================================================

def init_session_state() -> None:
    """
    Initialize all required session variables safely.
    This function is rerun-safe and deployment-safe.
    """

    # Initialize SWG DataFrames
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

    # Validation limits
    if "limits" not in st.session_state:
        st.session_state.limits = {
            "power": DEFAULT_LIMITS["power"].copy(),
            "soc": DEFAULT_LIMITS["soc"].copy()
        }

    # Table lock (used in Part 2)
    if "table_locked" not in st.session_state:
        st.session_state.table_locked = False

    # Undo / Redo (used in Part 2)
    if "history" not in st.session_state:
        st.session_state.history = []

    if "redo_stack" not in st.session_state:
        st.session_state.redo_stack = []

init_session_state()

# =============================================================================
# RESET BUTTON (IMPORTANT AFTER DEPLOY)
# =============================================================================

with st.container():
    if st.button("🔄 Reset All Data (Clear Old Records)"):
        for swg in SWG_LIST:
            st.session_state[f"{swg}_data"] = (
                st.session_state[f"{swg}_data"].iloc[0:0]
            )
        st.success("All old records cleared. Please re-enter data.")

# =============================================================================
# VALIDATION LOGIC
# =============================================================================

def validate_input(power: float, soc: float) -> Tuple[bool, str]:
    """
    Validate Power and SOC values against limits.
    """

    if power is None or soc is None:
        return False, "Power and SOC are required."

    pmin = st.session_state.limits["power"]["min"]
    pmax = st.session_state.limits["power"]["max"]
    smin = st.session_state.limits["soc"]["min"]
    smax = st.session_state.limits["soc"]["max"]

    if power < pmin or power > pmax:
        return False, f"Power must be between {pmin} and {pmax} MW."

    if soc < smin or soc > smax:
        return False, f"SOC must be between {smin}% and {smax}%."

    return True, ""

# =============================================================================
# INSERT DATA (TIMEZONE SAFE — CLOUD PROOF)
# =============================================================================

def insert_swg_row(swg: str, power: float, soc: float) -> None:
    """
    Insert ONE row with local timezone.
    Safe for Streamlit Cloud and local runs.
    """

    now_local = datetime.now(tz=LOCAL_TZ)

    row = {
        f"{swg}_DateTime": now_local,
        f"{swg}_Power(MW)": float(power),
        f"{swg}_SOC(%)": float(soc)
    }

    st.session_state[f"{swg}_data"] = pd.concat(
        [
            st.session_state[f"{swg}_data"],
            pd.DataFrame([row])
        ],
        ignore_index=True
    )

# =============================================================================
# INPUT SECTION
# =============================================================================

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Input Data</div>', unsafe_allow_html=True)

input_cols = st.columns(3)

def render_swg_input(col, swg: str, label: str) -> None:
    with col:
        st.markdown(f'<div class="swg-title">{label}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="helper-text">Power (MW) and SOC (%) are required</div>',
            unsafe_allow_html=True
        )

        power = st.number_input(
            f"{label} Power (MW)",
            key=f"{swg}_power_input",
            step=1.0,
            format="%.2f"
        )

        soc = st.number_input(
            f"{label} SOC (%)",
            key=f"{swg}_soc_input",
            step=1.0,
            format="%.2f"
        )

        if st.button(f"Add {label}", use_container_width=True):
            ok, msg = validate_input(power, soc)
            if not ok:
                st.error(msg)
            else:
                insert_swg_row(swg, power, soc)
                st.success(f"{label} added successfully")

render_swg_input(input_cols[0], "SWG1", "SWG-1")
render_swg_input(input_cols[1], "SWG2", "SWG-2")
render_swg_input(input_cols[2], "SWG3", "SWG-3")

st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# TABLE PREVIEW (DISPLAY SAFE — NO UTC, NO +07:00)
# =============================================================================

def format_for_preview(df: pd.DataFrame, swg: str) -> pd.DataFrame:
    """
    Format DateTime column ONLY for display.
    Handles naive & aware datetimes safely.
    """

    df = df.copy()
    dt_col = f"{swg}_DateTime"

    if dt_col in df.columns and not df.empty:
        series = pd.to_datetime(df[dt_col], errors="coerce")

        # Safe timezone handling
        if series.dt.tz is not None:
            series = series.dt.tz_convert(LOCAL_TZ).dt.tz_localize(None)
        else:
            series = series.dt.tz_localize(None)

        df[dt_col] = series.dt.strftime(DISPLAY_DT_FORMAT)

    return df

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Table Preview</div>', unsafe_allow_html=True)

preview_cols = st.columns(3)

with preview_cols[0]:
    st.markdown("**SWG-1 Data**")
    st.dataframe(
        format_for_preview(st.session_state.SWG1_data, "SWG1"),
        use_container_width=True,
        hide_index=True
    )

with preview_cols[1]:
    st.markdown("**SWG-2 Data**")
    st.dataframe(
        format_for_preview(st.session_state.SWG2_data, "SWG2"),
        use_container_width=True,
        hide_index=True
    )

with preview_cols[2]:
    st.markdown("**SWG-3 Data**")
    st.dataframe(
        format_for_preview(st.session_state.SWG3_data, "SWG3"),
        use_container_width=True,
        hide_index=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# END OF PART 1
# =============================================================================

# =============================================================================
# PART 2 — TABLE MANAGEMENT & EDITING SYSTEM
# EXPANDED / PADDED / STREAMLIT-CLOUD SAFE
# =============================================================================

# =============================================================================
# SECTION: VISUAL SEPARATOR
# =============================================================================

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

st.markdown(
    '<div class="glass"><div class="section-title">Table Management</div>',
    unsafe_allow_html=True
)

# =============================================================================
# SECTION: ACTIVE TABLE SELECTION
# =============================================================================

"""
This section allows the user to select which SWG table
they want to edit, preview, or manage.

The selected table is referred to as the "active table".
"""

select_col, info_col = st.columns([2.5, 3.5])

with select_col:
    ACTIVE_SWG = st.selectbox(
        "Select SWG Table",
        options=SWG_LIST,
        format_func=lambda x: x.replace("SWG", "SWG-"),
        key="active_swg_selector"
    )

with info_col:
    st.markdown(
        """
        <div class="helper-text">
        Select a table to edit.  
        Locking prevents any modification.
        </div>
        """,
        unsafe_allow_html=True
    )

ACTIVE_KEY = f"{ACTIVE_SWG}_data"
ACTIVE_DF = st.session_state[ACTIVE_KEY]

# =============================================================================
# SECTION: LOCK TABLE TOGGLE
# =============================================================================

lock_col, spacer_col = st.columns([2, 6])

with lock_col:
    st.markdown("### 🔒 Lock Table")
    TABLE_LOCKED = st.toggle(
        "Table Locked",
        value=st.session_state.table_locked,
        key="table_lock_toggle"
    )
    st.session_state.table_locked = TABLE_LOCKED

with spacer_col:
    if TABLE_LOCKED:
        st.warning("Table is locked. Editing is disabled.")
    else:
        st.success("Table is unlocked. Editing enabled.")

# =============================================================================
# SECTION: UNDO / REDO CONTROLS
# =============================================================================

undo_col, redo_col, pad_col = st.columns([1.5, 1.5, 5])

def save_history_snapshot(df: pd.DataFrame) -> None:
    """
    Save a snapshot of the current table for undo.
    """
    st.session_state.history.append(df.copy())
    st.session_state.redo_stack.clear()

with undo_col:
    if st.button("↩ Undo", use_container_width=True):
        if st.session_state.history:
            st.session_state.redo_stack.append(
                st.session_state[ACTIVE_KEY].copy()
            )
            st.session_state[ACTIVE_KEY] = st.session_state.history.pop()
        else:
            st.info("Nothing to undo")

with redo_col:
    if st.button("↪ Redo", use_container_width=True):
        if st.session_state.redo_stack:
            st.session_state.history.append(
                st.session_state[ACTIVE_KEY].copy()
            )
            st.session_state[ACTIVE_KEY] = st.session_state.redo_stack.pop()
        else:
            st.info("Nothing to redo")

# =============================================================================
# SECTION: EDIT ACTION SELECTION
# =============================================================================

"""
The edit action dropdown determines which operation
the user wants to perform on the active table.
"""

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

edit_action = st.selectbox(
    "Edit Action",
    options=[
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
    disabled=TABLE_LOCKED,
    key="edit_action_selector"
)

# =============================================================================
# SECTION: ACTION IMPLEMENTATIONS
# =============================================================================

"""
Each action below is isolated, defensive,
and safe against empty tables.
"""

# -----------------------------------------------------------------------------
# INSERT NEW ROW
# -----------------------------------------------------------------------------
if edit_action == "Insert New Row" and not TABLE_LOCKED:
    st.markdown("### ➕ Insert New Row")

    if st.button("Insert Empty Row"):
        save_history_snapshot(ACTIVE_DF)
        empty_row = {col: None for col in ACTIVE_DF.columns}
        st.session_state[ACTIVE_KEY] = pd.concat(
            [ACTIVE_DF, pd.DataFrame([empty_row])],
            ignore_index=True
        )
        st.success("Empty row inserted")

# -----------------------------------------------------------------------------
# DELETE LAST ROW
# -----------------------------------------------------------------------------
elif edit_action == "Delete Last Row" and not TABLE_LOCKED:
    st.markdown("### ➖ Delete Last Row")

    if ACTIVE_DF.empty:
        st.warning("Table is empty")
    else:
        if st.button("Delete Last Row"):
            save_history_snapshot(ACTIVE_DF)
            st.session_state[ACTIVE_KEY] = ACTIVE_DF.iloc[:-1]
            st.success("Last row deleted")

# -----------------------------------------------------------------------------
# INSERT NEW COLUMN
# -----------------------------------------------------------------------------
elif edit_action == "Insert New Column" and not TABLE_LOCKED:
    st.markdown("### ➕ Insert New Column")

    new_col_name = st.text_input(
        "New column name",
        value=f"New_Column_{len(ACTIVE_DF.columns) + 1}"
    )

    if new_col_name:
        if st.button("Insert Column"):
            save_history_snapshot(ACTIVE_DF)
            st.session_state[ACTIVE_KEY][new_col_name] = None
            st.success(f"Column '{new_col_name}' inserted")

# -----------------------------------------------------------------------------
# DELETE COLUMN
# -----------------------------------------------------------------------------
elif edit_action == "Delete Column" and not TABLE_LOCKED:
    st.markdown("### 🗑 Delete Column")

    if len(ACTIVE_DF.columns) == 0:
        st.warning("No columns to delete")
    else:
        col_to_delete = st.selectbox(
            "Select column",
            ACTIVE_DF.columns
        )
        if st.button("Delete Column"):
            save_history_snapshot(ACTIVE_DF)
            st.session_state[ACTIVE_KEY] = ACTIVE_DF.drop(columns=[col_to_delete])
            st.success(f"Column '{col_to_delete}' deleted")

# -----------------------------------------------------------------------------
# RENAME COLUMN
# -----------------------------------------------------------------------------
elif edit_action == "Rename Column" and not TABLE_LOCKED:
    st.markdown("### ✏ Rename Column")

    col_to_rename = st.selectbox("Select column", ACTIVE_DF.columns)
    new_name = st.text_input("New column name")

    if new_name:
        if st.button("Rename Column"):
            save_history_snapshot(ACTIVE_DF)
            st.session_state[ACTIVE_KEY] = ACTIVE_DF.rename(
                columns={col_to_rename: new_name}
            )
            st.success("Column renamed")

# -----------------------------------------------------------------------------
# MOVE COLUMN LEFT
# -----------------------------------------------------------------------------
elif edit_action == "Move Column Left" and not TABLE_LOCKED:
    st.markdown("### ⬅ Move Column Left")

    col = st.selectbox("Select column", ACTIVE_DF.columns)
    idx = ACTIVE_DF.columns.get_loc(col)

    if idx == 0:
        st.warning("Column already at leftmost position")
    else:
        if st.button("Move Left"):
            save_history_snapshot(ACTIVE_DF)
            cols = list(ACTIVE_DF.columns)
            cols[idx - 1], cols[idx] = cols[idx], cols[idx - 1]
            st.session_state[ACTIVE_KEY] = ACTIVE_DF[cols]
            st.success("Column moved left")

# -----------------------------------------------------------------------------
# MOVE COLUMN RIGHT
# -----------------------------------------------------------------------------
elif edit_action == "Move Column Right" and not TABLE_LOCKED:
    st.markdown("### ➡ Move Column Right")

    col = st.selectbox("Select column", ACTIVE_DF.columns)
    idx = ACTIVE_DF.columns.get_loc(col)

    if idx == len(ACTIVE_DF.columns) - 1:
        st.warning("Column already at rightmost position")
    else:
        if st.button("Move Right"):
            save_history_snapshot(ACTIVE_DF)
            cols = list(ACTIVE_DF.columns)
            cols[idx + 1], cols[idx] = cols[idx], cols[idx + 1]
            st.session_state[ACTIVE_KEY] = ACTIVE_DF[cols]
            st.success("Column moved right")

# -----------------------------------------------------------------------------
# MERGE COLUMNS
# -----------------------------------------------------------------------------
elif edit_action == "Merge Columns" and not TABLE_LOCKED:
    st.markdown("### 🔀 Merge Columns")

    col1 = st.selectbox("First column", ACTIVE_DF.columns, key="merge_col_1")
    col2 = st.selectbox("Second column", ACTIVE_DF.columns, key="merge_col_2")
    merged_name = st.text_input("Merged column name", "Merged_Column")
    separator = st.text_input("Separator", " | ")

    if st.button("Merge Columns"):
        save_history_snapshot(ACTIVE_DF)
        st.session_state[ACTIVE_KEY][merged_name] = (
            ACTIVE_DF[col1].astype(str) + separator + ACTIVE_DF[col2].astype(str)
        )
        st.success("Columns merged")

# =============================================================================
# SECTION: LIVE EDITABLE TABLE VIEW
# =============================================================================

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

st.markdown(
    f"<div class='section-title'>Editable Table — {ACTIVE_SWG.replace('SWG','SWG-')}</div>",
    unsafe_allow_html=True
)

st.data_editor(
    st.session_state[ACTIVE_KEY],
    use_container_width=True,
    disabled=TABLE_LOCKED,
    num_rows="dynamic",
    key="active_data_editor"
)

st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# END OF PART 2
# =============================================================================

# =============================================================================
# PART 3 — SETTINGS, LIMITS & VALIDATION SYSTEM
# PADDED / EXPANDED / STREAMLIT-CLOUD SAFE
# =============================================================================

# =============================================================================
# SECTION: VISUAL SEPARATOR
# =============================================================================

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

st.markdown(
    '<div class="glass"><div class="section-title">Settings & Constraints</div>',
    unsafe_allow_html=True
)

# =============================================================================
# SECTION: INTRODUCTORY TEXT
# =============================================================================

st.markdown(
    """
    <div class="helper-text">
    Configure input constraints for Power and State of Charge (SOC).  
    These settings affect <b>new data entry only</b>.  
    Existing records are preserved and validated separately.
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# SECTION: SETTINGS LAYOUT
# =============================================================================

power_col, soc_col = st.columns(2)

# =============================================================================
# SECTION: POWER LIMIT SETTINGS
# =============================================================================

with power_col:
    st.markdown("### ⚡ Power Input Limits (MW)")

    st.markdown(
        '<div class="helper-text">Define allowable Power range</div>',
        unsafe_allow_html=True
    )

    # Current values
    current_power_min = st.session_state.limits["power"]["min"]
    current_power_max = st.session_state.limits["power"]["max"]

    # Inputs
    power_min = st.number_input(
        "Minimum Power (MW)",
        value=float(current_power_min),
        step=1.0,
        format="%.2f",
        key="settings_power_min"
    )

    power_max = st.number_input(
        "Maximum Power (MW)",
        value=float(current_power_max),
        step=1.0,
        format="%.2f",
        key="settings_power_max"
    )

    # Action buttons
    p_btn_apply, p_btn_reset = st.columns(2)

    with p_btn_apply:
        if st.button("Apply Power Limits", use_container_width=True):
            if power_min >= power_max:
                st.error("Minimum Power must be less than Maximum Power.")
            else:
                st.session_state.limits["power"]["min"] = power_min
                st.session_state.limits["power"]["max"] = power_max
                st.success("Power limits updated successfully.")

    with p_btn_reset:
        if st.button("Reset Power Limits", use_container_width=True):
            st.session_state.limits["power"] = DEFAULT_LIMITS["power"].copy()
            st.success("Power limits reset to default.")

# =============================================================================
# SECTION: SOC LIMIT SETTINGS
# =============================================================================

with soc_col:
    st.markdown("### 🔋 SOC Input Limits (%)")

    st.markdown(
        '<div class="helper-text">Define allowable SOC range</div>',
        unsafe_allow_html=True
    )

    # Current values
    current_soc_min = st.session_state.limits["soc"]["min"]
    current_soc_max = st.session_state.limits["soc"]["max"]

    # Inputs
    soc_min = st.number_input(
        "Minimum SOC (%)",
        value=float(current_soc_min),
        step=1.0,
        format="%.2f",
        key="settings_soc_min"
    )

    soc_max = st.number_input(
        "Maximum SOC (%)",
        value=float(current_soc_max),
        step=1.0,
        format="%.2f",
        key="settings_soc_max"
    )

    # Action buttons
    s_btn_apply, s_btn_reset = st.columns(2)

    with s_btn_apply:
        if st.button("Apply SOC Limits", use_container_width=True):
            if soc_min >= soc_max:
                st.error("Minimum SOC must be less than Maximum SOC.")
            else:
                st.session_state.limits["soc"]["min"] = soc_min
                st.session_state.limits["soc"]["max"] = soc_max
                st.success("SOC limits updated successfully.")

    with s_btn_reset:
        if st.button("Reset SOC Limits", use_container_width=True):
            st.session_state.limits["soc"] = DEFAULT_LIMITS["soc"].copy()
            st.success("SOC limits reset to default.")

st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# SECTION: ACTIVE LIMIT SUMMARY
# =============================================================================

st.markdown(
    '<div class="glass"><div class="section-title">Active Limit Summary</div>',
    unsafe_allow_html=True
)

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.metric(
        label="Power Range (MW)",
        value=f"{st.session_state.limits['power']['min']} → {st.session_state.limits['power']['max']}"
    )

with summary_col2:
    st.metric(
        label="SOC Range (%)",
        value=f"{st.session_state.limits['soc']['min']} → {st.session_state.limits['soc']['max']}"
    )

st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# SECTION: EXISTING DATA VALIDATION CHECK
# =============================================================================

st.markdown(
    '<div class="glass"><div class="section-title">Existing Data Validation</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="helper-text">
    This check scans existing tables and warns if values fall outside
    the currently configured limits.  
    No data is modified automatically.
    </div>
    """,
    unsafe_allow_html=True
)

def check_existing_data_violations() -> None:
    """
    Scan all SWG tables for values outside current limits.
    """

    for swg in SWG_LIST:
        df = st.session_state[f"{swg}_data"]

        if df.empty:
            continue

        p_col = f"{swg}_Power(MW)"
        s_col = f"{swg}_SOC(%)"

        power_violation = (
            (df[p_col] < st.session_state.limits["power"]["min"]).any()
            or (df[p_col] > st.session_state.limits["power"]["max"]).any()
        )

        soc_violation = (
            (df[s_col] < st.session_state.limits["soc"]["min"]).any()
            or (df[s_col] > st.session_state.limits["soc"]["max"]).any()
        )

        if power_violation or soc_violation:
            st.warning(
                f"⚠️ {swg.replace('SWG','SWG-')} contains values outside current limits."
            )
            return

    st.success("All existing data is within the current limits.")

check_existing_data_violations()

st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# SECTION: INFORMATIONAL FOOTER
# =============================================================================

st.markdown(
    """
    <div class="glass helper-text">
    <b>Notes:</b><br>
    • Limits affect only new input entries.<br>
    • Editing tables may bypass limits (intentional).<br>
    • Downloaded data reflects actual stored values.<br>
    • Use the Reset button in Part 1 if migrating old data.
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# END OF PART 3
# =============================================================================

# =============================================================================
# PART 4 — DATA DOWNLOAD & EXPORT SYSTEM
# PADDED / EXPANDED / STREAMLIT-CLOUD SAFE
# =============================================================================

# =============================================================================
# IMPORTS (SAFE & STANDARD ONLY)
# =============================================================================

import io
import importlib.util

# =============================================================================
# SECTION: VISUAL SEPARATOR
# =============================================================================

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

st.markdown(
    '<div class="glass"><div class="section-title">Download Data</div>',
    unsafe_allow_html=True
)

# =============================================================================
# SECTION: INTRODUCTORY TEXT
# =============================================================================

st.markdown(
    """
    <div class="helper-text">
    Export all recorded data into CSV, XLSX, or JSON formats.  
    • CSV and JSON are always available  
    • XLSX is available only if <b>openpyxl</b> exists on the server  
    • DateTime is exported in local time (human-readable)  
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# SECTION: EXPORT DATA PREPARATION
# =============================================================================

def prepare_export_dataframe() -> pd.DataFrame:
    """
    Prepare a combined export DataFrame.

    - Combines SWG1 / SWG2 / SWG3 side-by-side
    - Safely handles timezone-aware and naive datetimes
    - Formats DateTime as MM/DD/YYYY HH:MM:SS AM/PM
    - Does NOT mutate session state
    """

    prepared_tables = []

    # -------------------------------------------------------------------------
    # LOOP THROUGH EACH SWG TABLE
    # -------------------------------------------------------------------------
    for swg in SWG_LIST:
        df = st.session_state[f"{swg}_data"].copy()
        dt_col = f"{swg}_DateTime"

        # ---------------------------------------------------------------------
        # SAFE DATETIME HANDLING (CLOUD + LOCAL)
        # ---------------------------------------------------------------------
        if dt_col in df.columns and not df.empty:
            series = pd.to_datetime(df[dt_col], errors="coerce")

            # Handle timezone-aware vs naive safely
            if series.dt.tz is not None:
                series = (
                    series
                    .dt.tz_convert(LOCAL_TZ)
                    .dt.tz_localize(None)
                )
            else:
                series = series.dt.tz_localize(None)

            df[dt_col] = series.dt.strftime(DISPLAY_DT_FORMAT)

        prepared_tables.append(df)

    # -------------------------------------------------------------------------
    # PAD TABLES TO SAME LENGTH
    # -------------------------------------------------------------------------
    max_len = max(len(df) for df in prepared_tables) if prepared_tables else 0

    def pad_table(df: pd.DataFrame, length: int) -> pd.DataFrame:
        return df.reindex(range(length))

    prepared_tables = [pad_table(df, max_len) for df in prepared_tables]

    # -------------------------------------------------------------------------
    # COMBINE SIDE-BY-SIDE (EXCEL STYLE)
    # -------------------------------------------------------------------------
    return pd.concat(prepared_tables, axis=1)


export_df = prepare_export_dataframe()

# =============================================================================
# SECTION: EMPTY DATA CHECK
# =============================================================================

if export_df.dropna(how="all").empty:
    st.warning("No data available to download yet.")
else:

    # =========================================================================
    # DOWNLOAD BUTTON LAYOUT
    # =========================================================================

    csv_col, xlsx_col, json_col = st.columns(3)

    # =========================================================================
    # CSV DOWNLOAD (ALWAYS AVAILABLE)
    # =========================================================================

    with csv_col:
        csv_bytes = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇ Download CSV",
            data=csv_bytes,
            file_name="energy_data.csv",
            mime="text/csv",
            use_container_width=True
        )

    # =========================================================================
    # XLSX DOWNLOAD (ONLY IF openpyxl EXISTS)
    # =========================================================================

    with xlsx_col:
        openpyxl_available = importlib.util.find_spec("openpyxl") is not None

        if openpyxl_available:

            def export_to_excel_bytes(df: pd.DataFrame) -> bytes:
                """
                Export DataFrame to XLSX safely.
                """
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
                label="⬇ Download XLSX",
                data=export_to_excel_bytes(export_df),
                file_name="energy_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.info(
                "XLSX export unavailable. "
                "Install openpyxl to enable Excel downloads."
            )

    # =========================================================================
    # JSON DOWNLOAD (ALWAYS AVAILABLE)
    # =========================================================================

    with json_col:
        json_str = export_df.to_json(
            orient="records",
            date_format="iso"
        )
        st.download_button(
            label="⬇ Download JSON",
            data=json_str,
            file_name="energy_data.json",
            mime="application/json",
            use_container_width=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# SECTION: FOOTER NOTES
# =============================================================================

st.markdown(
    """
    <div class="glass helper-text">
    <b>Export Notes:</b><br>
    • Export uses formatted local time (no UTC, no +07:00).<br>
    • Old records created before timezone fixes should be cleared.<br>
    • CSV and JSON do not require extra dependencies.<br>
    • XLSX requires <code>openpyxl</code> on the server.
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# END OF PART 4
# =============================================================================
