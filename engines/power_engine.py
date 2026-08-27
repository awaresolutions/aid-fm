"""
Power Procurement & Generation Dispatch Engine.
Models 5-year staged power procurement in 50 MW increments, blending utility grid and on-site generation.
"""

import pandas as pd
import numpy as np
from data.power_types import POWER_SOURCES

def calculate_5year_power_plan(
    target_mw: float,
    inc_mw_per_year: float,
    location_rate_kwh: float,
    location_demand_charge_kw: float,
    grid_pct_by_year: list,        # List of 5 floats (e.g. [1.0, 0.8, 0.5, 0.4, 0.3])
    smr_mw_by_year: list,          # List of 5 floats (MW of SMR deployed)
    diesel_mw_by_year: list,       # List of 5 floats (MW of Diesel deployed)
    gas_mw_by_year: list,          # List of 5 floats (MW of Gas Turbines deployed)
    pue: float = 1.15,
    inflation_rate: float = 0.035
):
    """
    Computes 5-year power capacity, energy consumption (MWh), and power cost breakdown.
    """
    years = [f"Year {y}" for y in range(1, 6)]
    
    records = []
    total_power_capex = 0.0
    
    # Track Capex added in each year
    smr_capex_per_mw = POWER_SOURCES["Small Modular Reactor (SMR)"]["capex_usd_per_mw"]
    diesel_capex_per_mw = POWER_SOURCES["Diesel Peaking / Prime Generators"]["capex_usd_per_mw"]
    gas_capex_per_mw = POWER_SOURCES["Natural Gas Combined Cycle / Turbines"]["capex_usd_per_mw"]
    grid_capex_per_mw = POWER_SOURCES["Utility Grid Supply"]["capex_usd_per_mw"]

    prev_smr = 0
    prev_diesel = 0
    prev_gas = 0
    prev_capacity = 0

    for i in range(5):
        yr_name = years[i]
        # Active capacity for the year (staged buildout up to target_mw)
        current_capacity_mw = min(target_mw, (i + 1) * inc_mw_per_year)
        
        # IT Load vs Total Facility Load (including PUE)
        facility_power_mw = current_capacity_mw * pue
        annual_hours = 8760
        annual_mwh_required = facility_power_mw * annual_hours
        
        # Active generation capacity deployed
        active_smr_mw = min(facility_power_mw, smr_mw_by_year[i])
        active_diesel_mw = min(facility_power_mw - active_smr_mw, diesel_mw_by_year[i])
        active_gas_mw = min(facility_power_mw - active_smr_mw - active_diesel_mw, gas_mw_by_year[i])
        
        # Grid covers remaining MW load
        grid_mw_needed = max(0.0, facility_power_mw - active_smr_mw - active_diesel_mw - active_gas_mw)
        
        # Incremental Capex incurred in this year
        add_smr_mw = max(0.0, smr_mw_by_year[i] - prev_smr)
        add_diesel_mw = max(0.0, diesel_mw_by_year[i] - prev_diesel)
        add_gas_mw = max(0.0, gas_mw_by_year[i] - prev_gas)
        add_grid_mw = max(0.0, current_capacity_mw - prev_capacity)

        yr_smr_capex = add_smr_mw * smr_capex_per_mw
        yr_diesel_capex = add_diesel_mw * diesel_capex_per_mw
        yr_gas_capex = add_gas_mw * gas_capex_per_mw
        yr_grid_capex = add_grid_mw * grid_capex_per_mw
        yr_total_power_capex = yr_smr_capex + yr_diesel_capex + yr_gas_capex + yr_grid_capex
        
        total_power_capex += yr_total_power_capex

        # Inflation adjusted electricity rates
        escalation = (1 + inflation_rate) ** i
        cur_grid_kwh_rate = location_rate_kwh * escalation
        cur_demand_charge = location_demand_charge_kw * escalation
        
        # Energy output (MWh) by source
        mwh_smr = active_smr_mw * annual_hours * POWER_SOURCES["Small Modular Reactor (SMR)"]["availability_factor"]
        mwh_diesel = active_diesel_mw * annual_hours * POWER_SOURCES["Diesel Peaking / Prime Generators"]["availability_factor"]
        mwh_gas = active_gas_mw * annual_hours * POWER_SOURCES["Natural Gas Combined Cycle / Turbines"]["availability_factor"]
        
        # Grid supplies whatever is left of required MWh
        mwh_grid = max(0.0, annual_mwh_required - mwh_smr - mwh_diesel - mwh_gas)

        # Operating expenses ($)
        smr_opex = mwh_smr * (POWER_SOURCES["Small Modular Reactor (SMR)"]["opex_base_usd_per_kwh"] * 1000) * escalation
        diesel_opex = mwh_diesel * (POWER_SOURCES["Diesel Peaking / Prime Generators"]["opex_base_usd_per_kwh"] * 1000) * escalation
        gas_opex = mwh_gas * (POWER_SOURCES["Natural Gas Combined Cycle / Turbines"]["opex_base_usd_per_kwh"] * 1000) * escalation
        
        grid_energy_opex = mwh_grid * (cur_grid_kwh_rate * 1000)
        # Utility Demand Charges ($/kW/month * 12 months) applied to Peak Grid MW draw
        grid_demand_opex = (grid_mw_needed * 1000) * cur_demand_charge * 12
        grid_total_opex = grid_energy_opex + grid_demand_opex

        total_power_opex = smr_opex + diesel_opex + gas_opex + grid_total_opex
        blended_lcoe_kwh = total_power_opex / (annual_mwh_required * 1000) if annual_mwh_required > 0 else 0.0

        records.append({
            "year": yr_name,
            "year_index": i + 1,
            "it_capacity_mw": current_capacity_mw,
            "facility_capacity_mw": facility_power_mw,
            "annual_mwh_required": annual_mwh_required,
            "grid_mw": grid_mw_needed,
            "smr_mw": active_smr_mw,
            "diesel_mw": active_diesel_mw,
            "gas_mw": active_gas_mw,
            "mwh_grid": mwh_grid,
            "mwh_smr": mwh_smr,
            "mwh_diesel": mwh_diesel,
            "mwh_gas": mwh_gas,
            "power_capex_usd": yr_total_power_capex,
            "grid_opex_usd": grid_total_opex,
            "smr_opex_usd": smr_opex,
            "diesel_opex_usd": diesel_opex,
            "gas_opex_usd": gas_opex,
            "total_power_opex_usd": total_power_opex,
            "blended_lcoe_kwh": blended_lcoe_kwh
        })

        # Update previous state
        prev_smr = smr_mw_by_year[i]
        prev_diesel = diesel_mw_by_year[i]
        prev_gas = gas_mw_by_year[i]
        prev_capacity = current_capacity_mw

    df_power = pd.DataFrame(records)
    return df_power, total_power_capex
