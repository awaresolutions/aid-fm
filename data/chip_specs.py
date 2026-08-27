"""
AI Accelerator Chip Specifications Database.
Includes power draw, compute capability, token throughput, rack density, and pricing.
"""

CHIP_DATABASE = {
    "NVIDIA GB300 NVL72 (Blackwell Ultra)": {
        "architecture": "Blackwell Ultra (2025/2026)",
        "form_factor": "NVL72 Rack System (72 GPUs + 36 Grace CPUs)",
        "tdp_kw_per_rack": 140.0,
        "tdp_watts_per_chip": 1950,
        "gpus_per_rack": 72,
        "fp8_tflops_per_chip": 7000.0,
        "fp4_tflops_per_chip": 14000.0,
        "tokens_per_sec_per_rack": 1_850_000,
        "tokens_per_sec_per_chip": 25_694,
        "rack_unit_cost_usd": 3_850_000,
        "chip_unit_cost_usd": 53_472,
        "cooling_type": "Direct-to-Chip Liquid Cooling (DLC)",
        "memory_capacity_gb_per_chip": 288,  # HBM3e
        "memory_bandwidth_tb_s": 8.0,
        "description": "NVIDIA's flagship 2026 Blackwell Ultra NVL72 rack platform delivering extreme FP4 inference density and native NVLink network switching."
    },
    "NVIDIA Vera Rubin NVL72": {
        "architecture": "Vera Rubin (2026 Next-Gen)",
        "form_factor": "NVL72 Rack System (72 Rubin GPUs + Vera CPUs)",
        "tdp_kw_per_rack": 180.0,
        "tdp_watts_per_chip": 2500,
        "gpus_per_rack": 72,
        "fp8_tflops_per_chip": 16000.0,
        "fp4_tflops_per_chip": 32000.0,
        "tokens_per_sec_per_rack": 4_500_000,
        "tokens_per_sec_per_chip": 62_500,
        "rack_unit_cost_usd": 4_950_000,
        "chip_unit_cost_usd": 68_750,
        "cooling_type": "Hybrid Liquid / Immersion Cooling",
        "memory_capacity_gb_per_chip": 384,  # HBM4
        "memory_bandwidth_tb_s": 13.0,
        "description": "Next-generation Vera Rubin architecture featuring Vera Arm-based CPUs, Rubin GPUs with HBM4 memory, and extreme FP4 AI throughput."
    },
    "NVIDIA B200 NVL72 (Blackwell)": {
        "architecture": "Blackwell (2024/2025)",
        "form_factor": "NVL72 Rack System (72 GPUs + 36 Grace CPUs)",
        "tdp_kw_per_rack": 120.0,
        "tdp_watts_per_chip": 1200,
        "gpus_per_rack": 72,
        "fp8_tflops_per_chip": 5000.0,
        "fp4_tflops_per_chip": 10000.0,
        "tokens_per_sec_per_rack": 1_200_000,
        "tokens_per_sec_per_chip": 16_666,
        "rack_unit_cost_usd": 3_200_000,
        "chip_unit_cost_usd": 44_444,
        "cooling_type": "Direct-to-Chip Liquid Cooling (DLC)",
        "memory_capacity_gb_per_chip": 192,
        "memory_bandwidth_tb_s": 8.0,
        "description": "Standard Blackwell NVL72 enterprise solution designed for trillion-parameter LLM training and high-throughput inference."
    },
    "NVIDIA H200 / H100 SXM5": {
        "architecture": "Hopper (2023/2024)",
        "form_factor": "HGX 8-GPU Node Server (4 Nodes/Rack)",
        "tdp_kw_per_rack": 40.0,
        "tdp_watts_per_chip": 700,
        "gpus_per_rack": 32,
        "fp8_tflops_per_chip": 2000.0,
        "fp4_tflops_per_chip": 4000.0,
        "tokens_per_sec_per_rack": 350_000,
        "tokens_per_sec_per_chip": 10_937,
        "rack_unit_cost_usd": 1_200_000,
        "chip_unit_cost_usd": 35_000,
        "cooling_type": "Air-Cooled / Rear-Door Heat Exchanger",
        "memory_capacity_gb_per_chip": 141,
        "memory_bandwidth_tb_s": 4.8,
        "description": "Workhorse Hopper architecture powering cloud inference and baseline enterprise data center deployments."
    },
    "AMD Instinct MI350X": {
        "architecture": "CDNA4 (2025/2026)",
        "form_factor": "8-OAM Server Rack System (32 GPUs/Rack)",
        "tdp_kw_per_rack": 110.0,
        "tdp_watts_per_chip": 1000,
        "gpus_per_rack": 32,
        "fp8_tflops_per_chip": 4800.0,
        "fp4_tflops_per_chip": 9600.0,
        "tokens_per_sec_per_rack": 1_400_000,
        "tokens_per_sec_per_chip": 43_750,
        "rack_unit_cost_usd": 2_950_000,
        "chip_unit_cost_usd": 38_000,
        "cooling_type": "Direct-to-Chip Liquid Cooling (DLC)",
        "memory_capacity_gb_per_chip": 288,
        "memory_bandwidth_tb_s": 8.0,
        "description": "AMD's premier CDNA4 accelerator with 288GB HBM3e and FP4 math formatting for high-efficiency enterprise AI workloads."
    }
}

def get_chip_names():
    return list(CHIP_DATABASE.keys())

def get_chip_info(chip_name: str):
    return CHIP_DATABASE.get(chip_name, CHIP_DATABASE["NVIDIA GB300 NVL72 (Blackwell Ultra)"])
