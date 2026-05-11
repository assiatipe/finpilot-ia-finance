def load_global_styles():
    return """
<style>
/* ═══════════════════════════════════════════════════════════════
   FINPILOT — PREMIUM DESIGN SYSTEM v2
   Direction : Luxury Fintech — sombre, sobre, élégant
   Inspiré de : Stripe, Linear, Vercel, Bloomberg Terminal
   ═══════════════════════════════════════════════════════════════ */

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Bricolage+Grotesque:wght@400;500;600;700;800&display=swap');

/* ─── TOKENS ─────────────────────────────────────────────────── */
:root {
    /* Fond */
    --bg:          #F9FAFB;
    --bg-2:        #F3F4F8;
    --bg-card:     #FFFFFF;
    --bg-hover:    #F7F9FF;

    /* Sidebar */
    --sidebar-bg:  #0A0F1E;
    --sidebar-2:   #0F172A;
    --sidebar-line: rgba(255,255,255,0.06);

    /* Couleur unique d'accent */
    --accent:      #1A56DB;
    --accent-soft: #EEF4FF;
    --accent-glow: rgba(26,86,219,0.15);

    /* Sémantique */
    --success:     #059669;
    --success-soft:#D1FAE5;
    --danger:      #DC2626;
    --danger-soft: #FEE2E2;
    --warning:     #D97706;
    --warning-soft:#FEF3C7;

    /* Texte */
    --text-1:  #0A0F1E;
    --text-2:  #374151;
    --text-3:  #6B7280;
    --text-4:  #9CA3AF;

    /* Bordures */
    --border:      #E5E7EB;
    --border-soft: #F3F4F6;

    /* Ombres */
    --shadow-xs: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04);
    --shadow-lg: 0 10px 15px rgba(0,0,0,0.07), 0 4px 6px rgba(0,0,0,0.04);
    --shadow-xl: 0 20px 25px rgba(0,0,0,0.08), 0 8px 10px rgba(0,0,0,0.04);

    /* Rayons */
    --r-sm:  8px;
    --r-md:  12px;
    --r-lg:  16px;
    --r-xl:  20px;
    --r-2xl: 24px;

    /* Typo */
    --font-display: 'Bricolage Grotesque', sans-serif;
    --font-body:    'Plus Jakarta Sans', sans-serif;
}

/* ─── RESET BASE ─────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

/* ─── APP SHELL ──────────────────────────────────────────────── */
.stApp {
    background: var(--bg) !important;
    color: var(--text-1) !important;
    font-family: var(--font-body) !important;
    font-size: 15px !important;
    -webkit-font-smoothing: antialiased !important;
}

.main .block-container {
    padding: 2rem 2.5rem !important;
    max-width: 1440px !important;
}

/* Cacher éléments Streamlit */
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton {
    display: none !important;
    visibility: hidden !important;
}

[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stAppViewContainer"] { overflow-x: hidden !important; }

/* ─── SIDEBAR ────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    transform: translateX(0) !important;
    min-width: 260px !important;
    width: 260px !important;
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--sidebar-line) !important;
    z-index: 9999 !important;
}

section[data-testid="stSidebar"] > div {
    display: block !important;
    visibility: visible !important;
}

[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--sidebar-line) !important;
}

[data-testid="stSidebar"] * { color: #E2E8F0 !important; }

[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1rem !important;
}

/* Bouton fermeture sidebar */
button[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}

[data-testid="collapsedControl"],
button[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
button[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    position: fixed !important;
    top: 80px !important;
    left: 12px !important;
    z-index: 999999 !important;
    width: 40px !important;
    height: 40px !important;
    border-radius: var(--r-md) !important;
    background: var(--accent) !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(26,86,219,0.35) !important;
}

[data-testid="collapsedControl"] svg,
button[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
button[data-testid="stSidebarCollapsedControl"] svg {
    color: #fff !important;
    fill: #fff !important;
    stroke: #fff !important;
    width: 18px !important;
    height: 18px !important;
}

/* Sidebar brand */
.sidebar-brand-wrap {
    padding: 0.5rem 0 1.2rem 0;
    border-bottom: 1px solid var(--sidebar-line);
    margin-bottom: 1.2rem;
}

.sidebar-logo-name {
    font-family: var(--font-display) !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    letter-spacing: -0.03em;
}

.sidebar-logo-sub {
    font-size: 0.78rem !important;
    color: #64748B !important;
    margin-top: 0.15rem;
    font-weight: 500;
}

.fp-logo-box, .fp-logo-symbol {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 800;
    font-size: 0.8rem;
    font-family: var(--font-display);
    box-shadow: 0 4px 12px rgba(26,86,219,0.4);
}

/* Sidebar nav buttons */
[data-testid="stSidebar"] .stButton > button {
    height: 44px !important;
    border-radius: var(--r-md) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border: none !important;
    background: transparent !important;
    color: #94A3B8 !important;
    justify-content: flex-start !important;
    padding-left: 0.9rem !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
    letter-spacing: 0;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.06) !important;
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: rgba(26,86,219,0.18) !important;
    color: #93BBFF !important;
    border: 1px solid rgba(26,86,219,0.30) !important;
}

/* ─── BOUTONS PRINCIPAUX ─────────────────────────────────────── */
.stButton > button {
    height: 44px !important;
    border-radius: var(--r-md) !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    letter-spacing: 0 !important;
    transition: all 0.15s ease !important;
    border: none !important;
}

.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    color: #FFFFFF !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1), 0 4px 12px rgba(26,86,219,0.25) !important;
}

.stButton > button[kind="primary"]:hover {
    background: #1648C4 !important;
    box-shadow: 0 4px 16px rgba(26,86,219,0.35) !important;
    transform: translateY(-1px) !important;
}

.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: var(--text-2) !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: var(--bg-hover) !important;
    border-color: #D1D5DB !important;
}

/* ─── TYPOGRAPHIE ────────────────────────────────────────────── */
.page-title, .fp-page-title, .adm-hero-title, .fb-hero-title {
    font-family: var(--font-display) !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    color: var(--text-1) !important;
    letter-spacing: -0.04em !important;
    line-height: 1.15 !important;
    margin-bottom: 0.6rem !important;
}

.page-subtitle, .fp-page-subtitle {
    color: var(--text-3) !important;
    font-size: 0.97rem !important;
    line-height: 1.7 !important;
    font-weight: 400 !important;
}

.section-label, .fp-page-label, .adm-hero-label, .fb-hero-label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--accent) !important;
    margin-bottom: 0.5rem !important;
}

/* ─── CARDS ──────────────────────────────────────────────────── */
.fp-card, .adm-card, .fb-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-xl) !important;
    padding: 1.5rem 1.6rem !important;
    box-shadow: var(--shadow-sm) !important;
    margin-bottom: 1rem !important;
    transition: box-shadow 0.2s ease !important;
}

.fp-card:hover, .adm-card:hover {
    box-shadow: var(--shadow-md) !important;
}

.fp-card-title, .adm-card-title, .fb-card-title {
    font-family: var(--font-display) !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    color: var(--text-1) !important;
    margin-bottom: 0.3rem !important;
    letter-spacing: -0.02em;
}

.fp-card-sub, .adm-card-sub, .fb-card-sub {
    color: var(--text-3) !important;
    font-size: 0.88rem !important;
    line-height: 1.6 !important;
    margin-bottom: 1rem !important;
    font-weight: 400 !important;
}

/* ─── KPI CARDS ──────────────────────────────────────────────── */
.kpi-card, .fp-kpi-card, .adm-kpi, .stat-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-xl) !important;
    padding: 1.4rem 1.5rem !important;
    box-shadow: var(--shadow-sm) !important;
    transition: box-shadow 0.2s ease, transform 0.2s ease !important;
}

.kpi-card:hover, .adm-kpi:hover, .stat-card:hover {
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) !important;
}

.kpi-title, .fp-kpi-title, .adm-kpi-label, .stat-label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: var(--text-4) !important;
    margin-bottom: 0.6rem !important;
}

.kpi-value, .fp-kpi-value, .adm-kpi-value, .stat-value {
    font-family: var(--font-display) !important;
    font-size: 1.9rem !important;
    font-weight: 800 !important;
    color: var(--text-1) !important;
    line-height: 1.1 !important;
    letter-spacing: -0.03em !important;
}

.kpi-sub, .fp-kpi-sub {
    color: var(--text-4) !important;
    font-size: 0.8rem !important;
    margin-top: 0.4rem !important;
}

/* Accent sur valeur importante */
.adm-kpi-accent { color: var(--accent) !important; }
.fp-positive     { color: var(--success) !important; }
.fp-negative     { color: var(--danger)  !important; }
.fp-neutral      { color: var(--accent)  !important; }

/* ─── HERO BANNERS ───────────────────────────────────────────── */
/* Hero sombre premium — remplace les dégradés criards */
.glass-card,
[class*="hero"],
[class*="-hero"] {
    border-radius: var(--r-2xl) !important;
}

/* Hero unifié sombre */
.fp-hero-dark {
    background: var(--text-1) !important;
    border-radius: var(--r-2xl) !important;
    padding: 2.2rem 2.5rem !important;
    position: relative !important;
    overflow: hidden !important;
    margin-bottom: 1.5rem !important;
}

.fp-hero-dark::before {
    content: "";
    position: absolute;
    top: -80px; right: -80px;
    width: 320px; height: 320px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(26,86,219,0.25), transparent 70%);
    pointer-events: none;
}

/* ─── GLASS CARD (dashboard) ─────────────────────────────────── */
.glass-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow-md) !important;
    border-radius: var(--r-2xl) !important;
}

/* ─── PILLS / BADGES ─────────────────────────────────────────── */
.fp-pill, .pill {
    display: inline-flex !important;
    align-items: center !important;
    padding: 0.28rem 0.65rem !important;
    border-radius: 6px !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
}

.fp-pill-blue, .pill-blue   { background: #EEF4FF !important; color: var(--accent) !important; border: 1px solid #DBEAFE !important; }
.fp-pill-green, .pill-green { background: var(--success-soft) !important; color: var(--success) !important; border: 1px solid #A7F3D0 !important; }
.fp-pill-red, .pill-red     { background: var(--danger-soft) !important; color: var(--danger) !important; border: 1px solid #FECACA !important; }
.fp-pill-gold, .pill-gold   { background: var(--warning-soft) !important; color: var(--warning) !important; border: 1px solid #FDE68A !important; }
.pill-purple                { background: #F5F3FF !important; color: #7C3AED !important; border: 1px solid #DDD6FE !important; }

/* ─── TABLEAUX ───────────────────────────────────────────────── */
.fp-table {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-xl) !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: hidden !important;
    margin-bottom: 1rem !important;
}

.fp-table-title {
    font-family: var(--font-display) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: var(--text-1) !important;
    padding: 1.1rem 1.4rem !important;
    border-bottom: 1px solid var(--border-soft) !important;
}

.fp-row {
    display: grid !important;
    align-items: center !important;
    padding: 0.85rem 1.4rem !important;
    border-bottom: 1px solid var(--border-soft) !important;
    gap: 0.8rem !important;
    transition: background 0.12s ease !important;
}

.fp-row:hover { background: var(--bg-hover) !important; }
.fp-row:last-child { border-bottom: none !important; }

.fp-row-header {
    background: var(--bg-2) !important;
    color: var(--text-4) !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

.fp-main-text {
    color: var(--text-1) !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
}

.fp-sub-text {
    color: var(--text-3) !important;
    font-size: 0.82rem !important;
    margin-top: 0.15rem !important;
}

/* ─── INPUTS & FORMS ─────────────────────────────────────────── */
.stTextInput > div > div,
.stNumberInput > div > div,
.stSelectbox > div > div,
.stTextArea > div > div {
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    min-height: 44px !important;
    font-family: var(--font-body) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

.stTextInput > div > div:focus-within,
.stNumberInput > div > div:focus-within,
.stSelectbox > div > div:focus-within,
.stTextArea > div > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(26,86,219,0.1) !important;
}

.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stTextArea label {
    color: var(--text-2) !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    font-family: var(--font-body) !important;
}

/* ─── TABS ───────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.25rem !important;
    background: var(--bg-2) !important;
    padding: 0.3rem !important;
    border-radius: var(--r-md) !important;
    border: 1px solid var(--border) !important;
    width: fit-content !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: var(--r-sm) !important;
    padding: 0.5rem 1rem !important;
    color: var(--text-3) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.15s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-1) !important;
    background: rgba(255,255,255,0.6) !important;
}

.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: var(--text-1) !important;
    box-shadow: var(--shadow-sm) !important;
    font-weight: 700 !important;
}

/* Indicateur de tab actif — supprimer la ligne rouge Streamlit */
.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

/* ─── DATAFRAMES ─────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    background: #FFFFFF !important;
    border-radius: var(--r-lg) !important;
    border: 1px solid var(--border) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ─── GRAPHIQUES PLOTLY ──────────────────────────────────────── */
[data-testid="stPlotlyChart"] {
    background: #FFFFFF !important;
    border-radius: var(--r-xl) !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: hidden !important;
}

/* ─── SELECT SLIDER ──────────────────────────────────────────── */
[data-testid="stSlider"] > div > div > div {
    background: var(--accent) !important;
}

/* ─── EXPANDER ───────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
    box-shadow: none !important;
    background: #FFFFFF !important;
}

[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: var(--text-1) !important;
    font-size: 0.92rem !important;
}

/* ─── SUCCESS / ERROR / WARNING ALERTS ───────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--r-md) !important;
    border-left-width: 3px !important;
    font-size: 0.88rem !important;
}

/* ─── SIDEBAR WIDGETS (visuals) ─────────────────────────────── */
.sidebar-visual-card {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--r-xl) !important;
}

.sidebar-cash {
    margin-top: 0.8rem;
    padding: 0.65rem 0.85rem;
    background: rgba(26,86,219,0.15);
    border: 1px solid rgba(26,86,219,0.25);
    border-radius: var(--r-md);
}

.sidebar-cash-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748B !important;
    display: block;
}

.sidebar-cash-value {
    font-family: var(--font-display);
    font-size: 1.05rem;
    font-weight: 800;
    color: #93BBFF !important;
    display: block;
    margin-top: 0.15rem;
}

/* ─── ALLOC BARS ─────────────────────────────────────────────── */
.alloc-bar-wrap {
    width: 100%;
    height: 4px;
    background: var(--bg-2);
    border-radius: 99px;
    margin-top: 0.4rem;
    overflow: hidden;
}

.alloc-bar {
    height: 100%;
    background: var(--accent);
    border-radius: 99px;
    transition: width 0.5s ease;
}

/* ─── ANIMATIONS ─────────────────────────────────────────────── */
@keyframes fp-fade-up {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

.fp-fade-in {
    animation: fp-fade-up 0.4s ease both;
}

/* Stagger */
.fp-fade-in:nth-child(1) { animation-delay: 0.05s; }
.fp-fade-in:nth-child(2) { animation-delay: 0.10s; }
.fp-fade-in:nth-child(3) { animation-delay: 0.15s; }
.fp-fade-in:nth-child(4) { animation-delay: 0.20s; }

/* ─── SCROLLBAR ──────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #9CA3AF; }

/* ─── SIDEBAR USER BOX ───────────────────────────────────────── */
.sidebar-user {
    padding: 0.9rem;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: var(--r-lg);
    background: rgba(255,255,255,0.04);
    margin-top: 0.5rem;
}

.sidebar-user-name {
    font-weight: 700;
    font-size: 0.9rem;
    color: #E2E8F0 !important;
}

.sidebar-user-email {
    font-size: 0.76rem;
    color: #64748B !important;
    margin-top: 0.1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ─── DIVERS ─────────────────────────────────────────────────── */
.side-widget {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: var(--r-xl);
    padding: 1.3rem 1.4rem;
    box-shadow: var(--shadow-sm);
}

.side-widget-title {
    font-family: var(--font-display);
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-1);
    margin-bottom: 1rem;
}

.widget-list-item {
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--border-soft);
}

.widget-list-item:last-child { border-bottom: none; }

.widget-list-title {
    font-weight: 700;
    font-size: 0.9rem;
    color: var(--text-1);
}

/* Feedback rows */
.review-card {
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
}

/* Admin user rows */
.user-row { transition: background 0.12s ease; }
.user-row:hover { background: var(--bg-hover) !important; }

/* Order chips */
.order-buy  { background: var(--success-soft) !important; color: var(--success) !important; }
.order-sell { background: var(--danger-soft)  !important; color: var(--danger)  !important; }

/* Chip générique sidebar */
.sidebar-chip {
    padding: 0.35rem 0.65rem;
    border-radius: 6px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.07);
    color: #94A3B8 !important;
    font-size: 0.76rem;
    font-weight: 600;
}

/* Note sidebar */
.sidebar-note {
    color: #334155 !important;
    font-size: 0.75rem;
    line-height: 1.55;
    margin-top: 1rem;
}

/* Stat dist bar */
.dist-bar-fill {
    background: var(--accent) !important;
}

</style>
"""
