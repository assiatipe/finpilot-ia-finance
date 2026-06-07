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
        radial-gradient(circle at 15% 45%, rgba(35, 216, 240, 0.12), transparent 28%),
        radial-gradient(circle at 85% 65%, rgba(122, 92, 255, 0.10), transparent 28%),
        radial-gradient(circle at 50% 0%, #FFFFFF 0%, #F8FAFC 100%) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Centrer le conteneur principal */
.block-container {
    max-width: 800px !important;
    padding-top: 2rem !important;
    padding-bottom: 8.5rem !important;
}

/* En-tête centré premium */
.header-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    margin-bottom: 3rem;
    animation: fadeInDown 0.8s ease-out;
}

@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

.header-avatar-circle {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    box-shadow: 0 10px 30px rgba(47, 124, 255, 0.12);
    border: 2px solid transparent;
    background-image: linear-gradient(white, white), linear-gradient(135deg, #2F7CFF, #23D8F0);
    background-origin: border-box;
    background-clip: padding-box, border-box;
    margin-bottom: 1.2rem;
}

.header-avatar-circle::after {
    content: "";
    position: absolute;
    top: -6px; right: -6px; bottom: -6px; left: -6px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2F7CFF, #23D8F0);
    z-index: -1;
    opacity: 0.25;
    filter: blur(12px);
}

.header-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #0F172A;
    font-family: 'Sora', sans-serif;
    margin-bottom: 0.4rem;
    letter-spacing: -0.03em;
}

.header-subtitle {
    font-size: 1.05rem;
    color: #64748B;
    margin-bottom: 1.2rem;
    font-weight: 400;
}

.online-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background-color: rgba(16, 185, 129, 0.08);
    color: #059669;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.4rem 1rem;
    border-radius: 30px;
    border: 1px solid rgba(16, 185, 129, 0.15);
}

.online-dot {
    width: 8px;
    height: 8px;
    background-color: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
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
    margin-bottom: 2rem;
    width: 100%;
    animation: fadeInUp 0.5s ease-out forwards;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

.chat-row.user {
    justify-content: flex-end;
}

.chat-row.assistant {
    justify-content: flex-start;
}

.bubble-container {
    max-width: 80%;
    display: flex;
    flex-direction: column;
}

.assistant .bubble-container {
    flex-direction: row;
    align-items: flex-start;
    gap: 1rem;
}

.bubble {
    padding: 1.2rem 1.5rem;
    border-radius: 24px;
    font-size: 1.05rem;
    line-height: 1.6;
    letter-spacing: -0.01em;
}

.bubble p {
    margin: 0;
}

/* Design Premium de la Bulle Utilisateur */
.bubble.user {
    background: linear-gradient(135deg, #1E293B, #0F172A);
    color: white;
    border-bottom-right-radius: 6px;
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.15);
}

/* Design Premium de la Bulle IA */
.bubble.assistant {
    background-color: #FFFFFF;
    color: #334155;
    border-bottom-left-radius: 6px;
    border: 1px solid rgba(226, 232, 240, 0.8);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.04);
}

.assistant-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2F7CFF, #23D8F0);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 4px 15px rgba(47, 124, 255, 0.2);
}

/* Boutons de suggestions (Pilules Glassmorphism) */
div[data-testid="column"] .stButton > button {
    border-radius: 30px !important;
    border: 1px solid rgba(47, 124, 255, 0.1) !important;
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(10px) !important;
    color: #2F7CFF !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important;
}

div[data-testid="column"] .stButton > button:hover {
    background: #2F7CFF !important;
    color: white !important;
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 25px rgba(47, 124, 255, 0.2) !important;
}

/* Barre de saisie style "Îlot flottant" premium de la maquette */
div[data-testid="stChatInput"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding-bottom: 3.5rem !important;
    max-width: 750px !important;
    margin: 0 auto !important;
    position: relative !important;
}

div[data-testid="stChatInput"] > div {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(226, 232, 240, 0.9) !important;
    border-radius: 35px !important;
    box-shadow: 0 15px 35px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.03) !important;
    padding: 0.4rem 0.5rem 0.4rem 3.5rem !important;
    position: relative !important;
}

div[data-testid="stChatInput"] > div::before {
    content: "";
    position: absolute;
    left: 1.4rem;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%232F7CFF' stroke='%232F7CFF' stroke-width='0'%3E%3Cpath d='M12 2c0 5.523 4.477 10 10 10-5.523 0-10 4.477-10 10 0-5.523-4.477-10-10-10 5.523 0 10-4.477 10-10z'%3E%3C/path%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
    pointer-events: none;
}

