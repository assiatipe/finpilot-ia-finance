import streamlit as st
import re
import textwrap
from auth import init_auth_state, render_auth_screen
from sidebar_ui import render_sidebar
from styles import load_global_styles
from ai_helper import get_chat_response

# ============================================================
# CONFIG ET AUTHENTIFICATION
# ============================================================
st.set_page_config(
    page_title="FinPilot · Assistant IA",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_auth_state()
st.markdown(load_global_styles(), unsafe_allow_html=True)

if not st.session_state.get("logged_in"):
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)
    render_auth_screen()
    st.stop()

user_id = st.session_state.get("user_id")
username = st.session_state.get("user_name") or st.session_state.get("username") or "Investisseur"

# ============================================================
# ICONES SVG
# ============================================================
def get_svg_icon(name, width=20, height=20, color="currentColor"):
    svgs = {
        "robot": f"""<svg width="{width}" height="{height}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2 2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/><path d="M12 8v14"/><path d="M8 12h8"/></svg>""",
        "send": f"""<svg width="{width}" height="{height}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>"""
    }
    return svgs.get(name, "")

# ============================================================
# SIDEBAR
# ============================================================
render_sidebar(active_page="assistant")

# ============================================================
st.markdown("""
<style>
/* Import de police premium */
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

/* Fond de la page luxueux avec des orbes lumineuses floues */
.stApp {
    background:
        radial-gradient(circle at 10% 40%, rgba(35, 216, 240, 0.12), transparent 28%),
        radial-gradient(circle at 90% 60%, rgba(122, 92, 255, 0.10), transparent 28%),
        radial-gradient(circle at 50% 0%, #FFFFFF 0%, #F8FAFC 100%) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Centrer le conteneur principal (élargi pour accueillir les deux colonnes) */
.block-container {
    max-width: 1050px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 8.5rem !important;
}

/* ------------------------------------------------------
   LEFT SIDEBAR CARD STYLE (MOCKUP)
   ------------------------------------------------------ */
.assistant-sidebar-card {
    background-color: #0E1629;
    border-radius: 24px;
    padding: 2.2rem 1.6rem;
    color: white;
    min-height: 480px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 12px 32px rgba(14, 22, 41, 0.18);
    margin-bottom: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.04);
}

.sidebar-title {
    font-size: 1.4rem;
    font-weight: 700;
    font-family: 'Sora', sans-serif;
    margin-bottom: 2rem;
    color: white;
    letter-spacing: -0.02em;
}

.sidebar-menu-list {
    display: flex;
    flex-direction: column;
    gap: 1.3rem;
    flex-grow: 1;
}

.menu-item {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    font-size: 0.95rem;
    font-weight: 600;
    color: #64748B;
    transition: color 0.2s ease;
}

.menu-item.active {
    color: #F8FAFC;
}

.dot-online {
    width: 8px;
    height: 8px;
    background-color: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 10px #10B981;
}

.diamond-bullet {
    color: #818CF8;
    font-size: 0.95rem;
    font-weight: 700;
}

.sidebar-stats-box {
    background-color: #1E293B;
    border-radius: 16px;
    padding: 1.1rem;
    margin-top: auto;
    border: 1px solid rgba(255, 255, 255, 0.03);
}

.stats-label {
    font-size: 0.72rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.4rem;
    font-weight: 700;
}

.stats-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.stats-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: white;
    font-family: 'Sora', sans-serif;
}

.stats-badge {
    font-size: 0.78rem;
    font-weight: 700;
    color: #10B981;
    background-color: rgba(16, 185, 129, 0.12);
    padding: 0.2rem 0.5rem;
    border-radius: 30px;
}

/* ------------------------------------------------------
   RIGHT CHAT VIEW & BUBBLES
   ------------------------------------------------------ */
.header-container {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 1rem;
    justify-content: flex-start;
    margin-bottom: 2.5rem;
}

.header-avatar-circle {
    width: 54px;
    height: 54px;
    border-radius: 50%;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    box-shadow: 0 8px 25px rgba(47, 124, 255, 0.1);
    border: 2px solid transparent;
    background-image: linear-gradient(white, white), linear-gradient(135deg, #2F7CFF, #23D8F0);
    background-origin: border-box;
    background-clip: padding-box, border-box;
    margin-bottom: 0;
    flex-shrink: 0;
}

.header-avatar-circle::after {
    content: "";
    position: absolute;
    top: -5px; right: -5px; bottom: -5px; left: -5px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2F7CFF, #23D8F0);
    z-index: -1;
    opacity: 0.2;
    filter: blur(10px);
}

.header-title {
    font-size: 1.85rem;
    font-weight: 800;
    color: #0F172A;
    font-family: 'Sora', sans-serif;
    margin-bottom: 0;
    letter-spacing: -0.03em;
}

.online-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background-color: rgba(16, 185, 129, 0.08);
    color: #059669;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 0.35rem 0.85rem;
    border-radius: 30px;
    border: 1px solid rgba(16, 185, 129, 0.15);
}

.online-dot {
    width: 8px;
    height: 8px;
    background-color: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
    animation: pulse-green 2s infinite;
}

@keyframes pulse-green {
    0% { box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
    70% { box-shadow: 0 0 0 6px rgba(16,185,129,0); }
    100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
}

/* Structure des bulles de chat avec animation */
.chat-row {
    display: flex;
    margin-bottom: 1.5rem;
    width: 100%;
    animation: fadeInUp 0.4s ease-out forwards;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

.chat-row.user {
    justify-content: flex-end;
}

.chat-row.assistant {
    justify-content: flex-start;
}

.bubble-container {
    max-width: 85%;
    display: flex;
    flex-direction: column;
}

.assistant .bubble-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 0;
}

.bubble {
    padding: 1rem 1.4rem;
    border-radius: 20px;
    font-size: 1rem;
    line-height: 1.5;
    letter-spacing: -0.01em;
}

.bubble p {
    margin: 0;
}

/* Bulle Utilisateur (Indigo) */
.bubble.user {
    background: #6366F1 !important;
    color: white !important;
    border-bottom-right-radius: 4px;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.15) !important;
}

/* Bulle Assistant (Gris-bleu clair) */
.bubble.assistant {
    background-color: #F8FAFC !important;
    color: #1E293B !important;
    border-bottom-left-radius: 4px;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02) !important;
}

/* Boutons de suggestions (Pilules Glassmorphism) */
div[data-testid="column"] .stButton > button {
    border-radius: 30px !important;
    border: 1px solid rgba(47, 124, 255, 0.1) !important;
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(10px) !important;
    color: #2F7CFF !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.01) !important;
}

div[data-testid="column"] .stButton > button:hover {
    background: #2F7CFF !important;
    color: white !important;
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 6px 18px rgba(47, 124, 255, 0.18) !important;
}

/* Barre de saisie style "Îlot flottant" premium de la maquette */
div[data-testid="stChatInput"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding-bottom: 3.5rem !important;
    max-width: 100% !important;
    margin: 0 !important;
    position: relative !important;
}

div[data-testid="stChatInput"] > div {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(226, 232, 240, 0.9) !important;
    border-radius: 35px !important;
    box-shadow: 0 15px 35px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.03) !important;
    padding: 0.4rem 0.5rem 0.4rem 1.5rem !important;
    position: relative !important;
}

div[data-testid="stChatInput"] textarea {
    font-size: 0.98rem !important;
    color: #1E293B !important;
    font-weight: 500 !important;
}

/* Cacher le contour de focus orange dégueulasse de Streamlit */
div[data-testid="stChatInput"] > div:focus-within {
    border-color: #2F7CFF !important;
    box-shadow: 0 15px 35px rgba(47, 124, 255, 0.1), 0 0 0 3px rgba(47, 124, 255, 0.15) !important;
}

/* Bouton envoyer rond bleu avec flèche blanche */
div[data-testid="stChatInput"] button {
    background: #2563EB !important;
    border: none !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25) !important;
    transition: all 0.2s ease !important;
    padding: 0 !important;
}

div[data-testid="stChatInput"] button:hover {
    transform: scale(1.05);
    background: #1D4ED8 !important;
    box-shadow: 0 4px 12px rgba(29, 78, 216, 0.35) !important;
}

div[data-testid="stChatInput"] button svg {
    color: white !important;
    stroke: white !important;
    fill: none !important;
    stroke-width: 2.5px !important;
}

/* =========================================
   RESPONSIVITÉ (MOBILES & TABLETTES)
   ========================================= */
@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-bottom: 7.5rem !important;
    }
    
    .header-title {
        font-size: 1.6rem;
    }
    
    .header-avatar-circle {
        width: 44px;
        height: 44px;
    }
    
    .bubble-container {
        max-width: 95%;
    }
    
    .bubble {
        padding: 0.9rem 1.1rem;
        font-size: 0.95rem;
    }
    
    div[data-testid="stChatInput"] {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        padding-bottom: 1rem !important;
    }
    
    div[data-testid="column"] .stButton > button {
        font-size: 0.82rem !important;
        padding: 0.4rem 0.8rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Custom Assistant Sidebar Card HTML
html_sidebar = """
<div class="assistant-sidebar-card">
    <div>
        <div class="sidebar-title">Assistant</div>
        <div class="sidebar-menu-list">
            <div class="menu-item active">
                <span class="dot-online"></span>
                <span>En ligne</span>
            </div>
            <div class="menu-item">
                <span class="diamond-bullet">♦</span>
                <span>FAQ finance</span>
            </div>
            <div class="menu-item">
                <span class="diamond-bullet">♦</span>
                <span>Actions</span>
            </div>
            <div class="menu-item">
                <span class="diamond-bullet">♦</span>
                <span>Risques</span>
            </div>
        </div>
    </div>
    <div class="sidebar-stats-box">
        <div class="stats-label">Questions traitées</div>
        <div class="stats-row">
            <span class="stats-value">128</span>
            <span class="stats-badge">+12%</span>
        </div>
    </div>
</div>
"""

# Avatar & Header setup
robot_face_svg = """<svg width="32" height="32" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M22 10V6" stroke="#0F172A" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="22" cy="5" r="2" fill="#23D8F0"/>
  <rect x="10" y="10" width="24" height="20" rx="7" fill="#0F172A"/>
  <rect x="7" y="16" width="3" height="8" rx="1.5" fill="#2F7CFF"/>
  <rect x="34" y="16" width="3" height="8" rx="1.5" fill="#2F7CFF"/>
  <circle cx="17" cy="19" r="2.5" fill="#23D8F0"/>
  <circle cx="27" cy="19" r="2.5" fill="#23D8F0"/>
  <path d="M18 24C19.5 25.5 24.5 25.5 26 24" stroke="white" stroke-width="2" stroke-linecap="round"/>
</svg>"""

html_header = f"""<div class="header-container">
<div class="header-avatar-circle">
{robot_face_svg}
</div>
<div class="header-title">FinPilot Copilot</div>
<div class="online-badge">
<span class="online-dot"></span> En ligne
</div>
</div>"""

# ============================================================
# GESTION DE L'ETAT
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Bonjour ! Je suis **FinPilot**, votre conseiller financier. Je suis là pour vous aider à analyser votre portefeuille ou à comprendre le marché. Que souhaitez-vous faire ?"}
    ]

def set_prompt(text):
    st.session_state.pending_prompt = text

# ============================================================
# RENDERING SPLIT LAYOUT
# ============================================================
col_left, col_right = st.columns([1, 2.3], gap="large")

with col_left:
    st.markdown(html_sidebar, unsafe_allow_html=True)

with col_right:
    # 1. En-tête horizontal
    st.markdown(html_header, unsafe_allow_html=True)
    
    # 2. Affichage de l'historique
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            content_html = msg['content'].replace('\n', '<br>')
            html_msg = f"""<div class="chat-row user">
<div class="bubble-container">
<div class="bubble user">
{content_html}
</div>
</div>
</div>"""
            st.markdown(html_msg, unsafe_allow_html=True)
        else:
            content_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', msg['content'])
            content_html = content_html.replace('\n', '<br>')
            html_msg = f"""<div class="chat-row assistant">
<div class="bubble-container">
<div class="bubble assistant">
{content_html}
</div>
</div>
</div>"""
            st.markdown(html_msg, unsafe_allow_html=True)

    # 3. Suggestions d'action
    if len(st.session_state.messages) == 1:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.button("Mon portefeuille", on_click=set_prompt, args=("Peux-tu analyser mon portefeuille ?",), use_container_width=True)
        with c2:
            st.button("Actualités", on_click=set_prompt, args=("Quelles sont les actualités ?",), use_container_width=True)
        with c3:
            st.button("Guide débutant", on_click=set_prompt, args=("Je suis débutante, par où commencer ?",), use_container_width=True)
        with c4:
            st.button("Idées d'actions", on_click=set_prompt, args=("As-tu des idées d'investissement ?",), use_container_width=True)

    # 4. Traitement du message utilisateur en cours
    if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
        html_loading_start = f"""<div class="chat-row assistant" style="margin-top:1rem;">
<div class="bubble-container">
<div class="bubble assistant">"""
        st.markdown(html_loading_start, unsafe_allow_html=True)
        message_placeholder = st.empty()
        
        html_loading_end = """</div>
</div>
</div>"""
        st.markdown(html_loading_end, unsafe_allow_html=True)

        stream = get_chat_response(
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[1:]], 
            user_id=user_id, 
            username=username
        )
        
        full_response = ""
        for chunk in stream:
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

    # 5. Saisie utilisateur
    prompt = st.chat_input("Posez une question sur la finance...")

    if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    st.markdown("<div style='height: 150px; width: 100%;'></div>", unsafe_allow_html=True)
