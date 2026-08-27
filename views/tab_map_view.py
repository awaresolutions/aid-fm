"""
Tab 3: Interactive US Map of Top 50 Top Secret (TS/SCI) Compliant Data Center Sites.
Renders geospatial plot, site filtering, utility rates, and site selection.
Compatible with Plotly 5.x and Plotly 6.x (scatter_mapbox / scatter_map).
Enhanced contrast edition.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from data.ts_locations import get_all_locations, get_location_by_id

def render_tab_map_view():
    st.markdown("### 🗺️ Top 50 TS/SCI Compliant US Data Center Locations")
    st.write("Explore intelligence-ready defense locations featuring dark fiber corridors, TEMPEST/SCIF readiness, and high-voltage grid ties.")

    locations = get_all_locations()
    df_locs = pd.DataFrame(locations)

    # Sidebar / Filter Controls
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        selected_state = st.multiselect(
            "Filter by State",
            options=sorted(df_locs["state"].unique()),
            default=[]
        )
    with col_f2:
        max_rate = st.slider(
            "Max Electricity Rate ($/kWh)",
            min_value=0.04,
            max_value=0.20,
            value=0.12,
            step=0.01
        )
    with col_f3:
        min_grid = st.slider(
            "Min Grid Capacity (MW)",
            min_value=300,
            max_value=1500,
            value=400,
            step=50
        )

    # Filter dataframe
    filtered_df = df_locs.copy()
    if selected_state:
        filtered_df = filtered_df[filtered_df["state"].isin(selected_state)]
    filtered_df = filtered_df[
        (filtered_df["median_rate_kwh"] <= max_rate) &
        (filtered_df["grid_capacity_mw"] >= min_grid)
    ]

    st.markdown(f"**Found {len(filtered_df)} Locations** matching search criteria.")

    hover_dict = {
        "city": True,
        "state": True,
        "utility": True,
        "rate_code": True,
        "median_rate_kwh": ":$.3f",
        "scif_rating": True,
        "grid_capacity_mw": ":,d MW",
        "lat": False,
        "lon": False
    }

    # Plotly 5.x vs 6.x map compatibility check
    if hasattr(px, "scatter_mapbox"):
        fig_map = px.scatter_mapbox(
            filtered_df,
            lat="lat",
            lon="lon",
            hover_name="name",
            hover_data=hover_dict,
            color="median_rate_kwh",
            size="grid_capacity_mw",
            color_continuous_scale="Viridis_r",
            size_max=22,
            zoom=3.5,
            center={"lat": 38.5, "lon": -96.0},
            mapbox_style="carto-positron",
            title="Top Secret AI Data Center Candidate Sites (Color = Rate $/kWh, Size = Grid MW)"
        )
    elif hasattr(px, "scatter_map"):
        fig_map = px.scatter_map(
            filtered_df,
            lat="lat",
            lon="lon",
            hover_name="name",
            hover_data=hover_dict,
            color="median_rate_kwh",
            size="grid_capacity_mw",
            color_continuous_scale="Viridis_r",
            size_max=22,
            zoom=3.5,
            center={"lat": 38.5, "lon": -96.0},
            map_style="carto-positron",
            title="Top Secret AI Data Center Candidate Sites (Color = Rate $/kWh, Size = Grid MW)"
        )
    else:
        fig_map = px.scatter_geo(
            filtered_df,
            lat="lat",
            lon="lon",
            hover_name="name",
            hover_data=hover_dict,
            color="median_rate_kwh",
            size="grid_capacity_mw",
            color_continuous_scale="Viridis_r",
            size_max=22,
            scope="usa",
            title="Top Secret AI Data Center Candidate Sites (Color = Rate $/kWh, Size = Grid MW)"
        )

    fig_map.update_layout(
        height=550,
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor='#ffffff',
        font=dict(color='#0f172a')
    )

    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")
    st.subheader("🎯 Active Location Selection")

    selected_name = st.selectbox(
        "Select Active Data Center Location for Financial Model:",
        options=filtered_df["name"].tolist() if len(filtered_df) > 0 else df_locs["name"].tolist(),
        index=0
    )

    selected_loc = filtered_df[filtered_df["name"] == selected_name].iloc[0].to_dict() if len(filtered_df) > 0 else df_locs.iloc[0].to_dict()

    col_d1, col_d2 = st.columns([1, 1])

    with col_d1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.3rem; font-weight:800; color:#1e3a8a; margin-bottom:10px;">{selected_loc['name']}</div>
            <div style="font-size:0.95rem; color:#0f172a; line-height: 1.7;">
                <b>City & State:</b> {selected_loc['city']}, {selected_loc['state']}<br>
                <b>Host Command / Complex:</b> {selected_loc['host_facility']}<br>
                <b>SCIF / TEMPEST Compliance Rating:</b> <span class="badge-ts">{selected_loc['scif_rating']} / 100</span><br>
                <b>Available Grid Interconnect Capacity:</b> {selected_loc['grid_capacity_mw']} MW<br>
                <b>Defense Fiber Corridor Score:</b> {selected_loc['fiber_score']} / 100
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_d2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.1rem; font-weight:800; color:#0f172a; margin-bottom:10px;">⚡ Electric Utility Details</div>
            <div style="font-size:0.95rem; color:#0f172a; line-height: 1.7;">
                <b>Utility Company:</b> {selected_loc['utility']}<br>
                <b>Rate Code / Tariff:</b> {selected_loc['rate_code']}<br>
                <b>Median Energy Rate:</b> <span style="color:#047857; font-weight:800; font-size:1.05rem;">${selected_loc['median_rate_kwh']:.3f} / kWh</span><br>
                <b>Peak Demand Charge:</b> ${selected_loc['demand_charge_kw']:.2f} / kW / month
            </div>
        </div>
        """, unsafe_allow_html=True)

    return selected_loc
