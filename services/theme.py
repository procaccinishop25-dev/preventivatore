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
        --color-primary: #2563EB;
        --color-primary-hover: #1D4ED8;
        --color-primary-active: #1E40AF;
        --color-primary-light: #EFF6FF;

        --color-bg: #F8FAFC;
        --color-bg-secondary: #F1F5F9;
        --color-surface: #FFFFFF;

        --color-title: #0F172A;
        --color-text: #1E293B;
        --color-text-secondary: #64748B;
        --color-text-disabled: #94A3B8;

        --color-border: #E2E8F0;
        --color-border-hover: #CBD5E1;
        --color-border-focus: #2563EB;
        --focus-ring: rgba(37, 99, 235, 0.15);

        --color-success: #16A34A;
        --color-success-light: #F0FDF4;
        --color-warning: #D97706;
        --color-warning-light: #FFFBEB;
        --color-danger: #DC2626;
        --color-danger-hover: #B91C1C;
        --color-danger-light: #FEF2F2;
        --color-info: #2563EB;
        --color-info-light: #EFF6FF;

        --radius: 8px;
    }

    .stApp { background-color: var(--color-bg); }

    h1, h2, h3 {
        color: var(--color-title) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }
    h1 { font-size: 1.75rem !important; margin-bottom: 0.2rem !important; }
    h2, h3 { font-size: 1.05rem !important; margin-top: 1.4rem !important; color: var(--color-text) !important; }
    p, .stMarkdown, .stCaption, label { color: var(--color-text); }

    .page-header h1 { margin-bottom: 0.15rem !important; }
    .page-header p { color: var(--color-text-secondary); font-size: 0.92rem; margin-top: 0; }

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {
        background-color: var(--color-surface);
        border-right: 1px solid var(--color-border);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.1rem; }
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0 0.6rem 1rem 0.6rem;
        margin-bottom: 0.4rem;
        border-bottom: 1px solid var(--color-border);
    }
    .sidebar-brand-icon { font-size: 1.4rem; }
    .sidebar-brand-title { font-weight: 700; font-size: 0.95rem; color: var(--color-title); line-height: 1.2; }
    .sidebar-brand-subtitle { font-size: 0.7rem; color: var(--color-text-secondary); }
    .sidebar-divider { border-top: 1px solid var(--color-border); margin: 0.5rem 0.6rem; }

    [data-testid="stSidebar"] [data-testid="stPageLink"] {
        border-radius: var(--radius);
        margin: 1px 0.4rem;
        padding: 0.1rem 0.3rem;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"]:hover { background-color: var(--color-bg); }
    [data-testid="stSidebar"] [data-testid="stPageLink"] p {
        font-size: 0.88rem;
        font-weight: 500;
        color: var(--color-text-secondary);
    }
    [data-testid="stSidebar"] [aria-current="page"] {
        background-color: var(--color-primary-light) !important;
        border-radius: var(--radius);
    }
    [data-testid="stSidebar"] [aria-current="page"] p {
        color: var(--color-primary-hover) !important;
        font-weight: 600;
    }

    /* ---------- BOTTONI ---------- */
    .stApp button {
        border-radius: var(--radius) !important;
        min-height: 42px;
        font-weight: 600 !important;
        font-size: 0.9rem;
        transition: background-color 0.12s ease, border-color 0.12s ease;
        border: 1px solid var(--color-border-hover);
        background-color: var(--color-surface);
    }
    .stApp button p, .stApp button div, .stApp button span {
        color: #334155;
    }
    .stApp button:hover {
        background-color: var(--color-bg);
        border-color: var(--color-text-disabled);
    }

    .stApp button[kind*="primary"] {
        background-color: var(--color-primary) !important;
        border-color: var(--color-primary) !important;
    }
    .stApp button[kind*="primary"] p,
    .stApp button[kind*="primary"] div,
    .stApp button[kind*="primary"] span {
        color: #FFFFFF !important;
    }
    .stApp button[kind*="primary"]:hover {
        background-color: var(--color-primary-hover) !important;
        border-color: var(--color-primary-hover) !important;
    }
    .stApp button[kind*="primary"]:active {
        background-color: var(--color-primary-active) !important;
        border-color: var(--color-primary-active) !important;
    }

    [data-testid="stDownloadButton"] button {
        background-color: var(--color-primary) !important;
        border-color: var(--color-primary) !important;
    }
    [data-testid="stDownloadButton"] button p,
    [data-testid="stDownloadButton"] button div,
    [data-testid="stDownloadButton"] button span {
        color: #FFFFFF !important;
    }
    [data-testid="stDownloadButton"] button:hover {
        background-color: var(--color-primary-hover) !important;
    }

    /* ---------- CARD ---------- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 10px !important;
        border: 1px solid var(--color-border) !important;
        background-color: var(--color-surface);
        padding: 0.35rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
        transition: box-shadow 0.12s ease, border-color 0.12s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.05);
        border-color: var(--color-border-hover) !important;
    }

    /* ---------- METRICHE ---------- */
    [data-testid="stMetric"] {
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: 10px;
        padding: 0.9rem 1rem;
    }
    [data-testid="stMetricValue"] { color: var(--color-title) !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: var(--color-text-secondary) !important; font-size: 0.8rem !important; }

    /* ---------- INPUT ---------- */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] div[data-baseweb="select"],
    [data-testid="stDateInput"] input {
        border-radius: var(--radius) !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        color: var(--color-title) !important;
        min-height: 42px;
    }
    [data-testid="stTextInput"] input:hover,
    [data-testid="stNumberInput"] input:hover,
    [data-testid="stTextArea"] textarea:hover {
        border-color: var(--color-text-disabled) !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--color-border-focus) !important;
        box-shadow: 0 0 0 3px var(--focus-ring) !important;
    }
    ::placeholder { color: var(--color-text-disabled) !important; }

    /* ---------- EXPANDER ---------- */
    [data-testid="stExpander"] {
        border-radius: 10px !important;
        border: 1px solid var(--color-border) !important;
        background-color: var(--color-surface);
    }

    /* ---------- TABELLE MARKDOWN ---------- */
    .stMarkdown table { border-collapse: collapse; width: 100%; }
    .stMarkdown table thead th {
        background-color: var(--color-bg) !important;
        color: #475569 !important;
        border-bottom: 1px solid var(--color-border) !important;
        font-size: 0.82rem;
        text-transform: none;
        font-weight: 600;
        padding: 8px 10px !important;
    }
    .stMarkdown table tbody td {
        background-color: var(--color-surface);
        border-bottom: 1px solid #F1F5F9 !important;
        padding: 8px 10px !important;
        color: var(--color-text);
    }
    .stMarkdown table tbody tr:hover td { background-color: var(--color-bg); }

    /* ---------- DATAFRAME ---------- */
    [data-testid="stDataFrame"] { border-radius: 10px; border: 1px solid var(--color-border); }

    .section-spacer { height: 1.1rem; }

    [data-testid="stCheckbox"], [data-testid="stRadio"] label { min-height: 36px; color: var(--color-text); }

    a { color: var(--color-primary) !important; }
    </style>
    """, unsafe_allow_html=True)


def badge(testo, tipo="neutral"):
    stili = {
        "success":        ("#15803D", "#F0FDF4"),
        "warning":        ("#D97706", "#FFFBEB"),
        "danger":         ("#B91C1C", "#FEF2F2"),
        "info":           ("#1D4ED8", "#EFF6FF"),
        "in_lavorazione": ("#1D4ED8", "#EFF6FF"),
        "completato":     ("#15803D", "#F0FDF4"),
        "inviato":        ("#1D4ED8", "#EFF6FF"),
        "accettato":      ("#15803D", "#F0FDF4"),
        "rifiutato":      ("#B91C1C", "#FEF2F2"),
        "bozza":          ("#475569", "#F1F5F9"),
        "neutral":        ("#475569", "#F1F5F9"),
    }
    colore_testo, colore_bg = stili.get(tipo, stili["neutral"])
    return (
        f"<span style='background-color:{colore_bg}; color:{colore_testo}; "
        f"padding:3px 10px; border-radius:6px; font-size:0.76rem; font-weight:600; "
        f"display:inline-block;'>{testo}</span>"
    )


def stato_badge(stato):
    """Badge dedicato per lo stato dei preventivi (bozza/inviato/accettato/rifiutato)."""
    mappa = {
        "bozza": ("Bozza", "bozza"),
        "inviato": ("Inviato", "inviato"),
        "accettato": ("Accettato", "accettato"),
        "rifiutato": ("Rifiutato", "rifiutato"),
    }
    etichetta, tipo = mappa.get(stato, (stato.capitalize() if stato else "—", "neutral"))
    return badge(etichetta, tipo)
