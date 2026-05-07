import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import hashlib
import os
import base64
import secrets
import urllib.parse
import requests
from datetime import datetime


DB_PATH = "finpilot.db"

# ============================================================
# GOOGLE OAUTH — VRAIE CONNEXION GOOGLE
# ============================================================
# 1) Crée un projet Google Cloud.
# 2) Crée un identifiant OAuth 2.0 de type "Application Web".
# 3) Ajoute exactement cette URL dans "Authorized redirect URIs" :
#       http://localhost:8502
# 4) Mets ton client_id et ton client_secret dans .streamlit/secrets.toml :
#
# [google_oauth]
# client_id = "TON_CLIENT_ID"
# client_secret = "TON_CLIENT_SECRET"
#
# Le bouton Google ouvrira le choix du compte, puis Google reviendra
# automatiquement vers http://localhost:8502?code=...
# Ensuite l'app valide le compte et connecte l'utilisateur.

GOOGLE_REDIRECT_URI = "http://localhost:8502"
GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"


def get_google_client_id():
    try:
        return st.secrets["google_oauth"]["client_id"]
    except Exception:
        return os.getenv("GOOGLE_CLIENT_ID", "")


def get_google_client_secret():
    try:
        return st.secrets["google_oauth"]["client_secret"]
    except Exception:
        return os.getenv("GOOGLE_CLIENT_SECRET", "")


# ============================================================
# OUTILS
# ============================================================

def html(content: str):
    st.markdown(content, unsafe_allow_html=True)


def image_to_base64(path: str) -> str:
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_connection():
    return sqlite3.connect(DB_PATH)


def clear_url_params():
    try:
        st.query_params.clear()
    except Exception:
        try:
            st.experimental_set_query_params()
        except Exception:
            pass


def get_query_param(name: str):
    try:
        value = st.query_params.get(name)
        if isinstance(value, list):
            return value[0] if value else None
        return value
    except Exception:
        try:
            params = st.experimental_get_query_params()
            value = params.get(name)
            if isinstance(value, list):
                return value[0] if value else None
            return value
        except Exception:
            return None


# ============================================================
# BASE DE DONNÉES UTILISATEURS
# ============================================================

