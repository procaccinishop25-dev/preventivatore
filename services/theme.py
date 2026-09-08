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
        /* --- Brand: rosso riservato alle azioni/CTA reali --- */
        --color-primary: #D92D20;
        --color-primary-hover: #B42318;
        --color-primary-light: #FEF3F2;

        /* --- Accento descrittivo: blu/lavanda, per icone e badge informativi --- */
        --color-accent: #4457C9;
        --color-accent-light: #EEF0FC;
        --color-accent-dark: #363F8C;

        /* --- Sfondo: lavanda molto tenue, superfici bianche --- */
        --color-bg: #F4F5FB;
        --color-surface: #FFFFFF;

        --color-title: #14151A;
        --color-text: #2D2F31;
        --color-text-quiet: #4B4F54;
        --color-text-secondary: #6B7076;
        --color-text-disabled: #9CA0A6;

        --color-border: #ECEDF5;
        --color-border-visible: #E2E4F0;
        --color-border-hover: #CBCEE0;
        --color-border-focus: #D92D20;
        --focus-ring: rgba(217, 45, 32, 0.16);

        --color-success: #12B76A;
        --color-success-light: #ECFDF3;
        --color-warning: #F79009;
        --color-warning-light: #FFFAEB;
        --color-danger: #D92D20;
        --color-danger-light: #FEF3F2;
        --color-info: #4457C9;
        --color-info-light: #EEF0FC;

        --space-1: 4px;
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-6: 24px;
        --space-8: 32px;
        --space-10: 40px;
        --space-12: 48px;

        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 18px;
        --radius-pill: 999px;

        --shadow-sm: 0 1px 3px rgba(68, 87, 201, 0.05);
        --shadow-md: 0 8px 24px rgba(68, 87, 201, 0.08);
    }

    .stApp { background-color: var(--color-bg); }

    /* ============== TYPOGRAPHY ============== */
    h1, h2, h3 {
        color: var(--color-title) !important;
        font-weight: 700 !important;
        letter-spacing: -0.015em;
    }
    h1 { font-size: 1.5rem !important; margin-bottom: 2px !important; line-height: 1.3; }
    h2 { font-size: 1.02rem !important; margin-top: var(--space-6) !important; margin-bottom: var(--space-3) !important; color: var(--color-title) !important; font-weight: 700 !important; }
    h3 { font-size: 0.9rem !important; margin-top: var(--space-3) !important; margin-bottom: var(--space-1) !important; color: var(--color-text) !important; font-weight: 600 !important; }

    p, .stMarkdown, label { color: var(--color-text); font-size: 0.87rem; }
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--color-text-secondary) !important; font-size: 0.78rem !important; }

    .page-header p { color: var(--color-text-secondary); font-size: 0.87rem; margin-top: 0; margin-bottom: var(--space-4); }

    /* ============== SIDEBAR — bianca, pulita, profilo in alto ============== */
    [data-testid="stSidebar"] {
        background-color: var(--color-surface);
        border-right: 1px solid var(--color-border);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: var(--space-4); }

    .sidebar-brand {
        padding: 0 var(--space-4) var(--space-3) var(--space-4);
        font-weight: 800;
        font-size: 1rem;
        color: var(--color-title);
        letter-spacing: -0.02em;
    }

    .sidebar-profile {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        margin: 0 var(--space-3) var(--space-4) var(--space-3);
        padding: var(--space-3);
        background-color: var(--color-bg);
        border-radius: var(--radius-md);
    }
    .sidebar-profile-avatar {
        width: 36px; height: 36px;
        border-radius: 50%;
        background-color: var(--color-accent);
        color: #FFFFFF;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700;
        font-size: 0.82rem;
        flex-shrink: 0;
    }
    .sidebar-profile-name { font-weight: 650; font-size: 0.85rem; color: var(--color-title); line-height: 1.3; }
    .sidebar-profile-role { font-size: 0.73rem; color: var(--color-text-secondary); }

    .sidebar-divider { border-top: 1px solid var(--color-border); margin: var(--space-3) var(--space-3); }

    .sidebar-section-label {
        font-size: 0.65rem;
        font-weight: 700;
        color: var(--color-text-disabled);
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: var(--space-3) var(--space-3) 2px var(--space-4);
    }

    [data-testid="stSidebar"] [data-testid="stPageLink"] {
        border-radius: var(--radius-sm);
        margin: 1px var(--space-2);
        padding: 5px var(--space-2);
        transition: background-color 150ms ease;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"]:hover { background-color: var(--color-bg); }
    [data-testid="stSidebar"] [data-testid="stPageLink"] p {
        font-size: 0.86rem;
        font-weight: 500;
        color: var(--color-text-quiet);
    }
    [data-testid="stSidebar"] [aria-current="page"] {
        background-color: var(--color-accent-light) !important;
        border-radius: var(--radius-sm);
    }
    [data-testid="stSidebar"] [aria-current="page"] p {
        color: var(--color-accent-dark) !important;
        font-weight: 650;
    }

    /* "Nuovo progetto": resta rosso pieno, è la vera CTA del brand */
    .sidebar-cta-primary { margin: var(--space-1) var(--space-2) var(--space-3) var(--space-2); }
    .sidebar-cta-primary [data-testid="stPageLink"] {
        background-color: var(--color-primary) !important;
        border-radius: var(--radius-md) !important;
        margin: 0 !important;
        padding: 8px var(--space-3) !important;
        box-shadow: var(--shadow-sm);
    }
    .sidebar-cta-primary [data-testid="stPageLink"] p { color: #FFFFFF !important; font-weight: 650 !important; }
    .sidebar-cta-primary [data-testid="stPageLink"]:hover { background-color: var(--color-primary-hover) !important; }

    /* ============== BOTTONI ============== */
    button {
        border-radius: var(--radius-md) !important;
        min-height: 38px !important;
        height: 38px;
        font-weight: 600 !important;
        font-size: 0.85rem;
        transition: background-color 150ms ease, border-color 150ms ease, transform 150ms ease, box-shadow 150ms ease;
        border: 1px solid var(--color-border-visible);
        background-color: var(--color-surface);
        box-shadow: none !important;
    }
    button p, button div, button span { color: var(--color-text-quiet); }
    button:hover { background-color: var(--color-bg); border-color: var(--color-border-hover); }
    button:active { transform: scale(0.98); }
    button:focus-visible { outline: none; box-shadow: 0 0 0 3px var(--focus-ring) !important; }
    button:disabled { opacity: 0.45; cursor: not-allowed; }

    button[kind*="primary"] {
        background-color: var(--color-primary) !important;
        border-color: var(--color-primary) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    button[kind*="primary"] p, button[kind*="primary"] div, button[kind*="primary"] span { color: #FFFFFF !important; font-weight: 650 !important; }
    button[kind*="primary"]:hover { background-color: var(--color-primary-hover) !important; border-color: var(--color-primary-hover) !important; }

    .btn-ghost button { border-color: transparent !important; background-color: transparent !important; box-shadow: none !important; }
    .btn-ghost button:hover { background-color: var(--color-bg) !important; }

    [data-testid="stDownloadButton"] button {
        background-color: var(--color-primary) !important;
        border-color: var(--color-primary) !important;
    }
    [data-testid="stDownloadButton"] button p, [data-testid="stDownloadButton"] button div, [data-testid="stDownloadButton"] button span { color: #FFFFFF !important; font-weight: 650 !important; }
    [data-testid="stDownloadButton"] button:hover { background-color: var(--color-primary-hover) !important; }

    .cta-principale button { min-height: 42px !important; height: 42px; font-size: 0.9rem !important; }

    /* ============== CARD — molto arrotondate, ombra soffusa colorata ============== */
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

    .row-actions { opacity: 1; }

    /* ============== METRICHE — card statistica, numero grande ============== */
    [data-testid="stMetric"] {
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        box-shadow: var(--shadow-sm);
    }
    [data-testid="stMetricValue"] {
        color: var(--color-title) !important;
        font-weight: 700 !important;
        font-size: 1.7rem !important;
        font-variant-numeric: tabular-nums;
    }
    [data-testid="stMetricLabel"] { color: var(--color-text-secondary) !important; font-size: 0.78rem !important; font-weight: 500; }

    .num-tabular { font-variant-numeric: tabular-nums; font-feature-settings: "tnum"; text-align: right; display: inline-block; }

    /* ============== INPUT / FORM ============== */
    input, textarea { accent-color: var(--color-primary); }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] div[data-baseweb="select"],
    [data-testid="stDateInput"] input {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--color-border-visible) !important;
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

    [data-baseweb="menu"] [aria-selected="true"] { background-color: var(--color-accent-light) !important; color: var(--color-accent-dark) !important; }
    [data-baseweb="menu"] li:hover { background-color: var(--color-bg) !important; }

    /* ============== EXPANDER ============== */
    [data-testid="stExpander"] {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--color-border) !important;
        background-color: var(--color-surface);
        box-shadow: var(--shadow-sm);
    }
    [data-testid="stExpander"] summary { font-size: 0.86rem; font-weight: 550; color: var(--color-text-quiet); }

    /* ============== TABELLE ============== */
    .stMarkdown table { border-collapse: collapse; width: 100%; }
    .stMarkdown table thead th {
        background-color: transparent !important;
        color: var(--color-text-secondary) !important;
        border-bottom: 1px solid var(--color-border-visible) !important;
        font-size: 0.72rem;
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
        padding: var(--space-3) var(--space-3) !important;
        font-size: 0.85rem;
        color: var(--color-text);
    }
    .stMarkdown table tbody tr:hover td { background-color: var(--color-bg); }

    [data-testid="stDataFrame"] { border-radius: var(--radius-lg); border: 1px solid var(--color-border); }

    /* ============== TABS / DIALOG ============== */
    [data-testid="stTabs"] button[role="tab"] { font-size: 0.85rem; font-weight: 550; }
    [data-testid="stTabs"] button[aria-selected="true"] { color: var(--color-accent) !important; }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: var(--color-accent) !important; }

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
    .empty-state-icon { margin-bottom: var(--space-3); opacity: 0.7; color: var(--color-text-disabled); }
    .empty-state-title { font-size: 1rem; font-weight: 650; color: var(--color-title); margin-bottom: 2px; }
    .empty-state-description { font-size: 0.85rem; color: var(--color-text-secondary); margin-bottom: var(--space-4); max-width: 340px; margin-left: auto; margin-right: auto; }
    </style>
    """, unsafe_allow_html=True)


def badge(testo, tipo="neutral"):
    """Badge a pillola morbida — informativo (blu/lavanda) o semantico (successo/attenzione/errore)."""
    stili = {
        "success":   ("#027A48", "#ECFDF3"),
        "warning":   ("#B54708", "#FFFAEB"),
        "danger":    ("#B42318", "#FEF3F2"),
        "info":      ("#363F8C", "#EEF0FC"),
        "bozza":     ("#4B4F54", "#F2F3F8"),
        "inviato":   ("#363F8C", "#EEF0FC"),
        "accettato": ("#027A48", "#ECFDF3"),
        "rifiutato": ("#B42318", "#FEF3F2"),
        "neutral":   ("#4B4F54", "#F2F3F8"),
    }
    colore_testo, colore_bg = stili.get(tipo, stili["neutral"])
    return (
        f"<span style='background-color:{colore_bg}; color:{colore_testo}; "
        f"padding:3px 11px; border-radius:999px; font-size:0.74rem; font-weight:600; "
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
    """Avvolge un valore numerico/economico già formattato in una classe con font tabulare, allineato a destra."""
    return f"<span class='num-tabular'>{testo}</span>"


def material_icon(nome, dimensione=20):
    """Renderizza un'icona Material Symbols (linea pulita) al posto di un'emoji."""
    return f"<span class='material-icon' style='font-size:{dimensione}px;'>{nome}</span>"
