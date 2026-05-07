def load_global_styles():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=DM+Sans:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-main: #F6F9FF;
    --bg-soft: #EEF4FF;
    --bg-card: #FFFFFF;
    --bg-sidebar: #0E1B36;
    --bg-sidebar-2: #13264A;

    --blue: #2F7CFF;
    --blue-soft: #EAF2FF;
    --green: #31B889;
    --green-soft: #E9FBF5;
    --purple: #7A5CFF;
    --gold: #D99A18;
    --red: #D44D61;

    --text-main: #10233F;
    --text-secondary: #53657F;
    --text-muted: #7A8AA3;

    --border: #DCE7F8;
    --shadow: 0 10px 35px rgba(22, 46, 90, 0.07);
    --radius: 22px;
}

* {
    box-sizing: border-box;
}

.stApp {
    background: linear-gradient(180deg, var(--bg-main) 0%, var(--bg-soft) 100%) !important;
    color: var(--text-main) !important;
    font-family: 'DM Sans', sans-serif !important;
}

.main .block-container {
    padding: 2rem 2.2rem !important;
    max-width: 1380px !important;
}

/* On cache seulement le menu et le footer.
   NE PAS cacher header, sinon le bouton natif de sidebar peut disparaître. */
#MainMenu,
footer {
    visibility: hidden !important;
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton {
    display: none !important;
}

/* ============================================================
   SIDEBAR — VERSION FIABLE
   La sidebar reste visible sur toutes les pages.
   Le bouton de fermeture reste affiché.
   ============================================================ */

[data-testid="stSidebarNav"] {
    display: none !important;
}

section[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    transform: translateX(0px) !important;
    min-width: 290px !important;
    width: 290px !important;
    background: linear-gradient(180deg, var(--bg-sidebar) 0%, var(--bg-sidebar-2) 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
    z-index: 9999 !important;
}

section[data-testid="stSidebar"] > div {
    display: block !important;
    visibility: visible !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-sidebar) 0%, var(--bg-sidebar-2) 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}

[data-testid="stSidebar"] * {
    color: #F5F8FF !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.4rem 1rem !important;
}

/* Bouton de fermeture de la sidebar */
button[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}

/* Bouton de réouverture si Streamlit le crée malgré tout */
[data-testid="collapsedControl"],
button[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
button[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    position: fixed !important;
    top: 92px !important;
    left: 14px !important;
    z-index: 999999 !important;
    width: 46px !important;
    height: 46px !important;
    border-radius: 15px !important;
    background: linear-gradient(135deg, #2F7CFF, #6C63FF) !important;
    border: 1px solid rgba(255,255,255,0.30) !important;
    box-shadow: 0 12px 28px rgba(47,124,255,0.30) !important;
}

[data-testid="collapsedControl"] svg,
button[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
button[data-testid="stSidebarCollapsedControl"] svg {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
    width: 22px !important;
    height: 22px !important;
}

[data-testid="stAppViewContainer"] {
    overflow-x: hidden !important;
}

/* SIDEBAR BRAND */
.sidebar-brand-wrap {
    padding: 1rem 0 1.1rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 1rem;
}

.sidebar-logo-name {
    font-family: 'Sora', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    color: #FFFFFF;
}

.sidebar-logo-sub {
    font-size: 0.82rem;
    color: #C6D7F2 !important;
    margin-top: 0.1rem;
}

.fp-logo-box {
    width: 38px;
    height: 38px;
    border-radius: 11px;
    background: linear-gradient(135deg, #2F7CFF, #31E6A8);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 800;
    font-size: 0.78rem;
    font-family: 'Sora', sans-serif;
}

/* BUTTONS */
.stButton > button {
    height: 52px !important;
    border-radius: 14px !important;
    font-size: 0.98rem !important;
    font-weight: 800 !important;
    border: none !important;
    box-shadow: 0 6px 18px rgba(47,124,255,0.18) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2F7CFF, #7A5CFF) !important;
    color: #FFFFFF !important;
}

.stButton > button[kind="secondary"] {
    background: #EAF2FF !important;
    color: #204A7A !important;
}

/* SIDEBAR BUTTONS */
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #2F7CFF, #7A5CFF) !important;
    color: white !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.08) !important;
    color: #F5F8FF !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

/* GLOBAL TYPOGRAPHY */
.fp-page-label {
    color: var(--blue);
    font-size: 0.88rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
    font-family: 'Sora', sans-serif;
}

.fp-page-title {
    color: var(--text-main);
    font-size: 2.35rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 0.7rem;
    font-family: 'Sora', sans-serif;
}

.fp-page-subtitle {
    color: var(--text-secondary);
    font-size: 1.04rem;
    line-height: 1.8;
    margin-bottom: 1.6rem;
}

/* CARDS */
.fp-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.45rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}

.fp-card-title {
    color: var(--text-main);
    font-size: 1.22rem;
    font-weight: 800;
    line-height: 1.4;
    font-family: 'Sora', sans-serif;
}

.fp-card-sub {
    color: var(--text-secondary);
    font-size: 0.96rem;
    line-height: 1.75;
    margin-top: 0.45rem;
}

.fp-small-label {
    color: #5B6F8E;
    font-size: 0.82rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.65rem;
    font-family: 'Sora', sans-serif;
}

.fp-kpi-card {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 1.35rem 1.35rem;
    box-shadow: var(--shadow);
}

.fp-kpi-title {
    color: #6B7F99;
    font-size: 0.82rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.55rem;
}

.fp-kpi-value {
    color: var(--text-main);
    font-size: 1.75rem;
    font-weight: 800;
    font-family: 'Sora', sans-serif;
    line-height: 1.15;
}

.fp-kpi-sub {
    color: var(--text-secondary);
    font-size: 0.92rem;
    margin-top: 0.45rem;
}

.fp-positive {
    color: var(--green) !important;
}

.fp-negative {
    color: var(--red) !important;
}

.fp-neutral {
    color: var(--blue) !important;
}

/* TABLE LIKE CARDS */
.fp-table {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 22px;
    box-shadow: var(--shadow);
    overflow: hidden;
    margin-bottom: 1rem;
}

.fp-table-title {
    color: var(--text-main);
    font-size: 1.18rem;
    font-weight: 800;
    padding: 1.15rem 1.35rem;
    border-bottom: 1px solid var(--border);
    font-family: 'Sora', sans-serif;
}

.fp-row {
    display: grid;
    align-items: center;
    padding: 0.95rem 1.35rem;
    border-bottom: 1px solid var(--border);
    gap: 0.8rem;
}

.fp-row:last-child {
    border-bottom: none;
}

.fp-row-header {
    background: #F4F8FF;
    color: #617693;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.fp-main-text {
    color: var(--text-main);
    font-size: 0.98rem;
    font-weight: 800;
    line-height: 1.35;
}

.fp-sub-text {
    color: var(--text-secondary);
    font-size: 0.88rem;
    margin-top: 0.2rem;
    line-height: 1.5;
}

.fp-pill {
    display: inline-block;
    padding: 0.38rem 0.75rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 800;
}

.fp-pill-blue {
    background: #E8F1FF;
    color: #2F7CFF;
    border: 1px solid #CFE0FF;
}

.fp-pill-green {
    background: #E9FBF5;
    color: #1C9C73;
    border: 1px solid #C5F3E1;
}

.fp-pill-red {
    background: #FFECEE;
    color: #D44D61;
    border: 1px solid #F7CBD3;
}

.fp-pill-gold {
    background: #FFF7E6;
    color: #A56A00;
    border: 1px solid #F6DEAA;
}

/* FORMS */
.stTextInput > div > div,
.stNumberInput > div > div,
.stSelectbox > div > div {
    background: #FFFFFF !important;
    border: 1px solid #DCE7F8 !important;
    border-radius: 14px !important;
    min-height: 50px !important;
}

.stTextInput label,
.stNumberInput label,
.stSelectbox label {
    color: #10233F !important;
    font-size: 0.95rem !important;
    font-weight: 800 !important;
}

/* DATAFRAMES */
[data-testid="stDataFrame"] {
    background: #FFFFFF !important;
    border-radius: 18px !important;
    border: 1px solid #DCE7F8 !important;
    overflow: hidden !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.4rem;
    background: transparent;
    flex-wrap: wrap;
}

.stTabs [data-baseweb="tab"] {
    background: #FFFFFF;
    border: 1px solid #DCE7F8;
    border-radius: 14px;
    padding: 0.65rem 1rem;
    color: #415875;
    font-weight: 800;
}

.stTabs [aria-selected="true"] {
    background: #EAF2FF !important;
    color: #2F7CFF !important;
    border-color: #CFE0FF !important;
}

[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border-radius: 22px;
}

/* SCROLLBAR */
::-webkit-scrollbar {
    width: 7px;
    height: 7px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: #C8D7ED;
    border-radius: 99px;
}

::-webkit-scrollbar-thumb:hover {
    background: #9FB5D4;
}
</style>
"""
