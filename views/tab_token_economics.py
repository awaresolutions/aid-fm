"""
Tab 5: Token Usage Demand, Hardware Matching, Optimization & Location Sensitivity.
Includes phased annual token demand, capacity vs demand relationship for each chip type, optimal capacity mix summary, and location sensitivity analysis.
Enhanced light theme contrast edition.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.chip_specs import CHIP_DATABASE
from engines.token_engine import calculate_token_economics
from engines.optimization_engine import optimize_capacity_and_chip_mix, calculate_top5_location_sensitivity

def render_tab_token_economics(chip_mix, capacity_schedule_mw, selected_location, total_5year_tco_usd):
    st.markdown("### 🧮 5-Year Token Demand, Hardware Capacity & Optimization Model")
    st.write("Model 5-year token demand schedules, compare capacity fulfillment per chip architecture, discover the cost-minimizing optimal mix, and analyze location cost sensitivities.")

    # 1. 5-Year Phased Token Demand Input
    st.subheader("1. 5-Year Phased Token Demand Schedule (Billion Tokens / Day)")
    st.caption("Set the daily token demand target expected in each of the 5 years.")

    col_td1, col_td2, col_td3, col_td4, col_td5 = st.columns(5)
    with col_td1:
        td_y1 = st.number_input("Year 1 Demand (B/day)", min_value=1.0, max_value=2000.0, value=10.0, step=5.0)
    with col_td2:
        td_y2 = st.number_input("Year 2 Demand (B/day)", min_value=1.0, max_value=2000.0, value=25.0, step=5.0)
    with col_td3:
        td_y3 = st.number_input("Year 3 Demand (B/day)", min_value=1.0, max_value=2000.0, value=50.0, step=5.0)
    with col_td4:
        td_y4 = st.number_input("Year 4 Demand (B/day)", min_value=1.0, max_value=2000.0, value=75.0, step=5.0)
    with col_td5:
        td_y5 = st.number_input("Year 5 Demand (B/day)", min_value=1.0, max_value=2000.0, value=100.0, step=5.0)

    token_demand_by_year_bday = [td_y1, td_y2, td_y3, td_y4, td_y5]

    st.markdown("---")

    # 2. Relationship between MW Capacity Brought Online & Token Demand per Chip Type
    st.subheader("2. Capacity vs Token Demand Relationship per Chip Architecture")
    st.write("Compares how much token throughput each chip family generates from your configured 5-year MW capacity schedule vs target token demand.")

    years = [f"Year {y}" for y in range(1, 6)]

    # Calculate token supply capacity for each chip type based on capacity_schedule_mw
    relationship_data = []
    for i in range(5):
        yr = years[i]
        mw = capacity_schedule_mw[i]
        demand_bday = token_demand_by_year_bday[i]

        row = {
            "Year": yr,
            "Built MW": mw,
            "Target Demand (B/day)": demand_bday
        }

        for c_name, c_spec in CHIP_DATABASE.items():
            racks = (mw * 1000.0) / c_spec["tdp_kw_per_rack"]
            tok_sec = racks * c_spec["tokens_per_sec_per_rack"]
            tok_bday = (tok_sec * 86400.0) / 1e9
            utilization_pct = (demand_bday / tok_bday) * 100.0 if tok_bday > 0 else 0.0

            row[f"{c_name} Supply (B/day)"] = round(tok_bday, 1)
            row[f"{c_name} Utilization %"] = round(utilization_pct, 1)

        relationship_data.append(row)

    df_rel = pd.DataFrame(relationship_data)

    # Plot Capacity Supply vs Demand line chart
    fig_rel = go.Figure()
    fig_rel.add_trace(go.Scatter(x=df_rel["Year"], y=df_rel["Target Demand (B/day)"], name="Target Demand (B/day)", line=dict(color="#0f172a", width=4, dash="dash")))

    colors = ["#2563eb", "#059669", "#7c3aed", "#d97706", "#dc2626"]
    c_idx = 0
    for c_name in CHIP_DATABASE.keys():
        fig_rel.add_trace(go.Scatter(x=df_rel["Year"], y=df_rel[f"{c_name} Supply (B/day)"], name=f"{c_name}", line=dict(color=colors[c_idx % len(colors)], width=3)))
        c_idx += 1

    fig_rel.update_layout(
        title=dict(text="5-Year Token Supply Capacity vs Demand (Billion Tokens / Day)", font=dict(color='#0f172a', size=16)),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8fafc",
        font=dict(color="#0f172a"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(gridcolor='#e2e8f0'),
        yaxis=dict(gridcolor='#e2e8f0')
    )
    st.plotly_chart(fig_rel, use_container_width=True)

    st.dataframe(
        df_rel[[
            "Year", "Built MW", "Target Demand (B/day)",
            "NVIDIA GB300 NVL72 (Blackwell Ultra) Supply (B/day)",
            "NVIDIA Vera Rubin NVL72 Supply (B/day)",
            "NVIDIA B200 NVL72 (Blackwell) Supply (B/day)",
            "NVIDIA H200 / H100 SXM5 Supply (B/day)"
        ]].style.format({
            "Built MW": "{:.0f} MW",
            "Target Demand (B/day)": "{:.1f} B/day",
            "NVIDIA GB300 NVL72 (Blackwell Ultra) Supply (B/day)": "{:.1f} B/day",
            "NVIDIA Vera Rubin NVL72 Supply (B/day)": "{:.1f} B/day",
            "NVIDIA B200 NVL72 (Blackwell) Supply (B/day)": "{:.1f} B/day",
            "NVIDIA H200 / H100 SXM5 Supply (B/day)": "{:.1f} B/day"
        }),
        use_container_width=True
    )

    st.markdown("---")

    # 3. Optimal Mix Summary to Minimize Costs
    st.subheader("🎯 Cost-Minimizing Optimal Capacity & Chip Architecture Mix")
    
    optimal_res, df_scenarios = optimize_capacity_and_chip_mix(
        token_demand_by_year_bday=token_demand_by_year_bday,
        selected_location=selected_location
    )

    col_opt1, col_opt2 = st.columns([1.2, 1])

    with col_opt1:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #059669;">
            <div class="metric-title" style="color:#059669;">💡 Cost-Minimizing Recommended Architecture</div>
            <div style="font-size:1.4rem; font-weight:800; color:#0f172a; margin-bottom:6px;">{optimal_res['chip_name']}</div>
            <div style="font-size:0.95rem; color:#1e293b; line-height:1.7;">
                • <b>5-Year Total Cost of Ownership (TCO):</b> <span style="color:#059669; font-weight:800;">${optimal_res['total_tco']/1e6:,.1f} Million</span><br>
                • <b>Burdened Unit Cost per 1M Tokens:</b> <span style="color:#059669; font-weight:800;">${optimal_res['cost_per_1m_tokens']:.4f}</span><br>
                • <b>Fully Burdened GPU Hour Cost:</b> ${optimal_res['cost_per_gpu_hour']:.2f} / GPU-hr<br>
                • <b>Optimal 5-Year MW Phasing:</b> {optimal_res['capacity_schedule_mw'][0]:.0f} MW → {optimal_res['capacity_schedule_mw'][1]:.0f} MW → {optimal_res['capacity_schedule_mw'][2]:.0f} MW → {optimal_res['capacity_schedule_mw'][3]:.0f} MW → {optimal_res['capacity_schedule_mw'][4]:.0f} MW
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_opt2:
        # Bar Chart comparing TCO across single-architecture scenarios
        fig_opt = px.bar(
            df_scenarios,
            x="chip_name",
            y="cost_per_1m_tokens",
            color="cost_per_1m_tokens",
            color_continuous_scale="Viridis_r",
            text_auto=".4f",
            title="5-Year Unit Cost per 1M Tokens by Architecture ($)"
        )
        fig_opt.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#f8fafc",
            font=dict(color="#0f172a"),
            xaxis=dict(tickangle=-15, tickfont=dict(color='#0f172a')),
            yaxis=dict(tickfont=dict(color='#0f172a'))
        )
        st.plotly_chart(fig_opt, use_container_width=True)

    st.markdown("---")

    # 4. Sensitivity Analysis: Top 5 Most Expensive vs Top 5 Least Expensive Locations
    st.subheader("📈 Location Cost Sensitivity: Top 5 Most Expensive vs Top 5 Least Expensive Sites")
    st.write("Models the 5-Year Total Cost of Ownership (TCO) impact of utility electricity rates across extreme US location bounds.")

    df_sens = calculate_top5_location_sensitivity(
        target_mw=max(capacity_schedule_mw),
        inc_mw_per_year=capacity_schedule_mw[0],
        chip_mix=chip_mix
    )

    # Plot horizontal bar chart comparing TCO across Top 5 Expensive vs Top 5 Cheapest
    fig_sens = px.bar(
        df_sens,
        y="Location",
        x="5-Yr Total TCO ($)",
        color="Group",
        color_discrete_map={"Top 5 Most Expensive": "#dc2626", "Top 5 Least Expensive": "#059669"},
        orientation="h",
        hover_data=["Utility", "Median Rate ($/kWh)", "5-Yr Total Opex ($)"],
        title=f"5-Year TCO Comparison across Utility Rate Extremes ({max(capacity_schedule_mw):.0f} MW Peak)"
    )

    fig_sens.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8fafc",
        font=dict(color="#0f172a"),
        xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#0f172a')),
        yaxis=dict(tickfont=dict(color='#0f172a'))
    )
    st.plotly_chart(fig_sens, use_container_width=True)

    st.dataframe(
        df_sens[[
            "Group", "Location", "City State", "Utility", "Median Rate ($/kWh)", "5-Yr Total Capex ($)", "5-Yr Total Opex ($)", "5-Yr Total TCO ($)", "Cost / GPU Hour ($)"
        ]].style.format({
            "Median Rate ($/kWh)": "${:.3f}",
            "5-Yr Total Capex ($)": "${:,.0f}",
            "5-Yr Total Opex ($)": "${:,.0f}",
            "5-Yr Total TCO ($)": "${:,.0f}",
            "Cost / GPU Hour ($)": "${:.2f}"
        }),
        use_container_width=True
    )