div[data-testid="stChatInput"] textarea {
    font-size: 1rem !important;
    color: #1E293B !important;
    font-weight: 500 !important;
}

/* Cacher le contour de focus orange dégueulasse de Streamlit */
div[data-testid="stChatInput"] > div:focus-within {
    border-color: #2F7CFF !important;
    box-shadow: 0 15px 35px rgba(47, 124, 255, 0.1), 0 0 0 3px rgba(47, 124, 255, 0.15) !important;
}

/* Bouton envoyer rond avec dégradé bleu */
div[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #2F7CFF, #23D8F0) !important;
    border: none !important;
    border-radius: 50% !important;
    width: 38px !important;
    height: 38px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 4px 12px rgba(47, 124, 255, 0.3) !important;
    transition: all 0.2s ease !important;
    padding: 0 !important;
}

div[data-testid="stChatInput"] button:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 16px rgba(47, 124, 255, 0.4) !important;
}

div[data-testid="stChatInput"] button svg {
    color: white !important;
    stroke: white !important;
    fill: none !important;
    stroke-width: 2.5px !important;
}

/* Pied de page de sécurité avec cadenas */
div[data-testid="stChatInput"]::after {
    position: absolute;
    bottom: 1rem;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.8rem;
    color: #64748B;
    font-weight: 500;
    white-space: nowrap;
    display: flex;
    align-items: center;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='11' width='18' height='11' rx='2' ry='2'%3E%3C/rect%3E%3Cpath d='M7 11V7a5 5 0 0 1 10 0v4'%3E%3C/path%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: left center;
    padding-left: 1.2rem;
    content: "Vos données sont sécurisées et confidentielles.";
    pointer-events: none;
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
        font-size: 1.8rem;
    }
    
    .header-subtitle {
        font-size: 0.95rem;
    }
    
    .header-avatar-circle {
        width: 70px;
        height: 70px;
        margin-bottom: 0.8rem;
    }
    
    .bubble-container {
        max-width: 95%;
    }
    
    .assistant .bubble-container {
        gap: 0.5rem;
    }
    
    .bubble {
        padding: 1rem 1.2rem;
        font-size: 1rem;
    }
    
    .assistant-avatar {
        width: 30px;
        height: 30px;
    }
    
    div[data-testid="stChatInput"] {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        padding-bottom: 1rem !important;
    }
    
    div[data-testid="column"] .stButton > button {
        font-size: 0.85rem !important;
        padding: 0.5rem 1rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# EN-TÊTE CENTRÉ
# ============================================================
robot_face_svg = """<svg width="44" height="44" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
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
<div class="header-subtitle">Posez-moi vos questions sur la finance, je vous guide vers l'excellence.</div>
<div class="online-badge">
<span class="online-dot"></span> En ligne
</div>
</div>"""

st.markdown(html_header, unsafe_allow_html=True)

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
# HISTORIQUE (SANS ESPACES D'INDENTATION)
# ============================================================

# 1. Affichage de l'historique
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
<div class="assistant-avatar">
{get_svg_icon('robot', 20, 20, 'white')}
</div>
<div class="bubble assistant">
{content_html}
</div>
</div>
</div>"""
        st.markdown(html_msg, unsafe_allow_html=True)

# 2. Affichage conditionnel des suggestions UNIQUEMENT si le dernier message est l'accueil
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

# 3. Traitement de la réponse en cours
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    
    # Structure de chargement sans indentation
    html_loading_start = f"""<div class="chat-row assistant" style="margin-top:1rem;">
<div class="bubble-container">
<div class="assistant-avatar" style="animation: pulse 1s infinite;">
{get_svg_icon('robot', 20, 20, 'white')}
</div>
<div class="bubble assistant">"""
    
    st.markdown(html_loading_start, unsafe_allow_html=True)
    message_placeholder = st.empty()
    
    html_loading_end = """</div>
</div>
</div>
<style>@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }</style>"""
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

# ============================================================
# ENTREE UTILISATEUR
# ============================================================
prompt = st.chat_input("Posez une question ou tapez un mot-clé...")

if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Espacement dynamique pour pousser la page vers le haut et éviter que 
# la barre de saisie fixe (st.chat_input) ne cache le dernier message.
st.markdown("<div style='height: 150px; width: 100%;'></div>", unsafe_allow_html=True)
