# ============================================================
# ENERGY POWER DASHBOARD
# PART 1 — CORE FOUNDATION (EXPANDED VERSION)
# ============================================================

# ----------------------------
# IMPORTS
# ----------------------------
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Tuple

# ----------------------------
# PAGE CONFIGURATION
# ----------------------------
st.set_page_config(
    page_title="Energy Power Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------
# GLOBAL CONSTANTS
# ----------------------------
SWG_LIST = ["SWG1", "SWG2", "SWG3"]

DEFAULT_LIMITS = {
    "power": {"min": -200.0, "max": 200.0},
    "soc": {"min": 0.0, "max": 100.0}
}

# ----------------------------
# WHITE GLASS UI (GLOBAL CSS)
# ----------------------------
st.markdown("""
<style>
body {
    background-color: #f4f6fb;
}
.glass {
    background: rgba(255, 255, 255, 0.82);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 22px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.08);
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
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# HEADER
# ----------------------------
st.markdown(
    '<div class="glass header">⚡ Energy Power Dashboard</div>',
    unsafe_allow_html=True
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

def initialize_session_state() -> None:
    """
    Initialize all session state variables.
    This ensures app stability across reruns.
    """
    # DataFrames for each SWG
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

    # Input limits
    if "limits" not in st.session_state:
        st.session_state.limits = DEFAULT_LIMITS.copy()

    # Lock flag (used in Part 2)
    if "table_locked" not in st.session_state:
        st.session_state.table_locked = False

    # Undo / Redo stacks (used in Part 2)
    if "history" not in st.session_state:
        st.session_state.history = []

    if "redo_stack" not in st.session_state:
        st.session_state.redo_stack = []

initialize_session_state()

# ============================================================
# VALIDATION LOGIC
# ============================================================

def validate_input(power: float, soc: float) -> Tuple[bool, str]:
    """
    Validate Power and SOC against limits.
    Returns (is_valid, error_message)
    """
    if power is None or soc is None:
        return False, "Power and SOC must be provided"

    # Power check
    p_min = st.session_state.limits["power"]["min"]
    p_max = st.session_state.limits["power"]["max"]
    if not (p_min <= power <= p_max):
        return False, f"Power must be between {p_min} and {p_max} MW"

    # SOC check
    s_min = st.session_state.limits["soc"]["min"]
    s_max = st.session_state.limits["soc"]["max"]
    if not (s_min <= soc <= s_max):
        return False, f"SOC must be between {s_min}% and {s_max}%"

    return True, ""

# ============================================================
# DATA INSERTION LOGIC (FIXED: 1 ROW ONLY)
# ============================================================

def insert_swg_row(swg: str, power: float, soc: float) -> None:
    """
    Insert ONE row into the selected SWG table.
    """
    now = datetime.now()

    new_row = pd.DataFrame(
        [{
            f"{swg}_DateTime": now,
            f"{swg}_Power(MW)": float(power),
            f"{swg}_SOC(%)": float(soc)
        }]
    )

    st.session_state[f"{swg}_data"] = pd.concat(
        [st.session_state[f"{swg}_data"], new_row],
        ignore_index=True
    )

# ============================================================
# INPUT UI
# ============================================================

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Input Data</div>', unsafe_allow_html=True)

input_cols = st.columns(3)

def render_swg_input(column, swg: str, label: str) -> None:
    """
    Render input controls for a single SWG.
    """
    with column:
        st.markdown(f'<div class="swg-title">{label}</div>', unsafe_allow_html=True)

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
            valid, error = validate_input(power, soc)
            if not valid:
                st.error(error)
            else:
                insert_swg_row(swg, power, soc)
                st.success(f"{label} record added")

render_swg_input(input_cols[0], "SWG1", "SWG-1")
render_swg_input(input_cols[1], "SWG2", "SWG-2")
render_swg_input(input_cols[2], "SWG3", "SWG-3")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TABLE PREVIEW (READ-ONLY)
# ============================================================

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Table Preview</div>', unsafe_allow_html=True)

preview_cols = st.columns(3)

with preview_cols[0]:
    st.markdown("**SWG-1 Data**")
    st.dataframe(
        st.session_state.SWG1_data,
        use_container_width=True,
        hide_index=True
    )

with preview_cols[1]:
    st.markdown("**SWG-2 Data**")
    st.dataframe(
        st.session_state.SWG2_data,
        use_container_width=True,
        hide_index=True
    )

with preview_cols[2]:
    st.markdown("**SWG-3 Data**")
    st.dataframe(
        st.session_state.SWG3_data,
        use_container_width=True,
        hide_index=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PART 2 — TABLE EDITING, LOCK, UNDO / REDO (EXPANDED)
# ============================================================

# ----------------------------
# SECTION HEADER
# ----------------------------
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Table Management</div>', unsafe_allow_html=True)

# ----------------------------
# CONTROL ROW
# ----------------------------
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2, 3, 1.5, 1.5])

# ----------------------------
# SELECT ACTIVE SWG TABLE
# ----------------------------
with ctrl_col1:
    active_swg = st.selectbox(
        "Select SWG Table",
        options=SWG_LIST,
        format_func=lambda x: x.replace("SWG", "SWG-")
    )

active_df_key = f"{active_swg}_data"
active_df = st.session_state[active_df_key]

# ----------------------------
# EDIT ACTION SELECTOR
# ----------------------------
with ctrl_col2:
    edit_action = st.selectbox(
        "Edit Table",
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

# ----------------------------
# LOCK TABLE TOGGLE
# ----------------------------
with ctrl_col3:
    st.markdown("#### Lock Table")
    st.session_state.table_locked = st.toggle(
        "Locked",
        value=st.session_state.table_locked
    )

# ----------------------------
# UNDO / REDO
# ----------------------------
with ctrl_col4:
    if st.button("↩ Undo", use_container_width=True):
        if st.session_state.history:
            st.session_state.redo_stack.append(
                st.session_state[active_df_key].copy()
            )
            st.session_state[active_df_key] = st.session_state.history.pop()

    if st.button("↪ Redo", use_container_width=True):
        if st.session_state.redo_stack:
            st.session_state.history.append(
                st.session_state[active_df_key].copy()
            )
            st.session_state[active_df_key] = st.session_state.redo_stack.pop()

# ----------------------------
# APPLY EDIT ACTIONS
# ----------------------------
def save_history():
    st.session_state.history.append(active_df.copy())
    st.session_state.redo_stack.clear()

if not st.session_state.table_locked and edit_action != "None":

    # ========================
    # INSERT ROW
    # ========================
    if edit_action == "Insert New Row":
        save_history()
        empty_row = pd.DataFrame(
            [{col: None for col in active_df.columns}]
        )
        st.session_state[active_df_key] = pd.concat(
            [active_df, empty_row],
            ignore_index=True
        )

    # ========================
    # DELETE LAST ROW
    # ========================
    elif edit_action == "Delete Last Row":
        if len(active_df) > 0:
            save_history()
            st.session_state[active_df_key] = active_df.iloc[:-1]

    # ========================
    # INSERT COLUMN
    # ========================
    elif edit_action == "Insert New Column":
        new_col_name = st.text_input(
            "New Column Name",
            value=f"New_Column_{len(active_df.columns)+1}"
        )
        if new_col_name and st.button("Insert Column"):
            save_history()
            st.session_state[active_df_key][new_col_name] = None

    # ========================
    # DELETE COLUMN
    # ========================
    elif edit_action == "Delete Column":
        col_to_delete = st.selectbox(
            "Select column to delete",
            options=active_df.columns
        )
        if st.button("Confirm Delete"):
            save_history()
            st.session_state[active_df_key] = active_df.drop(columns=[col_to_delete])

    # ========================
    # RENAME COLUMN
    # ========================
    elif edit_action == "Rename Column":
        col_to_rename = st.selectbox(
            "Select column",
            options=active_df.columns
        )
        new_name = st.text_input("New column name")
        if new_name and st.button("Rename"):
            save_history()
            st.session_state[active_df_key] = active_df.rename(
                columns={col_to_rename: new_name}
            )

    # ========================
    # MOVE COLUMN LEFT
    # ========================
    elif edit_action == "Move Column Left":
        col = st.selectbox("Select column", active_df.columns)
        idx = active_df.columns.get_loc(col)
        if idx > 0 and st.button("Move Left"):
            save_history()
            cols = list(active_df.columns)
            cols[idx - 1], cols[idx] = cols[idx], cols[idx - 1]
            st.session_state[active_df_key] = active_df[cols]

    # ========================
    # MOVE COLUMN RIGHT
    # ========================
    elif edit_action == "Move Column Right":
        col = st.selectbox("Select column", active_df.columns)
        idx = active_df.columns.get_loc(col)
        if idx < len(active_df.columns) - 1 and st.button("Move Right"):
            save_history()
            cols = list(active_df.columns)
            cols[idx + 1], cols[idx] = cols[idx], cols[idx + 1]
            st.session_state[active_df_key] = active_df[cols]

    # ========================
    # MERGE COLUMNS
    # ========================
    elif edit_action == "Merge Columns":
        col_a = st.selectbox("First column", active_df.columns, key="merge_a")
        col_b = st.selectbox("Second column", active_df.columns, key="merge_b")
        merged_name = st.text_input("Merged column name", "Merged_Column")
        separator = st.text_input("Separator", " | ")

        if st.button("Merge Columns"):
            save_history()
            st.session_state[active_df_key][merged_name] = (
                active_df[col_a].astype(str)
                + separator
                + active_df[col_b].astype(str)
            )

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# LIVE EDITABLE TABLE VIEW
# ============================================================

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown(
    f'<div class="section-title">Editable Table — {active_swg.replace("SWG","SWG-")}</div>',
    unsafe_allow_html=True
)

st.data_editor(
    st.session_state[active_df_key],
    use_container_width=True,
    disabled=st.session_state.table_locked,
    num_rows="dynamic"
)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PART 3 — SETTINGS & INPUT LIMIT MANAGEMENT (EXPANDED)
# ============================================================

# ----------------------------
# SETTINGS HEADER
# ----------------------------
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Settings</div>', unsafe_allow_html=True)

# ----------------------------
# LAYOUT
# ----------------------------
set_col1, set_col2 = st.columns(2)

# ============================================================
# POWER LIMIT SETTINGS
# ============================================================
with set_col1:
    st.markdown("### ⚡ Power Input Limits (MW)")

    current_pmin = st.session_state.limits["power"]["min"]
    current_pmax = st.session_state.limits["power"]["max"]

    power_min = st.number_input(
        "Minimum Power",
        value=float(current_pmin),
        step=1.0,
        format="%.2f",
        key="power_min_setting"
    )

    power_max = st.number_input(
        "Maximum Power",
        value=float(current_pmax),
        step=1.0,
        format="%.2f",
        key="power_max_setting"
    )

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        if st.button("Apply Power Limit", use_container_width=True):
            if power_min >= power_max:
                st.error("Minimum Power must be less than Maximum Power")
            else:
                st.session_state.limits["power"]["min"] = power_min
                st.session_state.limits["power"]["max"] = power_max
                st.success("Power limits updated")

    with col_p2:
        if st.button("Reset Power Limit", use_container_width=True):
            st.session_state.limits["power"] = DEFAULT_LIMITS["power"].copy()
            st.success("Power limits reset to default")

# ============================================================
# SOC LIMIT SETTINGS
# ============================================================
with set_col2:
    st.markdown("### 🔋 SOC Input Limits (%)")

    current_smin = st.session_state.limits["soc"]["min"]
    current_smax = st.session_state.limits["soc"]["max"]

    soc_min = st.number_input(
        "Minimum SOC",
        value=float(current_smin),
        step=1.0,
        format="%.2f",
        key="soc_min_setting"
    )

    soc_max = st.number_input(
        "Maximum SOC",
        value=float(current_smax),
        step=1.0,
        format="%.2f",
        key="soc_max_setting"
    )

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        if st.button("Apply SOC Limit", use_container_width=True):
            if soc_min >= soc_max:
                st.error("Minimum SOC must be less than Maximum SOC")
            else:
                st.session_state.limits["soc"]["min"] = soc_min
                st.session_state.limits["soc"]["max"] = soc_max
                st.success("SOC limits updated")

    with col_s2:
        if st.button("Reset SOC Limit", use_container_width=True):
            st.session_state.limits["soc"] = DEFAULT_LIMITS["soc"].copy()
            st.success("SOC limits reset to default")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# ACTIVE LIMIT SUMMARY (READ-ONLY)
# ============================================================

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Active Input Constraints</div>', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# VALIDATION WARNING (GLOBAL)
# ============================================================

def show_global_validation_warning():
    """
    Warn user if existing data violates new limits.
    """
    violations = False

    for swg in SWG_LIST:
        df = st.session_state[f"{swg}_data"]
        if df.empty:
            continue

        p_col = f"{swg}_Power(MW)"
        s_col = f"{swg}_SOC(%)"

        if (
            (df[p_col] < st.session_state.limits["power"]["min"]).any()
            or (df[p_col] > st.session_state.limits["power"]["max"]).any()
            or (df[s_col] < st.session_state.limits["soc"]["min"]).any()
            or (df[s_col] > st.session_state.limits["soc"]["max"]).any()
        ):
            violations = True
            break

    if violations:
        st.warning(
            "⚠️ Some existing table values are outside the current limits. "
            "You may want to review or edit the data."
        )

show_global_validation_warning()

# ============================================================
# PART 4 — DATA EXPORT (CSV / XLSX / JSON)
# DATE FORMAT FIXED: MM/DD/YYYY h:mm:ss AM/PM
# ============================================================

import io

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Download Data</div>', unsafe_allow_html=True)

# ============================================================
# PREPARE EXPORT DATAFRAME
# ============================================================

def prepare_export_dataframe() -> pd.DataFrame:
    """
    Combine SWG1, SWG2, SWG3 tables side-by-side
    and format DateTime columns for export.
    """
    df1 = st.session_state.SWG1_data.copy()
    df2 = st.session_state.SWG2_data.copy()
    df3 = st.session_state.SWG3_data.copy()

    # Ensure equal row length
    max_len = max(len(df1), len(df2), len(df3))

    def pad(df: pd.DataFrame, length: int) -> pd.DataFrame:
        return df.reindex(range(length))

    df1 = pad(df1, max_len)
    df2 = pad(df2, max_len)
    df3 = pad(df3, max_len)

    # -------- FORMAT DATETIME COLUMNS --------
    def format_dt(df: pd.DataFrame, swg: str) -> pd.DataFrame:
        dt_col = f"{swg}_DateTime"
        if dt_col in df.columns:
            df[dt_col] = pd.to_datetime(
                df[dt_col],
                errors="coerce"
            ).dt.strftime("%m/%d/%Y %I:%M:%S %p")
        return df

    df1 = format_dt(df1, "SWG1")
    df2 = format_dt(df2, "SWG2")
    df3 = format_dt(df3, "SWG3")

    # Combine side-by-side (Excel layout)
    combined_df = pd.concat([df1, df2, df3], axis=1)

    return combined_df

export_df = prepare_export_dataframe()

# ============================================================
# EMPTY DATA CHECK
# ============================================================

if export_df.dropna(how="all").empty:
    st.warning("No data available to download.")
else:

    dcol1, dcol2, dcol3 = st.columns(3)

    # ========================================================
    # CSV DOWNLOAD
    # ========================================================
    with dcol1:
        csv_data = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇ Download CSV",
            data=csv_data,
            file_name="energy_data.csv",
            mime="text/csv",
            use_container_width=True
        )

    # ========================================================
    # XLSX DOWNLOAD (ROBUST & SAFE)
    # ========================================================
    with dcol2:

        def to_excel_bytes(df: pd.DataFrame) -> bytes:
            buffer = io.BytesIO()
            try:
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df.to_excel(
                        writer,
                        index=False,
                        sheet_name="Energy Data"
                    )
            except Exception:
                # Fallback if openpyxl is not installed
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    df.to_excel(
                        writer,
                        index=False,
                        sheet_name="Energy Data"
                    )

            buffer.seek(0)
            return buffer.read()

        st.download_button(
            label="⬇ Download XLSX",
            data=to_excel_bytes(export_df),
            file_name="energy_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # ========================================================
    # JSON DOWNLOAD
    # ========================================================
    with dcol3:
        json_data = export_df.to_json(
            orient="records",
            date_format="iso"
        )
        st.download_button(
            label="⬇ Download JSON",
            data=json_data,
            file_name="energy_data.json",
            mime="application/json",
            use_container_width=True
        )

st.markdown('</div>', unsafe_allow_html=True)
