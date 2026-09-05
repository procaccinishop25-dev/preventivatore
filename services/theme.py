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
        /* --- Brand: rosso come unico accento --- */
        --color-primary: #D92D20;
        --color-primary-hover: #B42318;
        --color-primary-light: #FEF3F2;

        /* --- Neutri --- */
        --color-bg: #F8F9FB;
        --color-surface: #FFFFFF;

        --color-title: #171717;
        --color-text: #171717;
        --color-text-secondary: #667085;
        --color-text-disabled: #98A2B3;

        --color-border: #E4E7EC;
        --color-border-hover: #D0D5DD;
        --color-border-focus: #D92D20;
        --focus-ring: rgba(217, 45, 32, 0.15);

        /* --- Stati semantici --- */
        --color-success: #12B76A;
        --color-success-light: #ECFDF3;
        --color-warning: #F79009;
        --color-warning-light: #FFFAEB;
        --color-danger: #D92D20;
        --color-danger-light: #FEF3F2;
        --color-info: #2563EB;
        --color-info-light: #EFF6FF;

        /* --- Spacing: multipli di 4 --- */
        --space-1: 4px;
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-6: 24px;
        --space-8: 32px;
        --space-10: 40px;
        --space-12: 48px;

        /* --- Radius: sobrio, non "pillola" ovunque --- */
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 10px;
        --radius-pill: 999px;

        /* --- Ombre: molto leggere --- */
        --shadow-sm: 0 1px 2px rgba(23, 23, 23, 0.04);
        --shadow-md: 0 2px 8px rgba(23, 23, 23, 0.06);
    }

    .stApp { background-color: var(--color-bg); }

    /* ============== TYPOGRAPHY — gerarchia coerente ============== */
    h1, h2, h3 {
        color: var(--color-title) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }
    /* Page title */
    h1 { font-size: 1.5rem !important; margin-bottom: var(--space-1) !important; line-height: 1.3; }
    /* Section title */
    h2 { font-size: 1.125rem !important; margin-top: var(--space-6) !important; margin-bottom: var(--space-2) !important; }
    /* Card title */
    h3 { font-size: 0.95rem !important; margin-top: var(--space-4) !important; margin-bottom: var(--space-2) !important; color: var(--color-text) !important; }

    p, .stMarkdown, label { color: var(--color-text); font-size: 0.9rem; }
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--color-text-secondary) !important; font-size: 0.8rem !important; }

    .page-header h1 { margin-bottom: 2px !important; }
    .page-header p {
        color: var(--color-text-secondary);
        font-size: 0.88rem;
        margin-top: 0;
        margin-bottom: var(--space-4);
    }

    /* Badge: dimensione tipografica dedicata, gestita da badge() in questo stesso file */

    /* ============== SIDEBAR ============== */
    [data-testid="stSidebar"] {
        background-color: var(--color-surface);
        border-right: 1px solid var(--color-border);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: var(--space-4); }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: 0 var(--space-3) var(--space-4) var(--space-3);
        margin-bottom: var(--space-2);
        border-bottom: 1px solid var(--color-border);
    }
    .sidebar-brand-icon {
        font-size: 1.3rem;
        width: 32px; height: 32px;
        display: flex; align-items: center; justify-content: center;
        background-color: var(--color-primary-light);
        border-radius: var(--radius-md);
    }
    .sidebar-brand-title { font-weight: 700; font-size: 0.92rem; color: var(--color-title); line-height: 1.2; }
    .sidebar-brand-subtitle { font-size: 0.68rem; color: var(--color-text-secondary); }

    .sidebar-divider { border-top: 1px solid var(--color-border); margin: var(--space-3) var(--space-3); }

    .sidebar-section-label {
        font-size: 0.68rem;
        font-weight: 700;
        color: var(--color-text-disabled);
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: var(--space-3) var(--space-3) var(--space-1) var(--space-3);
    }

    [data-testid="stSidebar"] [data-testid="stPageLink"] {
        border-radius: var(--radius-md);
        margin: 1px var(--space-2);
        padding: 2px var(--space-1);
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"]:hover { background-color: var(--color-bg); }
    [data-testid="stSidebar"] [data-testid="stPageLink"] p {
        font-size: 0.86rem;
        font-weight: 500;
        color: var(--color-text-secondary);
    }
    [data-testid="stSidebar"] [aria-current="page"] {
        background-color: var(--color-primary-light) !important;
        border-radius: var(--radius-md);
    }
    [data-testid="stSidebar"] [aria-current="page"] p {
        color: var(--color-primary-hover) !important;
        font-weight: 600;
    }

    .sidebar-user {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-3);
        margin: var(--space-2);
        border-top: 1px solid var(--color-border);
        font-size: 0.82rem;
        color: var(--color-text-secondary);
    }
    .sidebar-user-avatar {
        width: 28px; height: 28px;
        border-radius: 50%;
        background-color: var(--color-primary-light);
        color: var(--color-primary);
        display: flex; align-items: center; justify-content: center;
        font-weight: 700;
        font-size: 0.75rem;
        flex-shrink: 0;
    }

    /* ============== BOTTONI ============== */
    .stApp button {
        border-radius: var(--radius-md) !important;
        min-height: 40px;
        font-weight: 600 !important;
        font-size: 0.88rem;
        transition: background-color 150ms ease, border-color 150ms ease, transform 150ms ease;
        border: 1px solid var(--color-border-hover);
        background-color: var(--color-surface);
    }
    .stApp button p, .stApp button div, .stApp button span { color: #344054; }
    .stApp button:hover {
        background-color: var(--color-bg);
        border-color: var(--color-text-disabled);
    }
    .stApp button:active { transform: scale(0.98); }
    .stApp button:focus-visible {
        outline: none;
        box-shadow: 0 0 0 3px var(--focus-ring);
    }
    .stApp button:disabled { opacity: 0.5; cursor: not-allowed; }

    .stApp button[kind*="primary"] {
        background-color: var(--color-primary) !important;
        border-color: var(--color-primary) !important;
        box-shadow: var(--shadow-sm);
    }
    .stApp button[kind*="primary"] p,
    .stApp button[kind*="primary"] div,
    .stApp button[kind*="primary"] span { color: #FFFFFF !important; }
    .stApp button[kind*="primary"]:hover {
        background-color: var(--color-primary-hover) !important;
        border-color: var(--color-primary-hover) !important;
    }

    [data-testid="stDownloadButton"] button {
        background-color: var(--color-primary) !important;
        border-color: var(--color-primary) !important;
    }
    [data-testid="stDownloadButton"] button p,
    [data-testid="stDownloadButton"] button div,
    [data-testid="stDownloadButton"] button span { color: #FFFFFF !important; }
    [data-testid="stDownloadButton"] button:hover { background-color: var(--color-primary-hover) !important; }

    /* CTA principale evidenziata (Home, sidebar) */
    .cta-principale button {
        min-height: 46px !important;
        font-size: 0.95rem !important;
    }

    /* ============== CARD ============== */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--color-border) !important;
        background-color: var(--color-surface);
        padding: var(--space-1);
        box-shadow: var(--shadow-sm);
        transition: box-shadow 150ms ease, border-color 150ms ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--color-border-hover) !important;
    }

    /* ============== METRICHE ============== */
    [data-testid="stMetric"] {
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
    }
    [data-testid="stMetricValue"] { color: var(--color-title) !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: var(--color-text-secondary) !important; font-size: 0.78rem !important; }

    /* ============== INPUT / FORM ============== */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] div[data-baseweb="select"],
    [data-testid="stDateInput"] input {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--color-border-hover) !important;
        background-color: #FFFFFF !important;
        color: var(--color-title) !important;
        min-height: 40px;
        font-size: 0.88rem;
        transition: border-color 150ms ease, box-shadow 150ms ease;
    }
    [data-testid="stTextInput"] input:hover,
    [data-testid="stNumberInput"] input:hover,
    [data-testid="stTextArea"] textarea:hover { border-color: var(--color-text-disabled) !important; }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--color-border-focus) !important;
        box-shadow: 0 0 0 3px var(--focus-ring) !important;
    }
    ::placeholder { color: var(--color-text-disabled) !important; }

    label {
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        color: var(--color-text) !important;
        margin-bottom: var(--space-1) !important;
    }

    /* ============== EXPANDER ============== */
    [data-testid="stExpander"] {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--color-border) !important;
        background-color: var(--color-surface);
    }
    [data-testid="stExpander"] summary { font-size: 0.88rem; font-weight: 500; }

    /* ============== TABELLE MARKDOWN ============== */
    .stMarkdown table { border-collapse: collapse; width: 100%; }
    .stMarkdown table thead th {
        background-color: var(--color-bg) !important;
        color: #475467 !important;
        border-bottom: 1px solid var(--color-border) !important;
        font-size: 0.78rem;
        font-weight: 600;
        padding: var(--space-2) var(--space-3) !important;
    }
    .stMarkdown table tbody td {
        background-color: var(--color-surface);
        border-bottom: 1px solid var(--color-border) !important;
        padding: var(--space-2) var(--space-3) !important;
        font-size: 0.86rem;
        color: var(--color-text);
    }
    .stMarkdown table tbody tr:hover td { background-color: var(--color-bg); }

    [data-testid="stDataFrame"] { border-radius: var(--radius-lg); border: 1px solid var(--color-border); }

    /* ============== TABS / DIALOG ============== */
    [data-testid="stTabs"] button[role="tab"] { font-size: 0.86rem; font-weight: 500; }

    div[role="dialog"] {
        border-radius: var(--radius-lg) !important;
    }

    /* ============== UTILITY DI SPACING ============== */
    .section-spacer { height: var(--space-6); }
    .spacer-sm { height: var(--space-2); }
    .spacer-lg { height: var(--space-10); }

    [data-testid="stCheckbox"], [data-testid="stRadio"] label { min-height: 34px; color: var(--color-text); font-weight: 400 !important; }

    a { color: var(--color-primary) !important; transition: color 150ms ease; }
    a:hover { color: var(--color-primary-hover) !important; }

    /* ============== EMPTY STATE ============== */
    .empty-state {
        text-align: center;
        padding: var(--space-12) var(--space-6);
        color: var(--color-text-secondary);
    }
    .empty-state-icon {
        font-size: 2.2rem;
        margin-bottom: var(--space-3);
        opacity: 0.6;
    }
    .empty-state-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--color-title);
        margin-bottom: var(--space-1);
    }
    .empty-state-description {
        font-size: 0.86rem;
        color: var(--color-text-secondary);
        margin-bottom: var(--space-4);
        max-width: 360px;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """, unsafe_allow_html=True)


def badge(testo, tipo="neutral"):
    stili = {
        "success":   ("#027A48", "#ECFDF3"),
        "warning":   ("#B54708", "#FFFAEB"),
        "danger":    ("#B42318", "#FEF3F2"),
        "info":      ("#1D4ED8", "#EFF6FF"),
        "bozza":     ("#475467", "#F2F4F7"),
        "inviato":   ("#1D4ED8", "#EFF6FF"),
        "accettato": ("#027A48", "#ECFDF3"),
        "rifiutato": ("#B42318", "#FEF3F2"),
        "neutral":   ("#475467", "#F2F4F7"),
    }
    colore_testo, colore_bg = stili.get(tipo, stili["neutral"])
    return (
        f"<span style='background-color:{colore_bg}; color:{colore_testo}; "
        f"padding:3px 10px; border-radius:6px; font-size:0.74rem; font-weight:600; "
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