def ensure_users_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def get_user_by_email_or_username(identifier: str):
    ensure_users_table()

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM users
        WHERE email = ? OR username = ?
        LIMIT 1
        """,
        (identifier, identifier),
    )

    row = cur.fetchone()
    conn.close()

    return dict(row) if row else None


def create_user(username: str, email: str, password: str):
    ensure_users_table()

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                email,
                hash_password(password),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        user_id = cur.lastrowid
        conn.close()
        return True, user_id, "Compte créé avec succès."

    except sqlite3.IntegrityError:
        conn.close()
        return False, None, "Cet email ou ce nom d’utilisateur existe déjà."

    except Exception as e:
        conn.close()
        return False, None, f"Erreur lors de la création du compte : {e}"


def create_or_get_google_user(email: str, name: str):
    ensure_users_table()

    existing = get_user_by_email_or_username(email)
    if existing:
        return existing

    base_username = (name or email.split("@")[0]).strip().lower()
    base_username = "".join(ch for ch in base_username if ch.isalnum() or ch in ["_", "-", "."])
    if not base_username:
        base_username = email.split("@")[0]

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    username = base_username
    counter = 1

    while True:
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not cur.fetchone():
            break
        counter += 1
        username = f"{base_username}{counter}"

    cur.execute(
        """
        INSERT INTO users (username, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            username,
            email,
            "GOOGLE_AUTH_USER",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()

    cur.execute("SELECT * FROM users WHERE email = ? LIMIT 1", (email,))
    row = cur.fetchone()
    conn.close()

    return dict(row)


def verify_login(identifier: str, password: str):
    user = get_user_by_email_or_username(identifier)

    if not user:
        return False, None, "Aucun compte trouvé avec ces identifiants."

    if user.get("password_hash") == "GOOGLE_AUTH_USER":
        return False, None, "Ce compte utilise la connexion Google. Cliquez sur Continuer avec Google."

    if user.get("password_hash") != hash_password(password):
        return False, None, "Mot de passe incorrect."

    return True, user, "Connexion réussie."


# ============================================================
# SESSION
# ============================================================

def init_auth_state():
    ensure_users_table()

    defaults = {
        "logged_in": False,
        "user_id": None,
        "username": None,
        "email": None,
        "oauth_state": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login_user(user: dict):
    st.session_state.logged_in = True
    st.session_state.user_id = user.get("id")
    st.session_state.username = user.get("username")
    st.session_state.email = user.get("email")


def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.email = None
    st.session_state.oauth_state = None


# ============================================================
# GOOGLE OAUTH LOGIC
# ============================================================

def build_google_auth_url():
    client_id = get_google_client_id()

    if not client_id:
        return "#"

    state = secrets.token_urlsafe(24)
    st.session_state.oauth_state = state

    params = {
        "client_id": client_id,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "include_granted_scopes": "true",
        "prompt": "select_account",
        "state": state,
    }

    return GOOGLE_AUTH_ENDPOINT + "?" + urllib.parse.urlencode(params)


def exchange_code_for_token(code: str):
    client_id = get_google_client_id()
    client_secret = get_google_client_secret()

    if not client_id or not client_secret:
        raise RuntimeError(
            "Client ID ou Client Secret manquant. Ajoutez-les dans .streamlit/secrets.toml."
        )

    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = requests.post(GOOGLE_TOKEN_ENDPOINT, data=data, timeout=20)

    if response.status_code != 200:
        raise RuntimeError(f"Échec échange token Google : {response.text}")

    return response.json()


def fetch_google_userinfo(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(GOOGLE_USERINFO_ENDPOINT, headers=headers, timeout=20)

    if response.status_code != 200:
        raise RuntimeError(f"Impossible de récupérer le profil Google : {response.text}")

    return response.json()


def handle_google_callback():
    code = get_query_param("code")
    state = get_query_param("state")
    error = get_query_param("error")

    if error:
        clear_url_params()
        st.error(f"Connexion Google annulée ou refusée : {error}")
        return

    if not code:
        return

    expected_state = st.session_state.get("oauth_state")

    if expected_state and state != expected_state:
        clear_url_params()
        st.error("Connexion Google refusée : état de sécurité invalide.")
        return

    try:
        token_data = exchange_code_for_token(code)
        access_token = token_data.get("access_token")

        if not access_token:
            raise RuntimeError("Access token Google absent.")

        userinfo = fetch_google_userinfo(access_token)

        email = userinfo.get("email")
        name = userinfo.get("name") or userinfo.get("given_name") or ""

        if not email:
            raise RuntimeError("Google n'a pas retourné d'adresse email.")

        user = create_or_get_google_user(email=email, name=name)
        login_user(user)

        clear_url_params()
        st.success("Connexion Google réussie.")
        st.rerun()

    except Exception as e:
        clear_url_params()
        st.error(f"Erreur Google OAuth : {e}")


# ============================================================
# STYLE GLOBAL STREAMLIT + FORMULAIRE DROIT
# ============================================================

def inject_global_login_style():
    html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --blue: #2F7CFF;
    --cyan: #54DFFF;
    --text: #10233F;
    --muted: #5F6F88;
}

* {
    box-sizing: border-box;
}

html, body, .stApp {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background:
        radial-gradient(circle at 0% 0%, rgba(47,124,255,0.11), transparent 26%),
        radial-gradient(circle at 100% 0%, rgba(49,230,168,0.12), transparent 24%),
        linear-gradient(135deg, #F8FBFF 0%, #EEF4FF 48%, #F8FFFD 100%) !important;
}

/* Masquer Streamlit + navigation native */
#MainMenu,
footer,
header,
[data-testid="stSidebar"],
[data-testid="stSidebarNav"] {
    visibility: hidden !important;
    display: none !important;
    width: 0 !important;
    min-width: 0 !important;
}

/* Masquer une sidebar personnalisée si elle existe dans app.py/styles.py */
.sidebar,
.custom-sidebar,
.app-sidebar,
.finpilot-sidebar,
.fp-sidebar,
.side-nav,
.nav-sidebar,
.left-sidebar,
.menu-sidebar,
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    min-width: 0 !important;
}

/* Si ton app a un conteneur décalé à cause de la sidebar */
.main-content,
.app-content,
.page-content,
.content,
.fp-main,
.dashboard-main {
    margin-left: 0 !important;
    padding-left: 0 !important;
}

.main .block-container {
    max-width: 1640px !important;
    padding: 1.7rem 2.4rem 1.5rem 2.4rem !important;
}

iframe {
    border: none !important;
}

/* Carte formulaire droite */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.98) !important;
    border: 1px solid #E2EAF7 !important;
    border-radius: 32px !important;
    box-shadow: 0 28px 72px rgba(28,64,132,0.13) !important;
    padding: 2.25rem 2.35rem !important;
    min-height: 760px !important;
    display: flex !important;
    align-items: center !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    width: 100% !important;
}

.login-top-label {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    color: #246DFF;
    font-size: 0.92rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
}

