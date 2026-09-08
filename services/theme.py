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
        /* --- Brand: rosso ora DOMINANTE, non solo accento --- */
        --color-primary: #D92D20;
        --color-primary-hover: #B42318;
        --color-primary-light: #FEF3F2;
        --color-primary-border: #F5A9A0;

        --color-bg: #F5F6F8;
        --color-surface: #FFFFFF;

        --color-title: #171717;
        --color-text: #2D2F31;
        --color-text-quiet: #4B4F54;
        --color-text-secondary: #6B7076;
        --color-text-disabled: #9CA0A6;

        --color-border: #E4E5E7;
        --color-border-visible: #D9DBDE;
        --color-border-hover: #C4C7CB;
        --color-border-focus: #D92D20;
        --focus-ring: rgba(217, 45, 32, 0.18);

        --color-success: #12B76A;
        --color-success-light: #ECFDF3;
        --color-warning: #F79009;
        --color-warning-light: #FFFAEB;
        --color-danger: #D92D20;
        --color-danger-light: #FEF3F2;
        --color-info: #2563EB;
        --color-info-light: #EFF6FF;

        --space-1: 4px;
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-6: 24px;
        --space-8: 32px;
        --space-10: 40px;
        --space-12: 48px;

        --radius-sm: 8px;
        --radius-md: 10px;
        --radius-lg: 14px;
        --radius-pill: 999px;

        --shadow-sm: 0 1px 3px rgba(23, 23, 23, 0.05);
        --shadow-md: 0 4px 12px rgba(217, 45, 32, 0.08);
    }

    .stApp { background-color: var(--color-bg); }

    /* ============== TYPOGRAPHY ============== */
    h1, h2, h3 {
        color: var(--color-title) !important;
        font-weight: 700 !important;
        letter-spacing: -0.015em;
    }
    h1 { font-size: 1.5rem !important; margin-bottom: 2px !important; line-height: 1.3; }
    h2 { font-size: 1.05rem !important; margin-top: var(--space-6) !important; margin-bottom: var(--space-3) !important; color: var(--color-title) !important; font-weight: 700 !important; }
    h3 { font-size: 0.9rem !important; margin-top: var(--space-3) !important; margin-bottom: var(--space-1) !important; color: var(--color-text) !important; font-weight: 600 !important; }

    p, .stMarkdown, label { color: var(--color-text); font-size: 0.87rem; }
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--color-text-secondary) !important; font-size: 0.78rem !important; }

    .page-header p { color: var(--color-text-secondary); font-size: 0.87rem; margin-top: 0; margin-bottom: var(--space-4); }

    /* ============== SIDEBAR — rossa piena ============== */
    [data-testid="stSidebar"] {
        background-color: var(--color-primary);
        border-right: none;
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: var(--space-4); }
    [data-testid="stSidebar"] * { color: #FFFFFF; }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: 0 var(--space-4) var(--space-4) var(--space-4);
        margin-bottom: var(--space-2);
    }
    .sidebar-brand-icon {
        font-size: 1.1rem;
        width: 32px; height: 32px;
        display: flex; align-items: center; justify-content: center;
        background-color: #FFFFFF;
        color: var(--color-primary);
        border-radius: var(--radius-sm);
        font-weight: 800;
        flex-shrink: 0;
    }
    .sidebar-brand-title { font-weight: 700; font-size: 0.95rem; color: #FFFFFF !important; }

    .sidebar-divider { border-top: 1px solid rgba(255,255,255,0.2); margin: var(--space-3) var(--space-3); }

    .sidebar-section-label {
        font-size: 0.66rem;
        font-weight: 700;
        color: rgba(255,255,255,0.65) !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: var(--space-3) var(--space-3) 2px var(--space-4);
    }

    [data-testid="stSidebar"] [data-testid="stPageLink"] {
        border-radius: var(--radius-sm);
        margin: 2px var(--space-2);
        padding: 4px var(--space-2);
        transition: background-color 150ms ease;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"]:hover { background-color: rgba(255,255,255,0.12); }
    [data-testid="stSidebar"] [data-testid="stPageLink"] p {
        font-size: 0.87rem;
        font-weight: 500;
        color: rgba(255,255,255,0.9) !important;
    }
    [data-testid="stSidebar"] [aria-current="page"] {
        background-color: #FFFFFF !important;
        border-radius: var(--radius-sm);
    }
    [data-testid="stSidebar"] [aria-current="page"] p {
        color: var(--color-primary) !important;
        font-weight: 700;
    }

    .sidebar-cta-primary { margin: var(--space-1) var(--space-2) var(--space-2) var(--space-2); }
    .sidebar-cta-primary [data-testid="stPageLink"] {
        background-color: rgba(255,255,255,0.15) !important;
        border: 1.5px dashed rgba(255,255,255,0.5);
        border-radius: var(--radius-md) !important;
        margin: 0 !important;
        padding: 7px var(--space-2) !important;
    }
    .sidebar-cta-primary [data-testid="stPageLink"] p { color: #FFFFFF !important; font-weight: 700 !important; }
    .sidebar-cta-primary [data-testid="stPageLink"]:hover { background-color: rgba(255,255,255,0.25) !important; }

    .sidebar-user {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-3) var(--space-4);
        margin: var(--space-2) 0 0 0;
        border-top: 1px solid rgba(255,255,255,0.2);
        font-size: 0.82rem;
        color: rgba(255,255,255,0.85) !important;
    }
    .sidebar-user-avatar {
        width: 26px; height: 26px;
        border-radius: 50%;
        background-color: #FFFFFF;
        color: var(--color-primary);
        display: flex; align-items: center; justify-content: center;
        font-weight: 800;
        font-size: 0.7rem;
        flex-shrink: 0;
    }

    /* ============== BOTTONI — pieni, a pillola ============== */
    button {
        border-radius: var(--radius-pill) !important;
        min-height: 38px !important;
        height: 38px;
        font-weight: 600 !important;
        font-size: 0.86rem;
        padding-left: 18px !important;
        padding-right: 18px !important;
        transition: background-color 150ms ease, border-color 150ms ease, transform 150ms ease, box-shadow 150ms ease;
        border: 1.5px solid var(--color-border-visible);
        background-color: var(--color-surface);
        box-shadow: none !important;
    }
    button p, button div, button span { color: var(--color-text-quiet); }
    button:hover { background-color: var(--color-bg); border-color: var(--color-border-hover); }
    button:active { transform: scale(0.97); }
    button:focus-visible { outline: none; box-shadow: 0 0 0 3px var(--focus-ring) !important; }
    button:disabled { opacity: 0.45; cursor: not-allowed; }

    button[kind*="primary"] {
        background-color: var(--color-primary) !important;
        border-color: var(--color-primary) !important;
        box-shadow: var(--shadow-md) !important;
    }
    button[kind*="primary"] p, button[kind*="primary"] div, button[kind*="primary"] span { color: #FFFFFF !important; font-weight: 700 !important; }
    button[kind*="primary"]:hover { background-color: var(--color-primary-hover) !important; border-color: var(--color-primary-hover) !important; }

    .btn-ghost button { border-color: transparent !important; background-color: transparent !important; box-shadow: none !important; }
    .btn-ghost button:hover { background-color: var(--color-primary-light) !important; }

    [data-testid="stDownloadButton"] button {
        background-color: var(--color-primary) !important;
        border-color: var(--color-primary) !important;
        box-shadow: var(--shadow-md) !important;
    }
    [data-testid="stDownloadButton"] button p, [data-testid="stDownloadButton"] button div, [data-testid="stDownloadButton"] button span { color: #FFFFFF !important; font-weight: 700 !important; }
    [data-testid="stDownloadButton"] button:hover { background-color: var(--color-primary-hover) !important; }

    .cta-principale button { min-height: 42px !important; height: 42px; font-size: 0.9rem !important; }

    /* ============== CARD — bordo rosso tenue visibile, decisa ============== */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: var(--radius-lg) !important;
        border: 1.5px solid var(--color-primary-border) !important;
        background-color: var(--color-surface);
        padding: var(--space-1);
        box-shadow: var(--shadow-sm);
        transition: border-color 150ms ease, box-shadow 150ms ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: var(--color-primary) !important;
        box-shadow: var(--shadow-md);
    }

    .row-actions { opacity: 1; }

    /* ============== METRICHE — numeri grandi e rossi ============== */
    [data-testid="stMetric"] {
        background-color: var(--color-surface);
        border: 1.5px solid var(--color-primary-border);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
    }
    [data-testid="stMetricValue"] {
        color: var(--color-primary) !important;
        font-weight: 800 !important;
        font-size: 1.9rem !important;
        font-variant-numeric: tabular-nums;
    }
    [data-testid="stMetricLabel"] { color: var(--color-text-secondary) !important; font-size: 0.78rem !important; font-weight: 600; }

    .num-tabular { font-variant-numeric: tabular-nums; font-feature-settings: "tnum"; text-align: right; display: inline-block; }

    /* ============== INPUT / FORM ============== */
    input, textarea { accent-color: var(--color-primary); }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] div[data-baseweb="select"],
    [data-testid="stDateInput"] input {
        border-radius: var(--radius-md) !important;
        border: 1.5px solid var(--color-border-visible) !important;
        background-color: #FFFFFF !important;
        color: var(--color-title) !important;
        min-height: 38px;
        font-size: 0.86rem;
        transition: border-color 150ms ease, box-shadow 150ms ease;
    }
    [data-testid="stTextInput"] input:hover,
    [data-testid="stNumberInput"] input:hover,
    [data-testid="stTextArea"] textarea:hover { border-color: var(--color-border-hover) !important; }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--color-border-focus) !important;
        box-shadow: 0 0 0 3px var(--focus-ring) !important;
    }
    ::placeholder { color: var(--color-text-disabled) !important; }

    label { font-size: 0.8rem !important; font-weight: 600 !important; color: var(--color-text-quiet) !important; margin-bottom: 3px !important; }

    [data-baseweb="menu"] [aria-selected="true"] { background-color: var(--color-primary-light) !important; color: var(--color-primary-hover) !important; }
    [data-baseweb="menu"] li:hover { background-color: var(--color-bg) !important; }

    /* ============== EXPANDER ============== */
    [data-testid="stExpander"] {
        border-radius: var(--radius-lg) !important;
        border: 1.5px solid var(--color-border-visible) !important;
        background-color: var(--color-surface);
    }
    [data-testid="stExpander"] summary { font-size: 0.87rem; font-weight: 600; color: var(--color-text-quiet); }

    /* ============== TABELLE ============== */
    .stMarkdown table { border-collapse: collapse; width: 100%; }
    .stMarkdown table thead th {
        background-color: var(--color-primary-light) !important;
        color: var(--color-primary-hover) !important;
        border-bottom: 1.5px solid var(--color-primary-border) !important;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        padding: var(--space-2) var(--space-3) !important;
        text-align: left;
    }
    .stMarkdown table thead th:last-child,
    .stMarkdown table tbody td:last-child { text-align: right; font-variant-numeric: tabular-nums; }
    .stMarkdown table tbody td {
        background-color: transparent;
        border-bottom: 1px solid var(--color-border) !important;
        padding: var(--space-2) var(--space-3) !important;
        font-size: 0.85rem;
        color: var(--color-text);
    }
    .stMarkdown table tbody tr:hover td { background-color: var(--color-primary-light); }

    [data-testid="stDataFrame"] { border-radius: var(--radius-lg); border: 1.5px solid var(--color-primary-border); }

    /* ============== TABS / DIALOG ============== */
    [data-testid="stTabs"] button[role="tab"] { font-size: 0.85rem; font-weight: 600; border-radius: var(--radius-sm) !important; }
    [data-testid="stTabs"] button[aria-selected="true"] { color: var(--color-primary) !important; }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: var(--color-primary) !important; }

    div[role="dialog"] { border-radius: var(--radius-lg) !important; }

    /* ============== SPACING UTILITY ============== */
    .section-spacer { height: var(--space-6); }
    .spacer-sm { height: var(--space-2); }
    .spacer-lg { height: var(--space-10); }

    [data-testid="stCheckbox"], [data-testid="stRadio"] label { min-height: 32px; color: var(--color-text); font-weight: 400 !important; }

    a { color: var(--color-primary) !important; font-weight: 600; transition: color 150ms ease; }
    a:hover { color: var(--color-primary-hover) !important; }

    /* ============== EMPTY STATE ============== */
    .empty-state { text-align: center; padding: var(--space-12) var(--space-6); color: var(--color-text-secondary); }
    .empty-state-icon { font-size: 2rem; margin-bottom: var(--space-3); }
    .empty-state-title { font-size: 1rem; font-weight: 700; color: var(--color-title); margin-bottom: 2px; }
    .empty-state-description { font-size: 0.85rem; color: var(--color-text-secondary); margin-bottom: var(--space-4); max-width: 340px; margin-left: auto; margin-right: auto; }
    </style>
    """, unsafe_allow_html=True)


def badge(testo, tipo="neutral"):
    """Badge pieno a pillola — stile audace/deciso."""
    stili = {
        "success":   ("#FFFFFF", "#12B76A"),
        "warning":   ("#FFFFFF", "#F79009"),
        "danger":    ("#FFFFFF", "#D92D20"),
        "info":      ("#FFFFFF", "#2563EB"),
        "bozza":     ("#4B4F54", "#E4E5E7"),
        "inviato":   ("#FFFFFF", "#2563EB"),
        "accettato": ("#FFFFFF", "#12B76A"),
        "rifiutato": ("#FFFFFF", "#D92D20"),
        "neutral":   ("#4B4F54", "#E4E5E7"),
    }
    colore_testo, colore_bg = stili.get(tipo, stili["neutral"])
    return (
        f"<span style='background-color:{colore_bg}; color:{colore_testo}; "
        f"padding:4px 12px; border-radius:999px; font-size:0.75rem; font-weight:700; "
        f"display:inline-block;'>{testo}</span>"
    )


def stato_badge(stato):
    mappa = {
        "bozza": ("Bozza", "bozza"),
        "inviato": ("Inviato", "inviato"),
        "accettato": ("Accettato", "accettato"),
        "rifiutato": ("Rifiutato", "rifiutato"),
    }
    etichetta, tipo = mappa.get(stato, (stato.capitalize() if stato else "—", "neutral"))
    return badge(etichetta, tipo)


def formatta_numero_tabulare(testo):
    return f"<span class='num-tabular'>{testo}</span>"
