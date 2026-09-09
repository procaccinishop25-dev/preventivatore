import streamlit as st


def apply_custom_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,400,0,0&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .material-icon {
        font-family: 'Material Symbols Outlined';
        font-weight: normal;
        font-style: normal;
        font-size: 20px;
        line-height: 1;
        vertical-align: middle;
    }

    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    :root {
        --color-primary: #176B52;
        --color-primary-hover: #10513E;
        --color-primary-light: #E4F1EB;

        --color-bg: #F8F9F8;
        --color-surface: #FFFFFF;
        --color-surface-secondary: #F1F3F1;

        --color-title: #17201C;
        --color-text: #17201C;
        --color-text-quiet: #3D453F;
        --color-text-secondary: #69746E;
        --color-text-disabled: #9BA39D;

        --color-border: #ECEFEC;
        --color-border-hover: #D7DED9;
        --color-border-focus: #176B52;
        --focus-ring: rgba(23, 107, 82, 0.16);

        --color-success: #176B52;
        --color-success-light: #E4F1EB;
        --color-warning: #D97745;
        --color-warning-light: #FFF1E8;
        --color-danger: #C94A4A;
        --color-danger-light: #FBEAEA;
        --color-info: #69746E;
        --color-info-light: #F0F2F1;

        --space-1: 4px;
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-5: 20px;
        --space-6: 24px;
        --space-8: 32px;
        --space-10: 40px;
        --space-12: 48px;

        --radius-sm: 8px;
        --radius-md: 9px;
        --radius-lg: 12px;
        --radius-pill: 999px;

        --shadow-sm: 0 1px 2px rgba(23, 32, 28, 0.03), 0 1px 3px rgba(23, 32, 28, 0.04);
    }

    .stApp { background-color: var(--color-bg); }

    /* ============== TYPOGRAPHY ============== */
    h1, h2, h3 {
        color: var(--color-title) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }
    h1 { font-size: 1.6rem !important; margin-bottom: 2px !important; line-height: 1.3; font-weight: 750 !important; }
    h2 { font-size: 1rem !important; margin-top: var(--space-6) !important; margin-bottom: var(--space-2) !important; color: var(--color-title) !important; font-weight: 650 !important; }
    h3 { font-size: 0.92rem !important; margin-top: var(--space-2) !important; margin-bottom: 2px !important; color: var(--color-title) !important; font-weight: 600 !important; }

    p, .stMarkdown, label { color: var(--color-text); font-size: 0.87rem; }
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--color-text-secondary) !important; font-size: 0.78rem !important; }

    .page-header p { color: var(--color-text-secondary); font-size: 0.86rem; margin-top: 0; margin-bottom: var(--space-5); font-weight: 400; }

    .card-title { font-size: 0.95rem; font-weight: 600; color: var(--color-title); margin: 0; }
    .card-description { font-size: 0.8rem; color: var(--color-text-secondary); margin: 2px 0 0 0; }

    .section-header-row {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-top: var(--space-6);
        margin-bottom: var(--space-3);
    }
    .section-header-row h2 { margin: 0 !important; }
    .section-header-action {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--color-primary);
        text-decoration: none;
    }
    .section-header-action:hover { color: var(--color-primary-hover); }

    /* ============== SIDEBAR ============== */
    [data-testid="stSidebar"] {
        background-color: var(--color-surface);
        border-right: 1px solid var(--color-border);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: var(--space-4); }

    .sidebar-brand {
        padding: 0 var(--space-4) var(--space-3) var(--space-4);
        font-weight: 750;
        font-size: 0.98rem;
        color: var(--color-title);
        letter-spacing: -0.01em;
    }

    .sidebar-profile {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        margin: 0 var(--space-3) var(--space-4) var(--space-3);
        padding: var(--space-3);
        background-color: var(--color-surface-secondary);
        border-radius: var(--radius-md);
    }
    .sidebar-profile-avatar {
        width: 34px; height: 34px;
        border-radius: 50%;
        background-color: var(--color-primary);
        color: #FFFFFF;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700;
        font-size: 0.78rem;
        flex-shrink: 0;
    }
    .sidebar-profile-name { font-weight: 650; font-size: 0.84rem; color: var(--color-title); line-height: 1.3; }
    .sidebar-profile-role { font-size: 0.72rem; color: var(--color-text-secondary); }

    .sidebar-divider { border-top: 1px solid var(--color-border); margin: var(--space-3) var(--space-3); }

    .sidebar-section-label {
        font-size: 0.66rem;
        font-weight: 700;
        color: var(--color-text-disabled);
        letter-spacing: 0.07em;
        text-transform: uppercase;
        padding: var(--space-3) var(--space-3) 3px var(--space-4);
    }

    [data-testid="stSidebar"] [data-testid="stPageLink"] {
        border-radius: var(--radius-sm);
        margin: 1px var(--space-2);
        padding: 6px var(--space-2) 6px 10px;
        border-left: 3px solid transparent;
        transition: background-color 150ms ease, border-color 150ms ease;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"]:hover { background-color: var(--color-bg); }
    [data-testid="stSidebar"] [data-testid="stPageLink"] p {
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--color-text-quiet);
    }
    [data-testid="stSidebar"] [aria-current="page"] {
        background-color: var(--color-primary-light) !important;
        border-left: 3px solid var(--color-primary) !important;
        border-radius: var(--radius-sm);
    }
    [data-testid="stSidebar"] [aria-current="page"] p {
        color: var(--color-primary-hover) !important;
        font-weight: 650;
    }

    /* ============== BOTTONI ============== */
    button {
        border-radius: var(--radius-md) !important;
        min-height: 38px !important;
        height: 38px;
        font-weight: 550 !important;
        font-size: 0.85rem;
        transition: background-color 150ms ease, border-color 150ms ease, color 150ms ease, box-shadow 150ms ease;
        border: 1px solid var(--color-border);
        background-color: var(--color-surface);
        box-shadow: none !important;
    }
    button p, button div, button span { color: var(--color-text-quiet); }
    button:hover { background-color: var(--color-surface-secondary); border-color: var(--color-border-hover); }
    button:focus-visible { outline: none; box-shadow: 0 0 0 3px var(--focus-ring) !important; }
    button:disabled { opacity: 0.45; cursor: not-allowed; }

    button[kind*="primary"] {
        background-color: var(--color-primary) !important;
        border-color: var(--color-primary) !important;
    }
    button[kind*="primary"] p, button[kind*="primary"] div, button[kind*="primary"] span { color: #FFFFFF !important; font-weight: 600 !important; }
    button[kind*="primary"]:hover { background-color: var(--color-primary-hover) !important; border-color: var(--color-primary-hover) !important; }

    .btn-ghost button { border-color: transparent !important; background-color: transparent !important; }
    .btn-ghost button:hover { background-color: var(--color-surface-secondary) !important; }

    [data-testid="stDownloadButton"] button {
        background-color: var(--color-primary) !important;
        border-color: var(--color-primary) !important;
    }
    [data-testid="stDownloadButton"] button p, [data-testid="stDownloadButton"] button div, [data-testid="stDownloadButton"] button span { color: #FFFFFF !important; font-weight: 600 !important; }
    [data-testid="stDownloadButton"] button:hover { background-color: var(--color-primary-hover) !important; }

    /* ============== CARD ============== */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--color-border) !important;
        background-color: var(--color-surface);
        padding: var(--space-1);
        box-shadow: var(--shadow-sm) !important;
        transition: box-shadow 180ms ease, border-color 180ms ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: var(--color-border-hover) !important;
    }

    .row-actions { opacity: 1; }
    .card-divider { border-top: 1px solid var(--color-border); margin: var(--space-3) 0; }

    /* --- Responsive: le righe di colonne vanno a capo invece di schiacciarsi
       su schermi stretti, invece di assumere che Streamlit lo faccia da solo --- */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap;
        row-gap: var(--space-2);
    }
    [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        min-width: 0;
    }

        /* --- Azione distruttiva: st.markdown non annida davvero i bottoni nel DOM,
       quindi usiamo st.container(key=...) che genera un vero div padre. --- */
    [class*="st-key-dangerwrap"] button {
        border-color: transparent !important;
        background-color: transparent !important;
    }
    [class*="st-key-dangerwrap"] button p,
    [class*="st-key-dangerwrap"] button div,
    [class*="st-key-dangerwrap"] button span {
        color: var(--color-danger) !important;
    }
    [class*="st-key-dangerwrap"] button:hover {
        background-color: var(--color-danger-light) !important;
    }

    /* ============== METRICHE ============== */
    [data-testid="stMetric"] {
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: var(--space-4) var(--space-5);
        box-shadow: var(--shadow-sm);
    }
    [data-testid="stMetricValue"] {
        color: var(--color-title) !important;
        font-weight: 700 !important;
        font-size: 1.85rem !important;
        font-variant-numeric: tabular-nums;
    }
    [data-testid="stMetricLabel"] {
        color: var(--color-text-secondary) !important;
        font-size: 0.72rem !important;
        font-weight: 650 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .num-tabular { font-variant-numeric: tabular-nums; font-feature-settings: "tnum"; text-align: right; display: inline-block; }

    /* ============== INPUT / FORM ============== */
    input, textarea { accent-color: var(--color-primary); }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] div[data-baseweb="select"],
    [data-testid="stDateInput"] input {
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--color-border) !important;
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

    label { font-size: 0.8rem !important; font-weight: 550 !important; color: var(--color-text-quiet) !important; margin-bottom: 3px !important; }

    [data-baseweb="menu"] [aria-selected="true"] { background-color: var(--color-primary-light) !important; color: var(--color-primary-hover) !important; }
    [data-baseweb="menu"] li:hover { background-color: var(--color-bg) !important; }

    /* ============== EXPANDER ============== */
    [data-testid="stExpander"] {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--color-border) !important;
        background-color: var(--color-surface);
        box-shadow: var(--shadow-sm);
    }
    [data-testid="stExpander"] summary { font-size: 0.85rem; font-weight: 550; color: var(--color-text-quiet); }

    /* ============== POPOVER (menu overflow "⋯") ============== */
    [data-testid="stPopoverBody"] {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--color-border) !important;
        box-shadow: var(--shadow-sm);
        padding: var(--space-2) !important;
    }

    /* ============== TABELLE ============== */
    .stMarkdown table { border-collapse: collapse; width: 100%; }
    .stMarkdown table thead th {
        background-color: transparent !important;
        color: var(--color-text-secondary) !important;
        border-bottom: 1px solid var(--color-border) !important;
        font-size: 0.7rem;
        font-weight: 650;
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
        font-size: 0.84rem;
        color: var(--color-text);
    }
    .stMarkdown table tbody tr:hover td { background-color: var(--color-bg); }

    [data-testid="stDataFrame"] { border-radius: var(--radius-lg); border: 1px solid var(--color-border); }

    /* ============== TABS / DIALOG ============== */
    [data-testid="stTabs"] button[role="tab"] { font-size: 0.84rem; font-weight: 550; }
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
    .empty-state { text-align: center; padding: var(--space-10) var(--space-6); color: var(--color-text-secondary); }
    .empty-state-icon { margin-bottom: var(--space-3); opacity: 0.55; color: var(--color-text-disabled); }
    .empty-state-title { font-size: 0.95rem; font-weight: 650; color: var(--color-title); margin-bottom: 2px; }
    .empty-state-description { font-size: 0.83rem; color: var(--color-text-secondary); margin-bottom: var(--space-4); max-width: 320px; margin-left: auto; margin-right: auto; }
    </style>
    """, unsafe_allow_html=True)


def badge(testo, tipo="neutral"):
    stili = {
        "success":   ("#176B52", "#E4F1EB"),
        "warning":   ("#B85E2D", "#FFF1E8"),
        "danger":    ("#B33A3A", "#FBEAEA"),
        "info":      ("#69746E", "#F0F2F1"),
        "bozza":     ("#69746E", "#F0F2F1"),
        "inviato":   ("#B85E2D", "#FFF1E8"),
        "accettato": ("#176B52", "#E4F1EB"),
        "rifiutato": ("#B33A3A", "#FBEAEA"),
        "neutral":   ("#69746E", "#F0F2F1"),
    }
    colore_testo, colore_bg = stili.get(tipo, stili["neutral"])
    return (
        f"<span style='background-color:{colore_bg}; color:{colore_testo}; "
        f"padding:3px 10px; border-radius:999px; font-size:0.72rem; font-weight:600; "
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


def material_icon(nome, dimensione=20):
    return f"<span class='material-icon' style='font-size:{dimensione}px;'>{nome}</span>"


def card_header(titolo, descrizione=None):
    html = f"<div class='card-title'>{titolo}</div>"
    if descrizione:
        html += f"<div class='card-description'>{descrizione}</div>"
    return html


def card_divider():
    return "<div class='card-divider'></div>"


def section_header_row(titolo, testo_azione=None):
    return f"<div class='section-header-row'><h2>{titolo}</h2>"
