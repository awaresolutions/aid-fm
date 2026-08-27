"""
Tab 4: 5-Year Financial Cost, TCO & Cash Flow Analytics.
Renders Capex/Opex stack charts, cash flow tables, NPV, and GPU cost metrics.
Enhanced contrast edition.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from engines.financial_engine import calculate_5year_financial_model

def render_tab_financials(target_mw, inc_mw_per_year, chip_mix, df_power_plan, total_power_capex):
    st.markdown("### 📊 5-Year Financial Cost, TCO & Cash Flow Engine")
    st.write("Comprehensive 5-year capital expenditure (Capex), operating expenses (Opex), Total Cost of Ownership (TCO), and NPV model.")

    col_inp1, col_inp2, col_inp3 = st.columns(3)
    with col_inp1:
        datacenter_cost_per_mw = st.number_input(
            "Facility Build Cost ($ / MW)",
            min_value=5_000_000,
            max_value=15_000_000,
            value=8_500_000,
            step=500_000,
            format="%d",
            help="Includes core & shell building, liquid cooling manifolds, heat rejection, and internal power distribution."
        )
    with col_inp2:
        discount_rate = st.slider(
            "Discount Rate (%)",
            min_value=4.0,
            max_value=15.0,
            value=8.0,
            step=0.5
        ) / 100.0
    with col_inp3:
        inflation_rate = st.slider(
            "Annual Inflation Rate (%)",
            min_value=1.0,
            max_value=8.0,
            value=3.5,
            step=0.5
        ) / 100.0

    # Run Master Financial Model
    fin_results = calculate_5year_financial_model(
        target_mw=target_mw,
        inc_mw_per_year=inc_mw_per_year,
        chip_selection_dict=chip_mix,
        df_power_plan=df_power_plan,
        total_power_capex=total_power_capex,
        datacenter_cost_per_mw=datacenter_cost_per_mw,
        discount_rate=discount_rate,
        inflation_rate=inflation_rate
    )

    df_fin = fin_results["df_financials"]

    # Top KPI Metrics Cards
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-title">5-Yr Total Capex</div>
            <div class="metric-value">${fin_results['total_5yr_capex']/1e6:,.1f}M</div>
            <div class="metric-subtext">Hardware + Facility + Power</div>
        </div>""", unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-title">5-Yr Total Opex</div>
            <div class="metric-value">${fin_results['total_5yr_opex']/1e6:,.1f}M</div>
            <div class="metric-subtext">Power + O&M + Security</div>
        </div>""", unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-title">5-Yr Total TCO</div>
            <div class="metric-value">${fin_results['total_5yr_tco']/1e6:,.1f}M</div>
            <div class="metric-subtext">Combined Capex + Opex</div>
        </div>""", unsafe_allow_html=True)

    with kpi4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-title">Total Deployed Racks</div>
            <div class="metric-value">{fin_results['total_it_racks']:,.0f}</div>
            <div class="metric-subtext">{fin_results['total_gpus']:,.0f} total GPUs</div>
        </div>""", unsafe_allow_html=True)

    with kpi5:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-title">Cost / GPU Hour</div>
            <div class="metric-value">${fin_results['cost_per_gpu_hour']:.2f}</div>
            <div class="metric-subtext">Fully Burdened TCO</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        # Stacked Capex Chart
        fig_capex = go.Figure()
        fig_capex.add_trace(go.Bar(name='IT Hardware Capex ($)', x=df_fin['Year'], y=df_fin['IT_Hardware_Capex'], marker_color='#2563eb'))
        fig_capex.add_trace(go.Bar(name='Facility Shell & Cooling ($)', x=df_fin['Year'], y=df_fin['Facility_Capex'], marker_color='#7c3aed'))
        fig_capex.add_trace(go.Bar(name='Power Generation Capex ($)', x=df_fin['Year'], y=df_fin['Power_Infra_Capex'], marker_color='#059669'))

        fig_capex.update_layout(
            title=dict(text="Capital Expenditure (Capex) Breakdown by Year ($)", font=dict(color='#0f172a', size=16, family='Inter')),
            barmode='stack',
            paper_bgcolor='#ffffff',
            plot_bgcolor='#f8fafc',
            font=dict(color='#0f172a'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#0f172a')),
            xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#0f172a')),
            yaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#0f172a'))
        )
        st.plotly_chart(fig_capex, use_container_width=True)

    with col_g2:
        # Stacked Opex Chart
        fig_opex = go.Figure()
        fig_opex.add_trace(go.Bar(name='Power & Electricity ($)', x=df_fin['Year'], y=df_fin['Power_Opex'], marker_color='#3b82f6'))
        fig_opex.add_trace(go.Bar(name='IT Maintenance ($)', x=df_fin['Year'], y=df_fin['Hardware_Maintenance_Opex'], marker_color='#9333ea'))
        fig_opex.add_trace(go.Bar(name='Facility O&M ($)', x=df_fin['Year'], y=df_fin['Facility_O&M_Opex'], marker_color='#d97706'))
        fig_opex.add_trace(go.Bar(name='TS/SCI Security & Staff ($)', x=df_fin['Year'], y=df_fin['Security_Staffing_Opex'], marker_color='#dc2626'))
        fig_opex.add_trace(go.Bar(name='Secure Fiber Network ($)', x=df_fin['Year'], y=df_fin['Fiber_Network_Opex'], marker_color='#16a34a'))

        fig_opex.update_layout(
            title=dict(text="Operating Expenses (Opex) Breakdown by Year ($)", font=dict(color='#0f172a', size=16, family='Inter')),
            barmode='stack',
            paper_bgcolor='#ffffff',
            plot_bgcolor='#f8fafc',
            font=dict(color='#0f172a'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#0f172a')),
            xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#0f172a')),
            yaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#0f172a'))
        )
        st.plotly_chart(fig_opex, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 5-Year Cash Flow Statement ($)")

    # Formatted Financial Table
    st.dataframe(
        df_fin[[
            "Year", "Active_MW", "Total_Capex", "Total_Opex", "Total_Cash_Outflow"
        ]].style.format({
            "Active_MW": "{:.0f} MW",
            "Total_Capex": "${:,.0f}",
            "Total_Opex": "${:,.0f}",
            "Total_Cash_Outflow": "${:,.0f}"
        }),
        use_container_width=True
    )

    return fin_results
