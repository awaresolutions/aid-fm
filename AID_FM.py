"""
AI Data Center Financial & Power Procurement Modeling System (AID_FM)
Main Application Entry Point with Password Authentication & Streamlit Cloud Secrets Support.
"""

import streamlit as st
import pandas as pd

# Page config
st.set_page_config(
    page_title="AI Data Center Financial Model",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config import CUSTOM_CSS, APP_TITLE, APP_SUBTITLE
from views.tab_chip_config import render_tab_chip_config
from views.tab_power_plan import render_tab_power_plan
from views.tab_map_view import render_tab_map_view
from views.tab_financials import render_tab_financials
from views.tab_token_economics import render_tab_token_economics
from views.tab_export import render_tab_export
from data.ts_locations import get_all_locations

# Inject custom styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------------------------------------------
# PASSWORD AUTHENTICATION SYSTEM
# ----------------------------------------------------
def check_password():
    """Returns `True` if the user has entered the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # Safely fetch password from Streamlit secrets or fallback default
        try:
            target_password = st.secrets["password"]
        except Exception:
            target_password = "AID2026!"

        if st.session_state.get("password_input", "") == target_password:
            st.session_state["password_correct"] = True
            if "password_input" in st.session_state:
                del st.session_state["password_input"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown(f"""
        <div class="app-header" style="max-width: 550px; margin: 40px auto 20px auto; text-align: center;">
            <div class="app-title">🔒 Secure Access Prompt</div>
            <div class="app-subtitle">{APP_TITLE}</div>
        </div>
        """, unsafe_allow_html=True)

        col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
        with col_l2:
            st.markdown("""
            <div class="metric-card" style="margin-bottom: 20px;">
                <div class="metric-title" style="color: #1e3a8a;">Authentication Required</div>
                <div style="font-size: 0.95rem; color: #334155; margin-top: 6px;">
                    Please enter the authorized access password to unlock the AI Data Center Financial Model.
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.text_input(
                "Access Password",
                type="password",
                on_change=password_entered,
                key="password_input",
                placeholder="Enter password..."
            )
            st.caption("💡 Default password: `AID2026!` (Can be overridden in `.streamlit/secrets.toml` or Streamlit Cloud Secrets).")
        return False

    elif not st.session_state["password_correct"]:
        st.markdown(f"""
        <div class="app-header" style="max-width: 550px; margin: 40px auto 20px auto; text-align: center;">
            <div class="app-title">🔒 Secure Access Prompt</div>
            <div class="app-subtitle">{APP_TITLE}</div>
        </div>
        """, unsafe_allow_html=True)

        col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
        with col_l2:
            st.error("❌ Incorrect Password. Please try again.")
            st.text_input(
                "Access Password",
                type="password",
                on_change=password_entered,
                key="password_input",
                placeholder="Enter password..."
            )
        return False
    else:
        return True


if not check_password():
    st.stop()

# ----------------------------------------------------
# MAIN DASHBOARD APPLICATION
# ----------------------------------------------------

col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown(f"""
    <div class="app-header" style="margin-bottom: 15px;">
        <div class="app-title">⚡ {APP_TITLE}</div>
        <div class="app-subtitle">{APP_SUBTITLE}</div>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    st.write("")
    st.write("")
    if st.button("🔒 Lock Dashboard", use_container_width=True):
        st.session_state["password_correct"] = False
        st.rerun()

if "selected_location" not in st.session_state:
    st.session_state["selected_location"] = get_all_locations()[0]

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🧬 Chip Config & Capacity Schedule",
    "⚡ 5-Year Power Strategy",
    "🗺️ Top 50 TS Locations Map",
    "📊 Financials & TCO",
    "🧮 Token Demand & Optimization",
    "📄 Executive Export"
])

with tab1:
    target_mw, capacity_schedule_mw, pue, chip_mix = render_tab_chip_config()

with tab3:
    selected_loc = render_tab_map_view()
    st.session_state["selected_location"] = selected_loc

active_loc = st.session_state["selected_location"]

if isinstance(capacity_schedule_mw, (list, tuple)) and len(capacity_schedule_mw) > 0:
    inc_mw_per_year = capacity_schedule_mw[0]
else:
    inc_mw_per_year = int(capacity_schedule_mw)
    capacity_schedule_mw = [inc_mw_per_year * (y + 1) for y in range(5)]

with tab2:
    df_power_plan, total_power_capex = render_tab_power_plan(
        selected_location=active_loc,
        target_mw=target_mw,
        inc_mw_per_year=inc_mw_per_year,
        pue=pue
    )

with tab4:
    fin_results = render_tab_financials(
        target_mw=target_mw,
        inc_mw_per_year=inc_mw_per_year,
        chip_mix=chip_mix,
        df_power_plan=df_power_plan,
        total_power_capex=total_power_capex
    )

with tab5:
    render_tab_token_economics(
        chip_mix=chip_mix,
        capacity_schedule_mw=capacity_schedule_mw,
        selected_location=active_loc,
        total_5year_tco_usd=fin_results["total_5yr_tco"]
    )

with tab6:
    render_tab_export(
        selected_location=active_loc,
        target_mw=target_mw,
        fin_results=fin_results,
        df_power_plan=df_power_plan
    )
