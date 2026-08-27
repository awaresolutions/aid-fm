"""
Master Financial Modeling Engine.
Computes 5-year Capex, Opex, TCO, Cash Flows, NPV, LCOE, and financial KPIs.
"""

import pandas as pd
import numpy as np
from data.chip_specs import CHIP_DATABASE
from config import DEFAULT_DC_BUILD_COST_PER_MW, DEFAULT_DISCOUNT_RATE, DEFAULT_INFLATION_RATE

def calculate_5year_financial_model(
    target_mw: float,
    inc_mw_per_year: float,
    chip_selection_dict: dict,    # {"chip_name": percentage}
    df_power_plan: pd.DataFrame,
    total_power_capex: float,
    datacenter_cost_per_mw: float = DEFAULT_DC_BUILD_COST_PER_MW,
    discount_rate: float = DEFAULT_DISCOUNT_RATE,
    inflation_rate: float = DEFAULT_INFLATION_RATE,
    token_api_price_per_1m: float = 0.50  # Revenue assumption for financial cash flow ($0.50 / 1M tokens)
):
    """
    Generates full 5-year financial cash flow, Capex/Opex breakdown, and TCO model.
    """
    # 1. Compute Hardware Sizing and Capex
    total_it_racks = 0.0
    total_gpus = 0.0
    total_hardware_capex = 0.0
    weighted_kw_per_rack = 0.0

    for chip_name, weight in chip_selection_dict.items():
        if weight > 0 and chip_name in CHIP_DATABASE:
            spec = CHIP_DATABASE[chip_name]
            weighted_kw_per_rack += weight * spec["tdp_kw_per_rack"]

    if weighted_kw_per_rack <= 0:
        weighted_kw_per_rack = 140.0

    # Number of racks for target_mw
    total_racks = (target_mw * 1000.0) / weighted_kw_per_rack

    for chip_name, weight in chip_selection_dict.items():
        if weight > 0 and chip_name in CHIP_DATABASE:
            spec = CHIP_DATABASE[chip_name]
            chip_racks = total_racks * weight
            chip_gpus = chip_racks * spec["gpus_per_rack"]
            chip_cost = chip_racks * spec["rack_unit_cost_usd"]
            
            total_it_racks += chip_racks
            total_gpus += chip_gpus
            total_hardware_capex += chip_cost

    # Facility Shell & Direct Liquid Cooling Capex
    facility_capex = target_mw * datacenter_cost_per_mw
    total_upfront_capex = total_hardware_capex + facility_capex + total_power_capex

    # 2. Year-by-Year Financial Cash Flows
    cash_flows = []
    
    # Year 0: Initial Capital Expenditure
    cash_flows.append({
        "Year": "Year 0",
        "Year_Index": 0,
        "Active_MW": 0.0,
        "IT_Hardware_Capex": total_hardware_capex * 0.60,  # 60% hardware deployed in Yr 0
        "Facility_Capex": facility_capex * 0.60,
        "Power_Infra_Capex": total_power_capex * 0.60,
        "Total_Capex": (total_hardware_capex + facility_capex + total_power_capex) * 0.60,
        "Power_Opex": 0.0,
        "Hardware_Maintenance_Opex": 0.0,
        "Facility_O&M_Opex": 0.0,
        "Security_Staffing_Opex": 0.0,
        "Fiber_Network_Opex": 0.0,
        "Total_Opex": 0.0,
        "Total_Cash_Outflow": (total_hardware_capex + facility_capex + total_power_capex) * 0.60,
        "Est_Token_Revenue": 0.0,
        "Net_Cash_Flow": -((total_hardware_capex + facility_capex + total_power_capex) * 0.60)
    })

    remaining_capex_frac = 0.40 / 5.0

    for i in range(5):
        yr_name = f"Year {i+1}"
        row_power = df_power_plan.iloc[i]
        cur_mw = row_power["it_capacity_mw"]
        escalation = (1 + inflation_rate) ** i

        # Remaining phased Capex additions
        yr_hw_capex = total_hardware_capex * remaining_capex_frac
        yr_fac_capex = facility_capex * remaining_capex_frac
        yr_pwr_capex = row_power["power_capex_usd"]
        yr_total_capex = yr_hw_capex + yr_fac_capex + yr_pwr_capex

        # Opex Breakdown
        yr_power_opex = row_power["total_power_opex_usd"]
        yr_hw_maint = (total_hardware_capex * 0.08) * escalation * (cur_mw / target_mw)  # 8% hw maintenance
        yr_fac_om = (facility_capex * 0.025) * escalation * (cur_mw / target_mw)          # 2.5% facility O&M
        yr_security = (4_500_000 * (cur_mw / 50.0)) * escalation                         # TS/SCI SCIF cleared team
        yr_fiber = (1_500_000 * (cur_mw / 50.0)) * escalation                            # High speed secure fiber

        yr_total_opex = yr_power_opex + yr_hw_maint + yr_fac_om + yr_security + yr_fiber
        yr_cash_out = yr_total_capex + yr_total_opex

        # Estimated Token Output & Revenue Potential
        # Calculate daily tokens from hardware capacity
        weighted_tokens_sec = 0.0
        for chip_name, weight in chip_selection_dict.items():
            if weight > 0 and chip_name in CHIP_DATABASE:
                spec = CHIP_DATABASE[chip_name]
                weighted_tokens_sec += (total_it_racks * weight * (cur_mw / target_mw)) * spec["tokens_per_sec_per_rack"]

        annual_tokens_yr = weighted_tokens_sec * 86400 * 365.25
        yr_token_revenue = (annual_tokens_yr / 1_000_000) * token_api_price_per_1m

        net_cash = yr_token_revenue - yr_cash_out

        cash_flows.append({
            "Year": yr_name,
            "Year_Index": i + 1,
            "Active_MW": cur_mw,
            "IT_Hardware_Capex": yr_hw_capex,
            "Facility_Capex": yr_fac_capex,
            "Power_Infra_Capex": yr_pwr_capex,
            "Total_Capex": yr_total_capex,
            "Power_Opex": yr_power_opex,
            "Hardware_Maintenance_Opex": yr_hw_maint,
            "Facility_O&M_Opex": yr_fac_om,
            "Security_Staffing_Opex": yr_security,
            "Fiber_Network_Opex": yr_fiber,
            "Total_Opex": yr_total_opex,
            "Total_Cash_Outflow": yr_cash_out,
            "Est_Token_Revenue": yr_token_revenue,
            "Net_Cash_Flow": net_cash
        })

    df_financials = pd.DataFrame(cash_flows)

    # 3. Key Financial Summary Metrics
    total_5yr_capex = df_financials["Total_Capex"].sum()
    total_5yr_opex = df_financials["Total_Opex"].sum()
    total_5yr_tco = total_5yr_capex + total_5yr_opex
    
    # Net Present Value (NPV)
    npv = 0.0
    for idx, row in df_financials.iterrows():
        t = row["Year_Index"]
        npv += row["Net_Cash_Flow"] / ((1 + discount_rate) ** t)

    # Levelized Cost of Compute ($/GPU Hour over 5 Years)
    total_gpu_hours = total_gpus * 8760 * 5.0
    cost_per_gpu_hour = total_5yr_tco / total_gpu_hours if total_gpu_hours > 0 else 0.0

    return {
        "df_financials": df_financials,
        "total_hardware_capex": total_hardware_capex,
        "facility_capex": facility_capex,
        "total_power_capex": total_power_capex,
        "total_5yr_capex": total_5yr_capex,
        "total_5yr_opex": total_5yr_opex,
        "total_5yr_tco": total_5yr_tco,
        "total_gpus": total_gpus,
        "total_it_racks": total_it_racks,
        "npv": npv,
        "cost_per_gpu_hour": cost_per_gpu_hour
    }
