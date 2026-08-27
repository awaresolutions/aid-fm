"""
Global configuration, styling, and UI themes for AI Data Center Financial Model.
Forced Light Theme edition with complete background color overrides.
"""

APP_TITLE = "AI Data Center Financial & Power Modeling System"
APP_SUBTITLE = "5-Year Capital, Power Procurement (Grid / SMR / Diesel), Geospatial TS/SCI Site Selector & Token Economics Model"

DEFAULT_TIMELINE_YEARS = 5
DEFAULT_PUE = 1.15
DEFAULT_INFLATION_RATE = 0.035
DEFAULT_DISCOUNT_RATE = 0.08
DEFAULT_DC_BUILD_COST_PER_MW = 8_500_000  # $8.5M per MW Core & Shell + Liquid Cooling Infrastructure

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Force full page and main containers light background */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] {
        background-color: #e2e8f0 !important;
        color: #0f172a !important;
    }

    /* Header bar transparent / light */
    header[data-testid="stHeader"], [data-testid="stHeader"] {
        background-color: #e2e8f0 !important;
    }

    /* Header styling with strong contrast border and shadow */
    .app-header {
        background: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-left: 8px solid #2563eb !important;
        padding: 24px 32px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.1), 0 8px 10px -6px rgba(15, 23, 42, 0.05);
    }

    .app-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a !important;
        margin: 0;
        letter-spacing: -0.025em;
    }

    .app-subtitle {
        color: #334155 !important;
        font-size: 1.05rem;
        margin-top: 6px;
        font-weight: 600;
    }

    /* Metric Cards - Pure White with distinct shadow and top accent line */
    .metric-card {
        background: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-top: 4px solid #2563eb !important;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -2px rgba(15, 23, 42, 0.04);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        border-color: #1d4ed8 !important;
        box-shadow: 0 20px 25px -5px rgba(37, 99, 235, 0.15), 0 8px 10px -6px rgba(37, 99, 235, 0.1);
    }

    .metric-title {
        color: #475569 !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #0f172a !important;
        font-size: 1.85rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
    }

    .metric-subtext {
        color: #1d4ed8 !important;
        font-size: 0.85rem;
        margin-top: 6px;
        font-weight: 700;
    }

    /* Status badges with rich contrast */
    .badge-ts {
        background-color: #fee2e2 !important;
        color: #991b1b !important;
        border: 1.5px solid #f87171 !important;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 800;
    }

    .badge-smr {
        background-color: #d1fae5 !important;
        color: #065f46 !important;
        border: 1.5px solid #34d399 !important;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 800;
    }

    .badge-grid {
        background-color: #dbeafe !important;
        color: #1e40af !important;
        border: 1.5px solid #60a5fa !important;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 800;
    }

    /* Streamlit Tab styling override with crisp contrast */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #cbd5e1 !important;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #94a3b8 !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 8px;
        color: #334155 !important;
        font-weight: 700;
        font-size: 0.95rem;
        padding: 0 20px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #1e3a8a !important;
        border: 2px solid #2563eb !important;
        box-shadow: 0 4px 10px rgba(15, 23, 42, 0.12);
    }

    /* Sidebar container styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 2px solid #cbd5e1 !important;
    }

    /* All text force dark */
    p, span, label, h1, h2, h3, h4, h5, h6, .stMarkdown {
        color: #0f172a !important;
    }
</style>
"""