.login-lock-icon {
    width: 17px;
    height: 17px;
    display: inline-block;
    position: relative;
    border: 2px solid #246DFF;
    border-radius: 4px;
}

.login-lock-icon::before {
    content: "";
    position: absolute;
    width: 9px;
    height: 8px;
    border: 2px solid #246DFF;
    border-bottom: none;
    border-radius: 9px 9px 0 0;
    top: -9px;
    left: 2px;
}

.login-title {
    color: var(--text);
    font-size: 2.55rem;
    line-height: 1.08;
    font-weight: 900;
    letter-spacing: -0.04em;
    margin-bottom: 0.85rem;
}

.login-subtitle {
    color: var(--muted);
    font-size: 1.02rem;
    line-height: 1.6;
    margin-bottom: 1.5rem;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 2.4rem !important;
    border-bottom: 1px solid #E6EEFA !important;
    margin-bottom: 1.25rem !important;
}

.stTabs [data-baseweb="tab"] {
    height: 50px !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    color: #5E6D84 !important;
    padding: 0 !important;
    font-size: 1.02rem !important;
    font-weight: 800 !important;
}

.stTabs [aria-selected="true"] {
    color: #246DFF !important;
    border-bottom: 3px solid #246DFF !important;
}

div[data-testid="stTextInput"] label {
    color: #172945 !important;
    font-size: 0.95rem !important;
    font-weight: 800 !important;
}

div[data-testid="stTextInput"] input {
    min-height: 56px !important;
    border-radius: 14px !important;
    border: 1px solid #DBE5F5 !important;
    font-size: 1rem !important;
    padding-left: 1rem !important;
    color: #10233F !important;
    background: white !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #9AA8BC !important;
}

div[data-testid="stCheckbox"] label,
div[data-testid="stCheckbox"] span {
    font-size: 0.92rem !important;
    color: #34445D !important;
}

.forgot-link-wrap {
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
}

.forgot-link-wrap a {
    color: #246DFF;
    text-decoration: none;
    font-weight: 800;
    font-size: 0.92rem;
}

/* Correction importante : bouton bleu, même si un autre CSS de ton app force le rouge */
.stButton > button,
button[kind="primary"],
div[data-testid="stFormSubmitButton"] button,
div[data-testid="stButton"] button,
div[data-testid="baseButton-primary"],
[data-testid="stBaseButton-primary"] {
    min-height: 56px !important;
    border-radius: 14px !important;
    border: none !important;
    font-size: 1.05rem !important;
    font-weight: 900 !important;
}

div[data-testid="stFormSubmitButton"] button,
div[data-testid="stFormSubmitButton"] button:hover,
div[data-testid="stFormSubmitButton"] button:focus,
div[data-testid="stButton"] button[kind="primary"],
div[data-testid="stButton"] button[kind="primary"]:hover,
button[kind="primary"],
button[kind="primary"]:hover,
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(90deg, #2F7CFF 0%, #4D55FF 100%) !important;
    color: white !important;
    box-shadow: 0 15px 32px rgba(47,124,255,0.24) !important;
}

.or-line {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: #7A889D;
    margin: 1rem 0;
    font-size: 0.9rem;
    font-weight: 700;
}

.or-line::before,
.or-line::after {
    content: "";
    height: 1px;
    background: #E4ECF7;
    flex: 1;
}

/* Bouton Google cliquable */
.google-login-link {
    width: 100%;
    min-height: 56px;
    border: 1px solid #DBE5F5;
    border-radius: 14px;
    background: white;
    color: #22324D !important;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.85rem;
    font-size: 1rem;
    font-weight: 800;
    text-decoration: none !important;
    transition: 0.2s ease;
}

.google-login-link:hover {
    border-color: #BFD0EA;
    box-shadow: 0 12px 26px rgba(28,64,132,0.10);
    transform: translateY(-1px);
}

