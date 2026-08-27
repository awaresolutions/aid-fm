"""
Tab 1: Chip Selector & Capacity Configuration Component.
Supports custom 5-year phased MW buildout schedule, phased token demand, and chip allocation.
Enhanced contrast light theme edition.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.chip_specs import CHIP_DATABASE, get_chip_names

def render_tab_chip_config():
    st.markdown("### 🧬 AI Accelerator Chip Selector & Phased Capacity Builder")
    st.write("Configure silicon architecture mix, custom 5-year phased power capacity buildout, and annual token demand schedules.")

    col1, col2 = st.columns([1.1, 1], gap="large")

    with col1:
        st.subheader("1. 5-Year Phased Power Capacity Schedule (MW)")
        st.caption("Specify MW capacity brought online in 50 MW building block increments for each year.")

        col_y1, col_y2, col_y3, col_y4, col_y5 = st.columns(5)
        with col_y1:
            mw_y1 = st.number_input("Year 1 MW", min_value=50, max_value=1000, value=50, step=50)
        with col_y2:
            mw_y2 = st.number_input("Year 2 MW", min_value=50, max_value=1000, value=100, step=50)
        with col_y3:
            mw_y3 = st.number_input("Year 3 MW", min_value=50, max_value=1000, value=150, step=50)
        with col_y4:
            mw_y4 = st.number_input("Year 4 MW", min_value=50, max_value=1000, value=200, step=50)
        with col_y5:
            mw_y5 = st.number_input("Year 5 MW", min_value=50, max_value=1000, value=250, step=50)

        capacity_schedule_mw = [mw_y1, mw_y2, mw_y3, mw_y4, mw_y5]
        target_mw = max(capacity_schedule_mw)
        num_50mw_blocks = target_mw // 50

        st.info(f"🧱 Peak Capacity: **{target_mw} MW** (**{num_50mw_blocks} Modular 50 MW Blocks**)")

        pue = st.number_input(
            "Power Usage Effectiveness (PUE)",
            min_value=1.05,
            max_value=1.60,
            value=1.15,
            step=0.01,
            help="Direct-to-Chip liquid cooling typically achieves 1.12 - 1.18 PUE."
        )

    with col2:
        st.subheader("2. Accelerator Chip Architecture Mix (%)")
        chip_names = get_chip_names()

        chip_mix = {}
        default_weights = {
            "NVIDIA GB300 NVL72 (Blackwell Ultra)": 60,
            "NVIDIA Vera Rubin NVL72": 40,
            "NVIDIA B200 NVL72 (Blackwell)": 0,
            "NVIDIA H200 / H100 SXM5": 0,
            "AMD Instinct MI350X": 0
        }

        total_pct = 0
        for chip in chip_names:
            val = st.slider(
                f"{chip} (%)",
                min_value=0,
                max_value=100,
                value=default_weights.get(chip, 0),
                step=5,
                key=f"mix_{chip}"
            )
            chip_mix[chip] = val / 100.0
            total_pct += val

        if total_pct != 100:
            st.warning(f"⚠️ Total chip mix percentages sum to **{total_pct}%**. Please adjust sliders so they sum to 100%.")
        else:
            st.success("✅ Chip mix allocation equals 100%.")

    st.markdown("---")
    st.subheader("🔍 Selected Silicon Hardware Specifications")

    # Display cards for selected chips
    cols = st.columns(len([c for c, w in chip_mix.items() if w > 0]))
    idx = 0
    for chip_name, weight in chip_mix.items():
        if weight > 0:
            spec = CHIP_DATABASE[chip_name]
            with cols[idx]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title" style="color:#1e3a8a;">{chip_name} ({int(weight*100)}% Mix)</div>
                    <div style="font-size: 0.9rem; color: #475569; margin-bottom: 8px; font-weight:600;">{spec['architecture']}</div>
                    <div style="font-size: 1.2rem; font-weight: 800; color: #1d4ed8;">⚡ {spec['tdp_kw_per_rack']} kW / Rack</div>
                    <div style="font-size: 0.88rem; color: #0f172a; margin-top: 10px; line-height: 1.6;">
                        • <b>FP4 Compute:</b> {spec['fp4_tflops_per_chip']/1000:.1f} PFLOPS/chip<br>
                        • <b>Token Output:</b> {spec['tokens_per_sec_per_rack']:,} tok/s/rack<br>
                        • <b>Rack Cost:</b> ${spec['rack_unit_cost_usd']:,}<br>
                        • <b>Cooling:</b> {spec['cooling_type']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                idx += 1

    return target_mw, capacity_schedule_mw, pue, chip_mix
