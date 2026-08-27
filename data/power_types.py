"""
Power Generation and Procurement Source Specifications.
Details capital cost, levelized operational cost, lead time, and capacity constraints for Grid, SMR, Diesel, Gas, and Battery systems.
"""

POWER_SOURCES = {
    "Utility Grid Supply": {
        "type": "Utility Interconnect PPA",
        "capex_usd_per_mw": 250_000,  # Substation & high-voltage switchgear tie-in
        "opex_base_usd_per_kwh": 0.065,  # Default, dynamically replaced by selected location rate
        "lead_time_years": 1,
        "emissions_co2_kg_mwh": 380,
        "availability_factor": 0.9999,
        "description": "Standard utility high-voltage industrial transmission feed. Subject to utility rate tariffs, demand charges, and grid queue delays."
    },
    "Small Modular Reactor (SMR)": {
        "type": "On-Site Nuclear Baseload",
        "capex_usd_per_mw": 6_800_000,  # $6.8M / MW ($6,800/kW overnight capital cost)
        "opex_base_usd_per_kwh": 0.034,  # Fuel assembly, NRC licensing compliance, O&M
        "lead_time_years": 3,
        "emissions_co2_kg_mwh": 0,
        "availability_factor": 0.9500,
        "description": "Clean, 24/7 firm nuclear baseload power operating in 77 MW module increments. Zero carbon emissions, low long-term marginal cost."
    },
    "Diesel Peaking / Prime Generators": {
        "type": "On-Site Liquid Fuel Generators",
        "capex_usd_per_mw": 450_000,  # $450/kW EPA Tier 4 generator sets
        "opex_base_usd_per_kwh": 0.220,  # ULSD fuel ($3.80/gal) + high frequency engine overhaul
        "lead_time_years": 1,
        "emissions_co2_kg_mwh": 650,
        "availability_factor": 0.9800,
        "description": "Rapidly deployable on-site power generation for bridging grid queue delays, load shaving, or emergency uninterruptible backup."
    },
    "Natural Gas Combined Cycle / Turbines": {
        "type": "On-Site Thermal Generation",
        "capex_usd_per_mw": 1_250_000,  # $1.25M / MW gas turbine plant
        "opex_base_usd_per_kwh": 0.065,  # Pipeline natural gas ($3.50/MMBtu) + turbine O&M
        "lead_time_years": 2,
        "emissions_co2_kg_mwh": 350,
        "availability_factor": 0.9400,
        "description": "Dispatchable prime thermal generation fed by high-pressure interstate gas pipelines. Moderate emissions and fast ramping."
    },
    "Solar PV + 4-Hr BESS (Battery Storage)": {
        "type": "On-Site Hybrid Renewable",
        "capex_usd_per_mw": 1_450_000,  # Combined solar field + 4hr LFP BESS
        "opex_base_usd_per_kwh": 0.018,  # Panel cleaning, inverter replacements & BESS degradation
        "lead_time_years": 1,
        "emissions_co2_kg_mwh": 0,
        "availability_factor": 0.3500,  # Capacity factor with battery firming
        "description": "Zero-carbon supplemental renewable power with battery energy storage for peak demand shaving."
    }
}

def get_power_sources():
    return POWER_SOURCES
