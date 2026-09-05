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
        /* --- Brand: rosso come unico accento, usato con moderazione --- */
        --color-primary: #D92D20;
        --color-primary-hover: #B42318;
        --color-primary-light: #FEF3F2;

        /* --- Neutri: la vera gerarchia vive qui --- */
        --color-bg: #FAFAFA;
        --color-surface: #FFFFFF;

        --color-title: #0C0D0E;
        --color-text: #2D2F31;
        --color-text-quiet: #4B4F54;
        --color-text-secondary: #6B7076;
        --color-text-disabled: #9CA0A6;

        /* --- Bordi: discreti, quasi invisibili --- */
        --color-border: #ECECED;
        --color-border-visible: #E4E5E7;
        --color-border-hover: #D4D6D9;
        --color-border-focus: #D92D20;
        --focus-ring: rgba(217, 45, 32, 0.14);

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

        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 10px;
        --radius-pill: 999px;

        /* --- Nessuna shadow-lift: solo un'ombra minima costante, mai crescente --- */
        --shadow-sm: 0 1px 2px rgba(12, 13, 14, 0.03);
    }

    .stApp { background-color: var(--color-bg); }

    /* ============== TYPOGRAPHY — "quiet", tracking stretto ============== */
    h1, h2, h3 {
        color: var(--color-title) !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    /* Page title: solo leggermente più grande del corpo, non "urlato" */
    h1 { font-size: 1.35rem !important; margin-bottom: 2px !important; line-height: 1.35; font-weight: 650 !important; }
    /* Section title: quiet, colore intermedio non nero pieno */
    h2 {
        font-size: 0.95rem !important;
        margin-top: var(--space-6) !important;
        margin-bottom: var(--space-2) !important;
        color: var(--color-text-quiet) !important;
        font-weight: 600 !important;
    }
    /* Card title */
    h3 { font-size: 0.88rem !important; margin-top: var(--space-3) !important; margin-bottom: var(--space-1) !important; color: var(--color-text) !important; font-weight: 600 !important; }

    p, .stMarkdown, label { color: var(--color-text); font-size: 0.87rem; letter-spacing: -0.005em; }
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--color-text-secondary) !important; font-size: 0.78rem !important; }

    .page-header h1 { margin-bottom: 2px !important; }
    .page-header p {
        color: var(--color-text-secondary);
        font-size: 0.85rem;
        margin-top: 0;
        margin-bottom: var(--space-4);
    }

    /* ============== SIDEBAR — minimale ============== */
    [data-testid="stSidebar"] {
        background-color: var(--color-surface);
        border-right: 1px solid var(--color-border);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: var(--space-4); }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: 0 var(--space-3) var(--space-3) var(--space-3);
        margin-bottom: var(--space-1);
    }
    .sidebar-brand-icon {
        font-size: 1.05rem;
        width: 26px; height: 26px;
        display: flex; align-items: center; justify-content: center;
        background-color: var(--color-primary-light);
        border-radius: var(--radius-sm);
        flex-shrink: 0;
    }
    .sidebar-brand-title { font-weight: 650; font-size: 0.86rem; color: var(--color-title); letter-spacing: -0.01em; }

    .sidebar-divider { border-top: 1px solid var(--color-border); margin: var(--space-2) var(--space-3); }

    .sidebar-section-label {
        font-size: 0.64rem;
        font-weight: 600;
        color: var(--color-text-disabled);
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: var(--space-3) var(--space-3) 2px var(--space-3);
    }

    [data-testid="stSidebar"] [data-testid="stPageLink"] {
        border-radius: var(--radius-sm);
        margin: 0px var(--space-2);
        padding: 1px 2px;
        transition: background-color 120ms ease;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"]:hover { background-color: var(--color-bg); }
    [data-testid="stSidebar"] [data-testid="stPageLink"] p {
        font-size: 0.84rem;
        font-weight: 450;
        color: var(--color-text-quiet);
        letter-spacing: -0.005em;
    }
    [data-testid="stSidebar"] [aria-current="page"] {
        background-color: var(--color-primary-light) !important;
        border-radius: var(--radius-sm);
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
        margin: var(--space-2) 0 0 0;
        border-top: 1px solid var(--color-border);
        font-size: 0.8rem;
        color: var(--color-text-secondary);
    }
    .sidebar-user-avatar {
        width: 24px; height: 24px;
        border-radius: 50%;
        background-color: var(--color-primary-light);
        color: var(--color-primary);
        display: flex; align-items: center; justify-content: center;
        font-weight: 650;
        font-size: 0.68rem;
        flex-shrink: 0;
    }

    /* ============== BOTTONI — 3 livelli, compatti (36px) ============== */
    .stApp button {
        border-radius: var(--radius-md) !important;
        min-height: 36px !important;
        height: 36px;
        font-weight: 500 !important;
        font-size: 0.84rem;
        letter-spacing: -0.005em;
        transition: background-color 120ms ease, border-color 120ms ease, color 120ms ease;
        border: 1px solid var(--color-border-visible);
        background-color: var(--color-surface);
        box-shadow: none !important;
    }
    .stApp button p, .stApp button div, .stApp button span { color: var(--color-text-quiet); }
    .stApp button:hover {
        background-color: var(--color-bg);
        border-color: var(--color-border-hover);
    }
    .stApp button:focus-visible {
        outline: none;
        box-shadow: 0 0 0 3px var(--focus-ring) !important;
    }
    .stApp button:disabled { opacity: 0.45; cursor: not-allowed; }

    /* Primary: pieno, rosso brand */
    .stApp button[kind*="primary"] {
        background-color: var(--color-primary) !important;
        border-color: var(--color-primary) !important;
    }
    .stApp button[kind*="primary"] p,
    .stApp button[kind*="primary"] div,
    .stApp button[kind*="primary"] span { color: #FFFFFF !important; }
    .stApp button[kind*="primary"]:hover {
        background-color: var(--color-primary-hover) !important;
        border-color: var(--color-primary-hover) !important;
    }

    /* Secondary: è il bottone di default sopra — bordo sottile, nessun riempimento */

    /* Ghost: nessun bordo visibile, solo sfondo leggero all'hover — applicata via classe wrapper */
    .btn-ghost button {
        border-color: transparent !important;
        background-color: transparent !important;
    }
    .btn-ghost button:hover { background-color: var(--color-bg) !important; }

    [data-testid="stDownloadButton"] button {
        background-color: var(--color-primary) !important;
        border-color: var(--color-primary) !important;
    }
    [data-testid="stDownloadButton"] button p,
    [data-testid="stDownloadButton"] button div,
    [data-testid="stDownloadButton"] button span { color: #FFFFFF !important; }
    [data-testid="stDownloadButton"] button:hover { background-color: var(--color-primary-hover) !important; }

    .cta-principale button { min-height: 40px !important; height: 40px; font-size: 0.88rem !important; font-weight: 600 !important; }

    /* ============== CARD — bordo quasi invisibile, MAI shadow-lift ============== */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--color-border) !important;
        background-color: var(--color-surface);
        padding: var(--space-1);
        box-shadow: var(--shadow-sm);
        transition: border-color 120ms ease;
    }
    /* Nessun aumento di ombra al passaggio del mouse: solo il bordo si fa leggermente più visibile */
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: var(--color-border-hover) !important;
    }

    /* Righe di lista: azioni rivelate al hover su desktop, sempre visibili su touch */
    .row-actions { opacity: 0.35; transition: opacity 120ms ease; }
    [data-testid="stVerticalBlockBorderWrapper"]:hover .row-actions { opacity: 1; }
    @media (hover: none) {
        .row-actions { opacity: 1; }
    }

    /* ============== METRICHE ============== */
    [data-testid="stMetric"] {
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
    }
    [data-testid="stMetricValue"] {
        color: var(--color-title) !important;
        font-weight: 650 !important;
        font-variant-numeric: tabular-nums;
    }
    [data-testid="stMetricLabel"] { color: var(--color-text-secondary) !important; font-size: 0.76rem !important; }

    /* ============== NUMERI ECONOMICI: allineati a destra, tabulari ============== */
    .num-tabular {
        font-variant-numeric: tabular-nums;
        font-feature-settings: "tnum";
        text-align: right;
        display: inline-block;
    }

    /* ============== INPUT / FORM ============== */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] div[data-baseweb="select"],
    [data-testid="stDateInput"] input {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--color-border-visible) !important;
        background-color: #FFFFFF !important;
        color: var(--color-title) !important;
        min-height: 36px;
        font-size: 0.86rem;
        transition: border-color 120ms ease, box-shadow 120ms ease;
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

    label {
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        color: var(--color-text-quiet) !important;
        margin-bottom: 3px !important;
    }

    /* ============== EXPANDER ============== */
    [data-testid="stExpander"] {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--color-border) !important;
        background-color: var(--color-surface);
    }
    [data-testid="stExpander"] summary { font-size: 0.86rem; font-weight: 450; color: var(--color-text-quiet); }

    /* ============== TABELLE — stile Stripe: dense, numeri a destra ============== */
    .stMarkdown table { border-collapse: collapse; width: 100%; }
    .stMarkdown table thead th {
        background-color: transparent !important;
        color: var(--color-text-secondary) !important;
        border-bottom: 1px solid var(--color-border-visible) !important;
        font-size: 0.72rem;
        font-weight: 600;
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
    [data-testid="stTabs"] button[role="tab"] { font-size: 0.84rem; font-weight: 450; }

    div[role="dialog"] { border-radius: var(--radius-lg) !important; }

    /* ============== SPACING UTILITY ============== */
    .section-spacer { height: var(--space-6); }
    .spacer-sm { height: var(--space-2); }
    .spacer-lg { height: var(--space-10); }

    [data-testid="stCheckbox"], [data-testid="stRadio"] label { min-height: 32px; color: var(--color-text); font-weight: 400 !important; }

    a { color: var(--color-primary) !important; transition: color 120ms ease; }
    a:hover { color: var(--color-primary-hover) !important; }

    /* ============== EMPTY STATE ============== */
    .empty-state { text-align: center; padding: var(--space-12) var(--space-6); color: var(--color-text-secondary); }
    .empty-state-icon { font-size: 1.8rem; margin-bottom: var(--space-3); opacity: 0.4; }
    .empty-state-title { font-size: 0.95rem; font-weight: 600; color: var(--color-text-quiet); margin-bottom: 2px; }
    .empty-state-description { font-size: 0.84rem; color: var(--color-text-secondary); margin-bottom: var(--space-4); max-width: 340px; margin-left: auto; margin-right: auto; }
    </style>
    """, unsafe_allow_html=True)


def badge(testo, tipo="neutral"):
    """Badge minimale in stile Stripe: puntino colorato + testo, niente sfondo pieno."""
    colori_dot = {
        "success":   "#12B76A",
        "warning":   "#F79009",
        "danger":    "#D92D20",
        "info":      "#2563EB",
        "bozza":     "#9CA0A6",
        "inviato":   "#2563EB",
        "accettato": "#12B76A",
        "rifiutato": "#D92D20",
        "neutral":   "#9CA0A6",
    }
    colore = colori_dot.get(tipo, colori_dot["neutral"])
    return (
        f"<span style='display:inline-flex; align-items:center; gap:6px; "
        f"font-size:0.78rem; font-weight:500; color:#4B4F54;'>"
        f"<span style='width:6px; height:6px; border-radius:50%; background-color:{colore}; flex-shrink:0;'></span>"
        f"{testo}</span>"
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


def formatta_numero_tabulare(testo):
    """Avvolge un valore numerico/economico già formattato in una classe con font tabulare, allineato a destra."""
    return f"<span class='num-tabular'>{testo}</span>"
