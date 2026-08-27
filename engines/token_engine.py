"""
Token Economics & Hardware Capacity Matching Engine.
Calculates required AI chips, 50 MW data center building blocks, and cost per 1M tokens.
"""

from data.chip_specs import CHIP_DATABASE

def calculate_token_economics(
    daily_tokens_target: float,  # e.g., 50_000_000_000 (50 Billion tokens/day)
    chip_selection_dict: dict,   # e.g., {"NVIDIA GB300 NVL72 (Blackwell Ultra)": 0.70, "NVIDIA Vera Rubin NVL72": 0.30}
    total_5year_tco_usd: float
):
    """
    Computes capacity sizing to fulfill target token demand and calculates token cost metrics.
    """
    # 24 hours * 3600 seconds = 86,400 seconds/day
    required_tokens_per_sec = daily_tokens_target / 86400.0
    
    # Calculate weighted average token throughput per rack and per MW
    weighted_tokens_per_sec_per_rack = 0.0
    weighted_kw_per_rack = 0.0
    weighted_rack_cost = 0.0
    weighted_chips_per_rack = 0.0

    for chip_name, weight in chip_selection_dict.items():
        if weight > 0 and chip_name in CHIP_DATABASE:
            spec = CHIP_DATABASE[chip_name]
            weighted_tokens_per_sec_per_rack += weight * spec["tokens_per_sec_per_rack"]
            weighted_kw_per_rack += weight * spec["tdp_kw_per_rack"]
            weighted_rack_cost += weight * spec["rack_unit_cost_usd"]
            weighted_chips_per_rack += weight * spec["gpus_per_rack"]

    if weighted_tokens_per_sec_per_rack <= 0:
        weighted_tokens_per_sec_per_rack = CHIP_DATABASE["NVIDIA GB300 NVL72 (Blackwell Ultra)"]["tokens_per_sec_per_rack"]
        weighted_kw_per_rack = CHIP_DATABASE["NVIDIA GB300 NVL72 (Blackwell Ultra)"]["tdp_kw_per_rack"]
        weighted_rack_cost = CHIP_DATABASE["NVIDIA GB300 NVL72 (Blackwell Ultra)"]["rack_unit_cost_usd"]
        weighted_chips_per_rack = 72

    # Racks required to meet token target
    total_racks_needed = required_tokens_per_sec / weighted_tokens_per_sec_per_rack
    total_chips_needed = total_racks_needed * weighted_chips_per_rack
    total_it_power_kw = total_racks_needed * weighted_kw_per_rack
    total_it_power_mw = total_it_power_kw / 1000.0
    
    # Number of 50 MW building blocks
    num_50mw_blocks = max(1, int(np.ceil(total_it_power_mw / 50.0)))
    datacenter_allocated_mw = num_50mw_blocks * 50.0
    
    total_hardware_capex_usd = total_racks_needed * weighted_rack_cost

    # 5-Year Token Volume
    annual_tokens = daily_tokens_target * 365.25
    five_year_total_tokens = annual_tokens * 5.0
    
    # Cost per 1 Million Tokens ($) based on 5-Year TCO
    cost_per_1m_tokens = (total_5year_tco_usd / five_year_total_tokens) * 1_000_000 if five_year_total_tokens > 0 else 0.0

    return {
        "required_tokens_per_sec": required_tokens_per_sec,
        "total_racks_needed": total_racks_needed,
        "total_chips_needed": total_chips_needed,
        "total_it_power_mw": total_it_power_mw,
        "num_50mw_blocks": num_50mw_blocks,
        "datacenter_allocated_mw": datacenter_allocated_mw,
        "total_hardware_capex_usd": total_hardware_capex_usd,
        "annual_tokens": annual_tokens,
        "five_year_total_tokens": five_year_total_tokens,
        "cost_per_1m_tokens_usd": cost_per_1m_tokens
    }

import numpy as np
