"""
Tab 6: Executive Summary, Scenario Benchmarking & Data Export Component.
Generates executive report summary and CSV downloads.
Enhanced contrast edition.
"""

import streamlit as st
import pandas as pd

def render_tab_export(selected_location, target_mw, fin_results, df_power_plan):
    st.markdown("### 📄 Executive Summary & Data Export")
    st.write("Export detailed 5-year financial statements, power procurement schedules, and executive briefing reports.")

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.2rem; font-weight:800; color:#1e3a8a; margin-bottom:10px;">📋 Executive Modeling Briefing</div>
            <div style="font-size:0.95rem; color:#0f172a; line-height: 1.8;">
                • <b>Primary Location:</b> {selected_location['name']} ({selected_location['utility']})<br>
                • <b>Data Center Capacity:</b> {target_mw} MW ({target_mw//50} x 50 MW Modular Blocks)<br>
                • <b>5-Year Total Capex:</b> ${fin_results['total_5yr_capex']/1e6:,.1f} Million<br>
                • <b>5-Year Total Opex:</b> ${fin_results['total_5yr_opex']/1e6:,.1f} Million<br>
                • <b>5-Year Total TCO:</b> ${fin_results['total_5yr_tco']/1e6:,.1f} Million<br>
                • <b>Fully Burdened Cost / GPU Hour:</b> ${fin_results['cost_per_gpu_hour']:.2f}<br>
                • <b>Net Present Value (NPV @ 8%):</b> ${fin_results['npv']/1e6:,.1f} Million
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_e2:
        st.markdown("#### 📥 Download Raw Financial & Power Datasets")

        # CSV Download Buttons
        df_fin = fin_results["df_financials"]
        csv_fin = df_fin.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Download 5-Year Financial Cash Flow Statement (CSV)",
            data=csv_fin,
            file_name=f"financial_statement_{selected_location['state']}_{target_mw}MW.csv",
            mime="text/csv",
            use_container_width=True
        )

        csv_pwr = df_power_plan.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⚡ Download 5-Year Power Procurement Schedule (CSV)",
            data=csv_pwr,
            file_name=f"power_procurement_schedule_{target_mw}MW.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.info("💡 CSV downloads contain itemized yearly figures for Capex, Opex, LCOE, and power generation dispatch.")
