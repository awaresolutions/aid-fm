"""
Optimization & Sensitivity Engine for AI Data Center Modeling.
1. Finds cost-optimal phased capacity schedule & chip mix to fulfill 5-year token demand schedule.
2. Performs sensitivity analysis comparing 5-Year TCO across Top 5 Most Expensive vs Top 5 Least Expensive locations.
"""

import pandas as pd
import numpy as np
from data.chip_specs import CHIP_DATABASE
from data.ts_locations import get_all_locations
from engines.power_engine import calculate_5year_power_plan
from engines.financial_engine import calculate_5year_financial_model
from engines.token_engine import calculate_token_economics

def optimize_capacity_and_chip_mix(
    token_demand_by_year_bday: list,  # List of 5 daily token targets (Billions/day)
    selected_location: dict,
    datacenter_cost_per_mw: float = 8_500_000,
    pue: float = 1.15
):
    """
    Evaluates configurations across chip families to find the cost-optimal phased capacity and chip allocation.
    """
    best_option = None
    min_tco = float('inf')
    
    # 5-Year total tokens requested
    total_5yr_tokens = sum([td * 1e9 * 365.25 for td in token_demand_by_year_bday])
    max_daily_demand = max(token_demand_by_year_bday) * 1e9
    
    scenarios = []

    for chip_name, spec in CHIP_DATABASE.items():
        # Calculate MW needed for peak demand using this chip family
        tok_sec_needed = max_daily_demand / 86400.0
        racks_needed = tok_sec_needed / spec["tokens_per_sec_per_rack"]
        it_mw_needed = (racks_needed * spec["tdp_kw_per_rack"]) / 1000.0
        
        # Step in 50 MW building blocks per year
        capacity_schedule_mw = []
        for yr_idx in range(5):
            yr_demand = token_demand_by_year_bday[yr_idx] * 1e9
            yr_tok_sec = yr_demand / 86400.0
            yr_racks = yr_tok_sec / spec["tokens_per_sec_per_rack"]
            yr_mw = (yr_racks * spec["tdp_kw_per_rack"]) / 1000.0
            # Sized in 50 MW increments
            blocks = max(1, int(np.ceil(yr_mw / 50.0)))
            capacity_schedule_mw.append(blocks * 50.0)

        chip_mix = {chip_name: 1.0}
        
        # Evaluate power & financial plan
        df_power, total_pwr_capex = calculate_5year_power_plan(
            target_mw=capacity_schedule_mw[-1],
            inc_mw_per_year=capacity_schedule_mw[0],
            location_rate_kwh=selected_location["median_rate_kwh"],
            location_demand_charge_kw=selected_location["demand_charge_kw"],
            grid_pct_by_year=[1.0]*5,
            smr_mw_by_year=[0]*5,
            diesel_mw_by_year=[0]*5,
            gas_mw_by_year=[0]*5,
            pue=pue
        )

        fin_res = calculate_5year_financial_model(
            target_mw=capacity_schedule_mw[-1],
            inc_mw_per_year=capacity_schedule_mw[0],
            chip_selection_dict=chip_mix,
            df_power_plan=df_power,
            total_power_capex=total_pwr_capex,
            datacenter_cost_per_mw=datacenter_cost_per_mw
        )

        tco = fin_res["total_5yr_tco"]
        cost_per_1m = (tco / total_5yr_tokens) * 1_000_000 if total_5yr_tokens > 0 else 0.0

        scenario_res = {
            "chip_name": chip_name,
            "peak_mw": capacity_schedule_mw[-1],
            "capacity_schedule_mw": capacity_schedule_mw,
            "total_tco": tco,
            "total_capex": fin_res["total_5yr_capex"],
            "total_opex": fin_res["total_5yr_opex"],
            "cost_per_1m_tokens": cost_per_1m,
            "cost_per_gpu_hour": fin_res["cost_per_gpu_hour"]
        }
        scenarios.append(scenario_res)

        if tco < min_tco:
            min_tco = tco
            best_option = scenario_res

    df_scenarios = pd.DataFrame(scenarios)
    return best_option, df_scenarios


def calculate_top5_location_sensitivity(
    target_mw: float,
    inc_mw_per_year: float,
    chip_mix: dict,
    datacenter_cost_per_mw: float = 8_500_000,
    pue: float = 1.15
):
    """
    Computes 5-Year TCO sensitivity for Top 5 Most Expensive vs Top 5 Least Expensive electricity locations.
    """
    all_locs = get_all_locations()
    df_locs = pd.DataFrame(all_locs)
    
    # Sort by median rate
    df_sorted = df_locs.sort_values(by="median_rate_kwh", ascending=False)
    
    top5_expensive = df_sorted.head(5).to_dict(orient="records")
    top5_cheapest = df_sorted.tail(5).sort_values(by="median_rate_kwh", ascending=True).to_dict(orient="records")

    results = []

    for group_label, loc_list in [("Top 5 Most Expensive", top5_expensive), ("Top 5 Least Expensive", top5_cheapest)]:
        for loc in loc_list:
            df_pwr, pwr_capex = calculate_5year_power_plan(
                target_mw=target_mw,
                inc_mw_per_year=inc_mw_per_year,
                location_rate_kwh=loc["median_rate_kwh"],
                location_demand_charge_kw=loc["demand_charge_kw"],
                grid_pct_by_year=[1.0]*5,
                smr_mw_by_year=[0]*5,
                diesel_mw_by_year=[0]*5,
                gas_mw_by_year=[0]*5,
                pue=pue
            )

            fin_res = calculate_5year_financial_model(
                target_mw=target_mw,
                inc_mw_per_year=inc_mw_per_year,
                chip_selection_dict=chip_mix,
                df_power_plan=df_pwr,
                total_power_capex=pwr_capex,
                datacenter_cost_per_mw=datacenter_cost_per_mw
            )

            results.append({
                "Group": group_label,
                "Location": loc["name"],
                "City State": f"{loc['city']}, {loc['state']}",
                "Utility": loc["utility"],
                "Median Rate ($/kWh)": loc["median_rate_kwh"],
                "Demand Charge ($/kW/mo)": loc["demand_charge_kw"],
                "5-Yr Total Capex ($)": fin_res["total_5yr_capex"],
                "5-Yr Total Opex ($)": fin_res["total_5yr_opex"],
                "5-Yr Total TCO ($)": fin_res["total_5yr_tco"],
                "Cost / GPU Hour ($)": fin_res["cost_per_gpu_hour"]
            })

    return pd.DataFrame(results)
