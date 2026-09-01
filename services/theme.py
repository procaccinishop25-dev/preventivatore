import streamlit as st


def apply_custom_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    :root {
        --color-primary: #4F46E5;
        --color-primary-dark: #4338CA;
        --color-primary-light: #EEF2FF;
        --color-text: #0F172A;
        --color-text-secondary: #64748B;
        --color-border: #E2E8F0;
        --color-bg: #F8FAFC;
        --color-surface: #FFFFFF;
        --color-success: #16A34A;
        --color-success-bg: #DCFCE7;
        --color-warning: #D97706;
        --color-warning-bg: #FEF3C7;
        --color-danger: #DC2626;
        --color-danger-bg: #FEE2E2;
    }

    .stApp { background-color: var(--color-bg); }

    h1, h2, h3 {
        color: var(--color-text) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    h1 { font-size: 1.9rem !important; margin-bottom: 0.25rem !important; }
    h2, h3 { font-size: 1.15rem !important; margin-top: 1.5rem !important; }
    p, .stMarkdown, .stCaption { color: var(--color-text-secondary); }

    .page-header h1 { margin-bottom: 0.15rem !important; }
    .page-header p { color: var(--color-text-secondary); font-size: 0.95rem; margin-top: 0; }

    [data-testid="stSidebar"] {
        background-color: var(--color-surface);
        border-right: 1px solid var(--color-border);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0 0.5rem 1.2rem 0.5rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid var(--color-border);
    }
    .sidebar-brand-icon { font-size: 1.6rem; }
    .sidebar-brand-title { font-weight: 700; font-size: 1rem; color: var(--color-text); line-height: 1.2; }
    .sidebar-brand-subtitle { font-size: 0.72rem; color: var(--color-text-secondary); }
    .sidebar-divider { border-top: 1px solid var(--color-border); margin: 0.6rem 0.5rem; }
    [data-testid="stSidebar"] [data-testid="stPageLink"] {
        border-radius: 10px;
        margin: 2px 0.3rem;
        padding: 0.15rem 0.3rem;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"]:hover { background-color: var(--color-primary-light); }
    [data-testid="stSidebar"] [data-testid="stPageLink"] p {
        font-size: 0.92rem;
        font-weight: 500;
        color: var(--color-text);
    }

    .stApp button {
        border-radius: 10px !important;
        min-height: 42px;
        font-weight: 600 !important;
        transition: all 0.15s ease;
        border: 1px solid var(--color-border);
    }
    .stApp button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.12);
    }
    [data-testid="stDownloadButton"] button, button[kind="primary"] {
        box-shadow: 0 2px 6px rgba(79, 70, 229, 0.25);
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        border: 1px solid var(--color-border) !important;
        background-color: var(--color-surface);
        padding: 0.4rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        transition: box-shadow 0.15s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08); }

    [data-testid="stMetric"] {
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: 14px;
        padding: 1rem 1.1rem;
    }
    [data-testid="stMetricValue"] { color: var(--color-primary) !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: var(--color-text-secondary) !important; font-size: 0.82rem !important; }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        border-radius: 10px !important;
        min-height: 42px;
    }

    [data-testid="stExpander"] {
        border-radius: 14px !important;
        border: 1px solid var(--color-border) !important;
        background-color: var(--color-surface);
    }

    .section-spacer { height: 1.2rem; }

    [data-testid="stCheckbox"], [data-testid="stRadio"] label { min-height: 38px; }
    </style>
    """, unsafe_allow_html=True)


def badge(testo, tipo="neutral"):
    colori = {
        "success": ("var(--color-success)", "var(--color-success-bg)"),
        "warning": ("var(--color-warning)", "var(--color-warning-bg)"),
        "danger": ("var(--color-danger)", "var(--color-danger-bg)"),
        "info": ("var(--color-primary)", "var(--color-primary-light)"),
        "neutral": ("#475569", "#F1F5F9"),
    }
    colore_testo, colore_bg = colori.get(tipo, colori["neutral"])
    return (
        f"<span style='background-color:{colore_bg}; color:{colore_testo}; "
        f"padding:3px 10px; border-radius:999px; font-size:0.78rem; font-weight:600; "
        f"display:inline-block;'>{testo}</span>"
    )