.google-g {
    font-size: 1.75rem;
    font-weight: 900;
    background: linear-gradient(90deg, #4285F4 0 25%, #EA4335 25% 50%, #FBBC05 50% 75%, #34A853 75% 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.oauth-warning {
    margin-top: 0.8rem;
    padding: 0.9rem 1rem;
    border-radius: 14px;
    background: #FFF7E8;
    border: 1px solid #F5D69A;
    color: #8A5A00;
    font-size: 0.9rem;
    line-height: 1.45;
}

.register-note {
    background: linear-gradient(135deg, rgba(47,124,255,0.08), rgba(49,230,168,0.08));
    border: 1px solid #DDE8F8;
    border-radius: 16px;
    padding: 0.95rem 1rem;
    color: #51657F;
    font-size: 0.92rem;
    line-height: 1.5;
    margin-top: 0.8rem;
}

.disclaimer {
    margin-top: 1.55rem;
    display: flex;
    gap: 0.8rem;
    align-items: flex-start;
    color: #53647C;
    font-size: 0.92rem;
    line-height: 1.45;
}

.disclaimer-icon {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: #EEF5FF;
    color: #2F7CFF;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #D9E7FF;
    flex-shrink: 0;
    position: relative;
}

.disclaimer-icon::before {
    content: "";
    width: 16px;
    height: 20px;
    border: 2px solid #2F7CFF;
    border-radius: 10px 10px 12px 12px;
    display: block;
}

.disclaimer-icon::after {
    content: "";
    position: absolute;
    width: 8px;
    height: 4px;
    border-left: 2px solid #2F7CFF;
    border-bottom: 2px solid #2F7CFF;
    transform: rotate(-45deg);
    top: 17px;
    left: 14px;
}

@media (max-width: 1200px) {
    .main .block-container {
        padding: 1rem !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        min-height: auto !important;
    }
}
</style>
""")


# ============================================================
# PANNEAU GAUCHE SANS EMOJI : FIGURES CSS
# ============================================================

def render_left_panel(logo_b64: str):
    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="fp-brand-logo">'
    else:
        logo_html = '<div class="fp-brand-fallback">FP</div>'

    left_panel_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    padding: 0;
    font-family: 'Inter', sans-serif;
    background: transparent;
    overflow: hidden;
}}

.fp-left-panel {{
    position: relative;
    height: 760px;
    width: 100%;
    background:
        radial-gradient(circle at 17% 12%, rgba(255,255,255,0.06), transparent 36%),
        radial-gradient(circle at 92% 11%, rgba(73,143,255,0.30), transparent 19%),
        linear-gradient(145deg, #021342 0%, #052574 43%, #0B55D8 100%);
    border-radius: 32px;
    padding: 2.55rem 2.6rem 2rem 2.6rem;
    color: white;
    overflow: hidden;
    box-shadow: 0 32px 85px rgba(10, 47, 125, 0.25);
    border: 1px solid rgba(255,255,255,0.13);
}}

.fp-left-panel::after {{
    content: "";
    position: absolute;
    top: -120px;
    right: -115px;
    width: 360px;
    height: 360px;
    border-radius: 999px;
    background: rgba(255,255,255,0.11);
    z-index: 1;
}}

.fp-left-panel::before {{
    content: "";
    position: absolute;
    bottom: -115px;
    left: -90px;
    width: 280px;
    height: 280px;
    border-radius: 999px;
    background: rgba(47,124,255,0.22);
    z-index: 1;
}}

.fp-stars {{
    position: absolute;
    inset: 0;
    z-index: 1;
    opacity: 0.75;
    background-image:
        radial-gradient(circle at 15% 8%, rgba(255,255,255,0.7) 0 1px, transparent 1.4px),
        radial-gradient(circle at 43% 7%, rgba(255,255,255,0.35) 0 1px, transparent 1.4px),
        radial-gradient(circle at 67% 13%, rgba(255,255,255,0.52) 0 1px, transparent 1.4px),
        radial-gradient(circle at 29% 28%, rgba(255,255,255,0.42) 0 1px, transparent 1.4px),
        radial-gradient(circle at 80% 38%, rgba(255,255,255,0.32) 0 1px, transparent 1.4px),
        radial-gradient(circle at 48% 53%, rgba(255,255,255,0.38) 0 1px, transparent 1.4px),
        radial-gradient(circle at 88% 72%, rgba(255,255,255,0.30) 0 1px, transparent 1.4px);
}}

.fp-chart-visual {{
    position: absolute;
    right: 18px;
    top: 125px;
    width: 430px;
    height: 400px;
    z-index: 2;
    opacity: 0.95;
    pointer-events: none;
}}

.chart-grid {{
    position: absolute;
    inset: 0;
    background:
        linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.045) 1px, transparent 1px);
    background-size: 52px 52px;
    mask-image: radial-gradient(circle at 55% 45%, black 0%, transparent 78%);
}}

.chart-bars {{
    position: absolute;
    right: 30px;
    bottom: 22px;
    width: 260px;
    height: 285px;
    display: flex;
    align-items: flex-end;
    gap: 13px;
}}

.chart-bar {{
    width: 18px;
    border-radius: 10px 10px 0 0;
    background: linear-gradient(180deg, rgba(47,124,255,0.78), rgba(47,124,255,0.08));
    animation: barPulse 3s ease-in-out infinite alternate;
}}

.chart-bar.b1 {{ height: 64px; animation-delay: 0s; }}
.chart-bar.b2 {{ height: 92px; animation-delay: .18s; }}
.chart-bar.b3 {{ height: 122px; animation-delay: .36s; }}
.chart-bar.b4 {{ height: 160px; animation-delay: .54s; }}
.chart-bar.b5 {{ height: 198px; animation-delay: .72s; }}
.chart-bar.b6 {{ height: 232px; animation-delay: .9s; }}
.chart-bar.b7 {{ height: 264px; animation-delay: 1.08s; }}

@keyframes barPulse {{
    from {{ opacity: 0.48; transform: scaleY(.90); }}
    to {{ opacity: 0.88; transform: scaleY(1.04); }}
}}

.chart-line {{
    position: absolute;
    left: 25px;
    top: 92px;
    width: 360px;
    height: 215px;
    border-radius: 50%;
    border-top: 5px solid #4BE7FF;
    transform: rotate(-15deg);
    box-shadow: 0 -10px 25px rgba(75,231,255,0.13);
    opacity: .95;
    animation: lineFloat 4.8s ease-in-out infinite;
}}

.chart-line::before {{
    content: "";
    position: absolute;
    width: 78px;
    height: 78px;
    border-radius: 50%;
    border-top: 5px solid #4BE7FF;
    left: 88px;
    top: 78px;
    transform: rotate(58deg);
}}

.chart-line::after {{
    content: "";
    position: absolute;
    right: 2px;
    top: -8px;
    width: 13px;
    height: 13px;
    border-radius: 50%;
    background: #65F0FF;
    box-shadow: 0 0 22px rgba(101,240,255,0.8);
}}

@keyframes lineFloat {{
    0%, 100% {{ transform: rotate(-15deg) translateY(0); }}
    50% {{ transform: rotate(-15deg) translateY(-8px); }}
}}

.fp-left-content {{
    position: relative;
    z-index: 3;
}}

.fp-brand {{
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2.2rem;
}}

.fp-brand-logo {{
    width: 88px;
    height: 88px;
    border-radius: 24px;
    object-fit: contain;
    background: rgba(255,255,255,0.96);
    padding: 0.32rem;
    border: 2px solid rgba(255,255,255,0.72);
    box-shadow: 0 16px 36px rgba(0,0,0,0.20);
}}

.fp-brand-fallback {{
    width: 88px;
    height: 88px;
    border-radius: 24px;
    background: linear-gradient(135deg, #2F7CFF, #31E6A8);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    font-weight: 900;
    color: white;
    border: 2px solid rgba(255,255,255,0.72);
    box-shadow: 0 16px 36px rgba(0,0,0,0.20);
}}

.fp-brand-title {{
    font-size: 2.15rem;
    font-weight: 900;
    color: white;
    line-height: 1;
}}

.fp-brand-subtitle {{
    color: rgba(255,255,255,0.84);
    font-size: 1.02rem;
    font-weight: 500;
    margin-top: 0.26rem;
}}

.fp-kicker {{
    color: #52F0FF;
    font-size: 0.95rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.11em;
    margin-bottom: 0.92rem;
}}

.fp-main-title {{
    color: white;
    font-size: 3.65rem;
    line-height: 1.08;
    font-weight: 900;
    letter-spacing: -0.055em;
    max-width: 780px;
    margin-bottom: 1.1rem;
}}

.fp-main-title .accent {{
    color: #55DFFF;
}}

.fp-main-text {{
    color: rgba(255,255,255,0.92);
    font-size: 1.18rem;
    line-height: 1.7;
    max-width: 710px;
    margin-bottom: 2rem;
}}

.floating-stat {{
    position: absolute;
    z-index: 4;
    background: rgba(10, 43, 115, 0.78);
    border: 1px solid rgba(96,178,255,0.36);
    border-radius: 18px;
    box-shadow: 0 18px 45px rgba(0,0,0,0.20);
    padding: 0.9rem 1rem;
    backdrop-filter: blur(8px);
    color: white;
}}

.floating-stat.stat-1 {{
    top: 110px;
    right: 54px;
    min-width: 142px;
    animation: floatOne 6s ease-in-out infinite;
}}

.floating-stat.stat-2 {{
    top: 365px;
    right: 204px;
    min-width: 94px;
    animation: floatTwo 5.4s ease-in-out infinite;
}}

@keyframes floatOne {{
    0%,100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-10px); }}
}}

@keyframes floatTwo {{
    0%,100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(8px); }}
}}

.floating-label {{
    color: rgba(255,255,255,0.84);
    font-size: 0.86rem;
    font-weight: 700;
    margin-bottom: 0.1rem;
}}

.floating-value {{
    color: #39E7C0;
    font-size: 1.55rem;
    line-height: 1;
    font-weight: 900;
}}

.fp-feature-strip {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0;
    border-radius: 22px;
    overflow: hidden;
    background: rgba(3, 21, 63, 0.44);
    border: 1px solid rgba(255,255,255,0.13);
    backdrop-filter: blur(10px);
    margin-top: 2.1rem;
}}

.fp-feature {{
    display: grid;
    grid-template-columns: 58px 1fr;
    gap: 1rem;
    padding: 1.25rem 1rem;
    border-right: 1px solid rgba(255,255,255,0.11);
}}

.fp-feature:last-child {{
    border-right: none;
}}

.fp-feature-title {{
    color: white;
    font-size: 1.1rem;
    font-weight: 900;
    margin-bottom: 0.25rem;
}}

.fp-feature-text {{
    color: rgba(255,255,255,0.76);
    font-size: 0.9rem;
    line-height: 1.45;
}}

.fp-icon-box {{
    width: 54px;
    height: 54px;
    border-radius: 17px;
    background: rgba(7, 50, 142, 0.60);
    border: 1px solid rgba(83,151,255,0.34);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.icon-ai .node {{
    position: absolute;
    width: 8px;
    height: 8px;
    background: #55DFFF;
    border-radius: 999px;
    box-shadow: 0 0 12px rgba(85,223,255,.8);
}}

.icon-ai .n1 {{ left: 15px; top: 16px; }}
.icon-ai .n2 {{ right: 14px; top: 15px; }}
.icon-ai .n3 {{ left: 24px; bottom: 14px; }}

.icon-ai::before {{
    content: "";
    width: 28px;
    height: 22px;
    border: 2px solid rgba(85,223,255,0.75);
    border-radius: 999px;
    transform: rotate(-8deg);
}}

.icon-shield::before {{
    content: "";
    width: 26px;
    height: 32px;
    border: 3px solid #55DFFF;
    border-radius: 14px 14px 18px 18px;
    clip-path: polygon(0 0, 100% 0, 100% 65%, 50% 100%, 0 65%);
}}

.icon-shield::after {{
    content: "";
    position: absolute;
    width: 13px;
    height: 7px;
    border-left: 3px solid #39E7C0;
    border-bottom: 3px solid #39E7C0;
    transform: rotate(-45deg);
    top: 24px;
    left: 20px;
}}

.icon-bars {{
    gap: 4px;
}}

.icon-bars span {{
    display: block;
    width: 6px;
    border-radius: 8px 8px 2px 2px;
    background: linear-gradient(180deg, #55DFFF, #2F7CFF);
}}

.icon-bars span:nth-child(1) {{ height: 16px; }}
.icon-bars span:nth-child(2) {{ height: 25px; }}
.icon-bars span:nth-child(3) {{ height: 34px; }}

.fp-bottom-line {{
    height: 1px;
    width: 100%;
    background: rgba(255,255,255,0.11);
    margin: 1.55rem 0 1rem 0;
}}

.fp-trust-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0;
}}

.fp-trust-item {{
    display: grid;
    grid-template-columns: 44px 1fr;
    gap: 0.8rem;
    padding: 0.85rem 1rem;
    border-right: 1px solid rgba(255,255,255,0.11);
    align-items: start;
}}

.fp-trust-item:last-child {{
    border-right: none;
}}

.fp-trust-icon {{
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: rgba(14,56,150,0.70);
    border: 1px solid rgba(96,178,255,0.30);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}}

.trust-local::before {{
    content: "";
    width: 20px;
    height: 16px;
    border-left: 3px solid #55DFFF;
    border-bottom: 3px solid #55DFFF;
    transform: skew(-12deg);
}}

.trust-local::after {{
    content: "";
    position: absolute;
    width: 7px;
    height: 7px;
    background: #39E7C0;
    border-radius: 999px;
    right: 11px;
    top: 11px;
}}

.trust-lock::before {{
    content: "";
    width: 17px;
    height: 16px;
    border: 2px solid #55DFFF;
    border-radius: 4px;
    position: absolute;
    top: 18px;
}}

.trust-lock::after {{
    content: "";
    width: 13px;
    height: 11px;
    border: 2px solid #55DFFF;
    border-bottom: none;
    border-radius: 9px 9px 0 0;
    position: absolute;
    top: 10px;
}}

.trust-check::before {{
    content: "";
    width: 20px;
    height: 20px;
    border-radius: 999px;
    background: rgba(57,231,192,0.18);
    border: 2px solid #39E7C0;
}}

.trust-check::after {{
    content: "";
    position: absolute;
    width: 10px;
    height: 5px;
    border-left: 3px solid #39E7C0;
    border-bottom: 3px solid #39E7C0;
    transform: rotate(-45deg);
    top: 17px;
    left: 15px;
}}

.fp-trust-title {{
    color: white;
    font-size: 0.98rem;
    font-weight: 900;
    margin-bottom: 0.2rem;
}}

.fp-trust-text {{
    color: rgba(255,255,255,0.73);
    font-size: 0.82rem;
    line-height: 1.35;
}}
</style>
</head>

<body>
<div class="fp-left-panel">
    <div class="fp-stars"></div>

    <div class="fp-chart-visual">
        <div class="chart-grid"></div>
        <div class="chart-bars">
            <div class="chart-bar b1"></div>
            <div class="chart-bar b2"></div>
            <div class="chart-bar b3"></div>
            <div class="chart-bar b4"></div>
            <div class="chart-bar b5"></div>
            <div class="chart-bar b6"></div>
            <div class="chart-bar b7"></div>
        </div>
        <div class="chart-line"></div>
    </div>

    <div class="floating-stat stat-1">
        <div class="floating-label">Portefeuille simulé</div>
        <div class="floating-value">+12,4%</div>
    </div>

    <div class="floating-stat stat-2">
        <div class="floating-label">Sharpe</div>
        <div class="floating-value">1,28</div>
    </div>

    <div class="fp-left-content">
        <div class="fp-brand">
            {logo_html}
            <div>
                <div class="fp-brand-title">FinPilot</div>
                <div class="fp-brand-subtitle">Marchés financiers · Intelligence artificielle</div>
            </div>
        </div>

        <div class="fp-kicker">Plateforme d’aide à l’investissement</div>

        <div class="fp-main-title">
            Investissez avec plus<br>
            de clarté <span class="accent">grâce à l’IA</span>
        </div>

        <div class="fp-main-text">
            FinPilot combine intelligence artificielle et données de marché pour vous aider
            à analyser, comparer et simuler vos investissements en toute confiance.
        </div>

        <div class="fp-feature-strip">
            <div class="fp-feature">
                <div class="fp-icon-box icon-ai">
                    <span class="node n1"></span>
                    <span class="node n2"></span>
                    <span class="node n3"></span>
                </div>
                <div>
                    <div class="fp-feature-title">IA avancée</div>
                    <div class="fp-feature-text">Recommandations fondées sur vos objectifs et le marché.</div>
                </div>
            </div>

            <div class="fp-feature">
                <div class="fp-icon-box icon-shield"></div>
                <div>
                    <div class="fp-feature-title">Analyse complète</div>
                    <div class="fp-feature-text">Comparez les actifs et mesurez le risque avec précision.</div>
                </div>
            </div>

            <div class="fp-feature">
                <div class="fp-icon-box icon-bars">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <div>
                    <div class="fp-feature-title">Simulation sans risque</div>
                    <div class="fp-feature-text">Testez vos stratégies dans un environnement sécurisé.</div>
                </div>
            </div>
        </div>

        <div class="fp-bottom-line"></div>

        <div class="fp-trust-grid">
            <div class="fp-trust-item">
                <div class="fp-trust-icon trust-local"></div>
                <div>
                    <div class="fp-trust-title">Données locales</div>
                    <div class="fp-trust-text">Vos données restent sur votre appareil.</div>
                </div>
            </div>

            <div class="fp-trust-item">
                <div class="fp-trust-icon trust-lock"></div>
                <div>
                    <div class="fp-trust-title">Sécurité renforcée</div>
                    <div class="fp-trust-text">Chiffrement et confidentialité.</div>
                </div>
            </div>

            <div class="fp-trust-item">
                <div class="fp-trust-icon trust-check"></div>
                <div>
                    <div class="fp-trust-title">Simulation sans risque</div>
                    <div class="fp-trust-text">Aucun argent réel engagé.</div>
                </div>
            </div>
        </div>
    </div>
</div>
</body>
</html>
"""

    components.html(left_panel_html, height=780, scrolling=False)


# ============================================================
# PAGE AUTH
# ============================================================

def render_auth_screen():
    init_auth_state()

    # Important : d'abord traiter le retour Google.
    # Si Google renvoie ?code=..., on connecte l'utilisateur puis on reste dans l'app.
    handle_google_callback()

    inject_global_login_style()

    logo_b64 = image_to_base64("assets/finpilot_logo_final.png")

    google_client_id = get_google_client_id()
    google_client_secret = get_google_client_secret()
    google_auth_url = build_google_auth_url()

    left, right = st.columns([1.75, 1.05], gap="large")

    with left:
        render_left_panel(logo_b64)

    with right:
        with st.container(border=True):
            html("""
<div class="login-top-label">
    <span class="login-lock-icon"></span>
    <span>Espace sécurisé</span>
</div>

<div class="login-title">Bienvenue sur FinPilot</div>

<div class="login-subtitle">
    Connectez-vous pour accéder à vos portefeuilles, analyses
    et simulations personnalisées.
</div>
""")

            login_tab, register_tab = st.tabs(["Connexion", "Créer un compte"])

            with login_tab:
                with st.form("login_form_finpilot", clear_on_submit=False):
                    identifier = st.text_input(
                        "Email ou nom d’utilisateur",
                        placeholder="exemple@email.com",
                        key="login_identifier_ref",
                    )

                    password = st.text_input(
                        "Mot de passe",
                        type="password",
                        placeholder="Votre mot de passe",
                        key="login_password_ref",
                    )

                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.checkbox("Se souvenir de moi", key="remember_me_ref")
                    with c2:
                        html("""
<div class="forgot-link-wrap">
    <a href="#">Mot de passe oublié ?</a>
</div>
""")

                    submit_login = st.form_submit_button(
                        "→  Se connecter",
                        type="primary",
                        use_container_width=True,
                    )

                    if submit_login:
                        if not identifier.strip() or not password.strip():
                            st.error("Veuillez remplir tous les champs.")
                        else:
                            ok, user, message = verify_login(identifier.strip(), password.strip())

                            if ok:
                                login_user(user)
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

                html("""
<div class="or-line">OU</div>
""")

                if google_client_id and google_client_secret:
                    html(f"""
<a class="google-login-link" href="{google_auth_url}" target="_self">
    <span class="google-g">G</span>
    <span>Continuer avec Google</span>
</a>
""")
                else:
                    html("""
<div class="google-login-link" style="opacity:0.55; cursor:not-allowed;">
    <span class="google-g">G</span>
    <span>Google à configurer</span>
</div>

<div class="oauth-warning">
    Le bouton Google sera actif après l’ajout de <b>client_id</b> et
    <b>client_secret</b> dans <b>.streamlit/secrets.toml</b>.
    Utilisez aussi <b>http://localhost:8502</b> comme URL de redirection Google Cloud.
</div>
""")

            with register_tab:
                with st.form("register_form_finpilot", clear_on_submit=False):
                    username = st.text_input(
                        "Nom d’utilisateur",
                        placeholder="Votre nom d’utilisateur",
                        key="register_username_ref",
                    )

                    email = st.text_input(
                        "Adresse email",
                        placeholder="exemple@email.com",
                        key="register_email_ref",
                    )

                    password = st.text_input(
                        "Mot de passe",
                        type="password",
                        placeholder="Minimum 6 caractères",
                        key="register_password_ref",
                    )

                    confirm = st.text_input(
                        "Confirmer le mot de passe",
                        type="password",
                        placeholder="Répétez le mot de passe",
                        key="register_confirm_ref",
                    )

                    submit_register = st.form_submit_button(
                        "Créer mon compte",
                        type="primary",
                        use_container_width=True,
                    )

                    if submit_register:
                        username = username.strip()
                        email = email.strip()

                        if not username or not email or not password or not confirm:
                            st.error("Veuillez remplir tous les champs.")
                        elif "@" not in email or "." not in email:
                            st.error("Veuillez saisir une adresse email valide.")
                        elif len(password) < 6:
                            st.error("Le mot de passe doit contenir au moins 6 caractères.")
                        elif password != confirm:
                            st.error("Les mots de passe ne correspondent pas.")
                        else:
                            ok, user_id, message = create_user(username, email, password)

                            if ok:
                                user = get_user_by_email_or_username(email)
                                login_user(user)
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

                html("""
<div class="register-note">
    Après création du compte, vous pourrez définir votre capital initial,
    sauvegarder vos analyses et commencer vos simulations.
</div>
""")

            html("""
<div class="disclaimer">
    <div class="disclaimer-icon"></div>
    <div>
        <b>FinPilot</b> ne donne pas de conseils en investissement.<br>
        Les performances passées ne préjugent pas des performances futures.
    </div>
</div>
""")


# Si tu testes ce fichier seul, décommente les deux lignes suivantes :
# st.set_page_config(page_title="FinPilot", page_icon="📈", layout="wide")
# render_auth_screen()
