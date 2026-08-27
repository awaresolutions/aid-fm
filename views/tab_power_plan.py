"""
Tab 2: 5-Year Staged Power Procurement & Hybrid Generation Component.
Models staged power delivery blending utility grid with SMRs and Diesel generators.
Enhanced contrast edition.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.power_types import POWER_SOURCES
from engines.power_engine import calculate_5year_power_plan

def render_tab_power_plan(selected_location, target_mw, inc_mw_per_year, pue):
    st.markdown("### ⚡ 5-Year Staged Power Procurement & On-Site Generation Strategy")
    st.write(f"Configure grid tie-in, Small Modular Reactors (SMRs), and Diesel peaking generators for **{selected_location['name']}**.")

    col_loc1, col_loc2, col_loc3, col_loc4 = st.columns(4)
    with col_loc1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-title">Utility Company</div>
            <div style="font-weight:800; color:#1e3a8a; font-size:1.05rem;">{selected_location['utility']}</div>
        </div>""", unsafe_allow_html=True)
    with col_loc2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-title">Rate Code</div>
            <div style="font-weight:700; color:#0f172a; font-size:0.9rem;">{selected_location['rate_code']}</div>
        </div>""", unsafe_allow_html=True)
    with col_loc3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-title">Median Energy Rate</div>
            <div class="metric-value" style="color:#047857;">${selected_location['median_rate_kwh']:.3f} <span style="font-size:0.9rem; color:#475569;">/ kWh</span></div>
        </div>""", unsafe_allow_html=True)
    with col_loc4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-title">Peak Demand Charge</div>
            <div class="metric-value" style="color:#b45309;">${selected_location['demand_charge_kw']:.2f} <span style="font-size:0.9rem; color:#475569;">/ kW / mo</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🛠️ 5-Year Staged Generation Deployment Schedule (MW)")

    col1, col2, col3 = st.columns(3)

    smr_mw = []
    diesel_mw = []
    gas_mw = []

    with col1:
        st.markdown("#### ⚛️ Small Modular Reactors (SMR)")
        st.caption("77 MW per Module | $6,800/kW Capex | $0.034/kWh Fuel | 3-Year Deployment")
        smr_mw.append(st.number_input("Year 1 SMR (MW)", min_value=0, max_value=target_mw, value=0, step=77, key="smr_y1"))
        smr_mw.append(st.number_input("Year 2 SMR (MW)", min_value=0, max_value=target_mw, value=0, step=77, key="smr_y2"))
        smr_mw.append(st.number_input("Year 3 SMR (MW)", min_value=0, max_value=target_mw, value=77, step=77, key="smr_y3"))
        smr_mw.append(st.number_input("Year 4 SMR (MW)", min_value=0, max_value=target_mw, value=154, step=77, key="smr_y4"))
        smr_mw.append(st.number_input("Year 5 SMR (MW)", min_value=0, max_value=target_mw, value=231, step=77, key="smr_y5"))

    with col2:
        st.markdown("#### 🚜 Diesel Peaking Generators")
        st.caption("2.5 MW Units | $450/kW Capex | $0.220/kWh Fuel | Fast Bridge Power")
        diesel_mw.append(st.number_input("Year 1 Diesel (MW)", min_value=0, max_value=target_mw, value=50, step=25, key="dies_y1"))
        diesel_mw.append(st.number_input("Year 2 Diesel (MW)", min_value=0, max_value=target_mw, value=50, step=25, key="dies_y2"))
        diesel_mw.append(st.number_input("Year 3 Diesel (MW)", min_value=0, max_value=target_mw, value=25, step=25, key="dies_y3"))
        diesel_mw.append(st.number_input("Year 4 Diesel (MW)", min_value=0, max_value=target_mw, value=0, step=25, key="dies_y4"))
        diesel_mw.append(st.number_input("Year 5 Diesel (MW)", min_value=0, max_value=target_mw, value=0, step=25, key="dies_y5"))

    with col3:
        st.markdown("#### 🏭 Natural Gas Turbines")
        st.caption("Combined Cycle | $1,250/kW Capex | $0.065/kWh Fuel | 2-Year Lead Time")
        gas_mw.append(st.number_input("Year 1 Gas (MW)", min_value=0, max_value=target_mw, value=0, step=25, key="gas_y1"))
        gas_mw.append(st.number_input("Year 2 Gas (MW)", min_value=0, max_value=target_mw, value=25, step=25, key="gas_y2"))
        gas_mw.append(st.number_input("Year 3 Gas (MW)", min_value=0, max_value=target_mw, value=25, step=25, key="gas_y3"))
        gas_mw.append(st.number_input("Year 4 Gas (MW)", min_value=0, max_value=target_mw, value=25, step=25, key="gas_y4"))
        gas_mw.append(st.number_input("Year 5 Gas (MW)", min_value=0, max_value=target_mw, value=25, step=25, key="gas_y5"))

    # Compute 5-Year Power Plan
    df_power, total_power_capex = calculate_5year_power_plan(
        target_mw=target_mw,
        inc_mw_per_year=inc_mw_per_year,
        location_rate_kwh=selected_location["median_rate_kwh"],
        location_demand_charge_kw=selected_location["demand_charge_kw"],
        grid_pct_by_year=[1.0]*5,
        smr_mw_by_year=smr_mw,
        diesel_mw_by_year=diesel_mw,
        gas_mw_by_year=gas_mw,
        pue=pue
    )

    st.markdown("---")
    st.subheader("📊 5-Year Power Mix & Cost Analysis")

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        # Stacked Bar Chart of MW Generation by Source
        fig_mw = go.Figure()
        fig_mw.add_trace(go.Bar(name='Utility Grid (MW)', x=df_power['year'], y=df_power['grid_mw'], marker_color='#2563eb'))
        fig_mw.add_trace(go.Bar(name='SMR Nuclear (MW)', x=df_power['year'], y=df_power['smr_mw'], marker_color='#059669'))
        fig_mw.add_trace(go.Bar(name='Gas Turbines (MW)', x=df_power['year'], y=df_power['gas_mw'], marker_color='#d97706'))
        fig_mw.add_trace(go.Bar(name='Diesel Peaking (MW)', x=df_power['year'], y=df_power['diesel_mw'], marker_color='#dc2626'))

        fig_mw.update_layout(
            title=dict(text="Staged Power Capacity Delivery by Source (MW)", font=dict(color='#0f172a', size=16, family='Inter')),
            barmode='stack',
            paper_bgcolor='#ffffff',
            plot_bgcolor='#f8fafc',
            font=dict(color='#0f172a'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#0f172a')),
            xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#0f172a')),
            yaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#0f172a'))
        )
        st.plotly_chart(fig_mw, use_container_width=True)

    with col_c2:
        # Annual Opex Chart
        fig_opex = go.Figure()
        fig_opex.add_trace(go.Bar(name='Grid Power Opex ($)', x=df_power['year'], y=df_power['grid_opex_usd'], marker_color='#3b82f6'))
        fig_opex.add_trace(go.Bar(name='SMR Fuel Opex ($)', x=df_power['year'], y=df_power['smr_opex_usd'], marker_color='#10b981'))
        fig_opex.add_trace(go.Bar(name='Gas Fuel Opex ($)', x=df_power['year'], y=df_power['gas_opex_usd'], marker_color='#f59e0b'))
        fig_opex.add_trace(go.Bar(name='Diesel Fuel Opex ($)', x=df_power['year'], y=df_power['diesel_opex_usd'], marker_color='#ef4444'))

        fig_opex.update_layout(
            title=dict(text="Annual Power Procurement Opex ($)", font=dict(color='#0f172a', size=16, family='Inter')),
            barmode='stack',
            paper_bgcolor='#ffffff',
            plot_bgcolor='#f8fafc',
            font=dict(color='#0f172a'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#0f172a')),
            xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#0f172a')),
            yaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#0f172a'))
        )
        st.plotly_chart(fig_opex, use_container_width=True)

    st.dataframe(
        df_power[[
            "year", "it_capacity_mw", "facility_capacity_mw",
            "grid_mw", "smr_mw", "diesel_mw", "gas_mw",
            "power_capex_usd", "total_power_opex_usd", "blended_lcoe_kwh"
        ]].style.format({
            "it_capacity_mw": "{:.0f} MW",
            "facility_capacity_mw": "{:.1f} MW",
            "grid_mw": "{:.1f} MW",
            "smr_mw": "{:.1f} MW",
            "diesel_mw": "{:.1f} MW",
            "gas_mw": "{:.1f} MW",
            "power_capex_usd": "${:,.0f}",
            "total_power_opex_usd": "${:,.0f}",
            "blended_lcoe_kwh": "${:.4f}"
        }),
        use_container_width=True
    )

    return df_power, total_power_capex
