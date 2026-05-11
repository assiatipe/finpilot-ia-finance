import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import init_auth_state, logout
from database import (
    init_db,
    get_user_cash_balance,
    is_user_admin,
    admin_get_all_users,
    admin_get_user_orders,
    admin_get_user_analyses,
    admin_delete_user,
    admin_delete_feedback,
    admin_get_global_stats,
    get_all_feedbacks,
    get_feedback_stats,
)
from styles import load_global_styles
from sidebar_ui import render_sidebar

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="FinPilot · Admin",
    page_icon="assets/finpilot_logo_final.png",
    layout="wide",
)

init_db()
init_auth_state()
st.markdown(load_global_styles(), unsafe_allow_html=True)

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
    st.stop()

user_id = st.session_state.user_id

if not is_user_admin(user_id):
    st.error("⛔ Accès refusé. Cette page est réservée aux administrateurs.")
    st.stop()

cash_balance = get_user_cash_balance(user_id)
render_sidebar(active_page="admin", cash_balance=cash_balance, logout_callback=logout)


# ============================================================
# STYLES LOCAUX
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');

.adm-hero {
    position: relative;
    overflow: hidden;
    padding: 2.2rem 2.5rem;
    border-radius: 28px;
    color: white;
    background:
        radial-gradient(circle at 90% 18%, rgba(239,68,68,.45), transparent 26%),
        radial-gradient(circle at 10% 80%, rgba(122,92,255,.35), transparent 26%),
        linear-gradient(120deg, #0B0F1A 0%, #1A1040 50%, #2D1B6E 100%);
    box-shadow: 0 20px 55px rgba(0,0,0,.30);
    margin-bottom: 1.5rem;
}
.adm-hero-label {
    color: #F87171;
    font-size: .82rem;
    font-weight: 900;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: .6rem;
}
.adm-hero-title {
    font-family: 'Sora', sans-serif;
    font-size: 2.5rem;
    font-weight: 900;
    letter-spacing: -.04em;
    line-height: 1.1;
    margin-bottom: .7rem;
}
.adm-hero-sub {
    color: rgba(255,255,255,.80);
    font-size: 1rem;
    line-height: 1.7;
}

.adm-kpi {
    background: #FFFFFF;
    border: 1px solid #DCE7F8;
    border-radius: 20px;
    padding: 1.3rem 1.4rem;
    box-shadow: 0 8px 24px rgba(22,46,90,.07);
    text-align: center;
}
.adm-kpi-value {
    font-family: 'Sora', sans-serif;
    font-size: 2rem;
    font-weight: 900;
    color: #10233F;
    line-height: 1.1;
}
.adm-kpi-label {
    color: #64748B;
    font-size: .84rem;
    margin-top: .3rem;
}
.adm-kpi-accent {
    color: #2F7CFF;
}

.adm-card {
    background: #FFFFFF;
    border: 1px solid #DCE7F8;
    border-radius: 22px;
    padding: 1.5rem 1.7rem;
    box-shadow: 0 10px 32px rgba(22,46,90,.07);
    margin-bottom: 1rem;
}
.adm-card-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    color: #10233F;
    margin-bottom: .35rem;
}
.adm-card-sub {
    color: #64748B;
    font-size: .92rem;
    margin-bottom: 1rem;
}

.user-row {
    display: grid;
    grid-template-columns: 1fr 1.4fr 90px 70px 70px 70px 80px;
    gap: .6rem;
    align-items: center;
    padding: .85rem 1rem;
    border-bottom: 1px solid #EEF4FF;
    font-size: .9rem;
}
.user-row-header {
    background: #F4F8FF;
    border-radius: 12px 12px 0 0;
    color: #617693;
    font-size: .78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .05em;
}
.user-row:last-child { border-bottom: none; }

.pill {
    display: inline-block;
    padding: .28rem .6rem;
    border-radius: 999px;
    font-size: .76rem;
    font-weight: 800;
}
.pill-blue  { background:#EAF2FF; color:#2F7CFF; border:1px solid #CFE0FF; }
.pill-green { background:#E9FBF5; color:#1C9C73; border:1px solid #C5F3E1; }
.pill-red   { background:#FFECEE; color:#D44D61; border:1px solid #F7CBD3; }
.pill-gold  { background:#FFF7E6; color:#A56A00; border:1px solid #F6DEAA; }
.pill-purple{ background:#F3EEFF; color:#7A5CFF; border:1px solid #D9CCFF; }

.fb-row {
    background: #F8FBFF;
    border: 1px solid #E2EDF8;
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: .65rem;
}
.fb-row-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: .4rem;
    flex-wrap: wrap;
    gap: .4rem;
}
.fb-stars { color: #F59E0B; font-size: 1rem; }
.fb-msg   { color: #334155; font-size: .92rem; line-height: 1.65; margin-top: .3rem; }
.fb-meta  { color: #94A3B8; font-size: .80rem; }

.order-chip {
    display: inline-block;
    padding: .22rem .55rem;
    border-radius: 8px;
    font-size: .78rem;
    font-weight: 800;
}
.order-buy  { background:#E9FBF5; color:#1C9C73; }
.order-sell { background:#FFECEE; color:#D44D61; }

.section-divider {
    border: none;
    border-top: 1px solid #EEF4FF;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================

def stars(n):
    n = int(n or 0)
    return "★" * n + "☆" * (5 - n)

def profile_pill(p):
    colors = {"Prudent": "pill-green", "Modéré": "pill-blue", "Dynamique": "pill-gold"}
    return f'<span class="pill {colors.get(p, "pill-blue")}">{p}</span>'

def fmt_money(v):
    try:
        return f"${float(v):,.0f}"
    except Exception:
        return "—"

def fmt_date(d):
    return str(d or "")[:16].replace("T", " ")


# ============================================================
# HERO
# ============================================================

st.markdown(f"""
<div class="adm-hero">
    <div class="adm-hero-label">⚙ Espace Administration</div>
    <div class="adm-hero-title">Tableau de bord Admin</div>
    <div class="adm-hero-sub">
        Connecté en tant que <b>{st.session_state.get('user_name', 'Admin')}</b> ·
        Supervision complète de la plateforme FinPilot.
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# KPI GLOBAUX
# ============================================================

gstats = admin_get_global_stats()

k1, k2, k3, k4, k5, k6 = st.columns(6)
kpis = [
    ("Utilisateurs", str(gstats["nb_users"]), ""),
    ("Ordres simulés", str(gstats["nb_orders"]), ""),
    ("Analyses IA", str(gstats["nb_analyses"]), ""),
    ("Avis déposés", str(gstats["nb_feedbacks"]), ""),
    ("Volume simulé", fmt_money(gstats["volume_total"]), "adm-kpi-accent"),
    ("Note moyenne", f"{gstats['avg_rating']:.1f} / 5", ""),
]
for col, (label, val, css) in zip([k1, k2, k3, k4, k5, k6], kpis):
    with col:
        st.markdown(f"""
        <div class="adm-kpi">
            <div class="adm-kpi-value {css}">{val}</div>
            <div class="adm-kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)


# ============================================================
# TABS
# ============================================================

tab_users, tab_feedbacks = st.tabs(["👥  Utilisateurs", "💬  Avis clients"])


# ============================================================
# TAB 1 — UTILISATEURS
# ============================================================

with tab_users:
    all_users = admin_get_all_users()

    st.markdown(f"""
    <div class="adm-card">
        <div class="adm-card-title">Tous les utilisateurs ({len(all_users)})</div>
        <div class="adm-card-sub">Cliquez sur un utilisateur pour voir le détail de son activité.</div>
    </div>
    """, unsafe_allow_html=True)

    # En-tête tableau
    st.markdown("""
    <div class="user-row user-row-header">
        <div>Nom</div>
        <div>Email</div>
        <div>Profil</div>
        <div>Ordres</div>
        <div>Analyses</div>
        <div>Avis</div>
        <div>Capital</div>
    </div>
    """, unsafe_allow_html=True)

    for u in all_users:
        uid       = u.get("id")
        uname     = u.get("username", "—")
        email     = u.get("email", "—")
        profil    = u.get("profile", "Modéré")
        nb_ord    = u.get("nb_orders", 0)
        nb_ana    = u.get("nb_analyses", 0)
        nb_fb     = u.get("nb_feedbacks", 0)
        capital   = u.get("initial_capital")
        cash      = u.get("cash_balance")
        is_adm    = int(u.get("is_admin", 0) or 0)
        badge     = ' <span class="pill pill-red">Admin</span>' if is_adm else ""

        st.markdown(f"""
        <div class="user-row">
            <div><b>{uname}</b>{badge}</div>
            <div style="color:#64748B;font-size:.85rem;">{email}</div>
            <div>{profile_pill(profil)}</div>
            <div style="text-align:center;font-weight:700;">{nb_ord}</div>
            <div style="text-align:center;font-weight:700;">{nb_ana}</div>
            <div style="text-align:center;font-weight:700;">{nb_fb}</div>
            <div style="font-size:.85rem;">{fmt_money(capital)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── DÉTAIL UTILISATEUR ──────────────────────────────────────────────
    st.markdown("""
    <div class="adm-card">
        <div class="adm-card-title">Détail d'un utilisateur</div>
        <div class="adm-card-sub">Sélectionnez un utilisateur pour voir ses ordres et analyses.</div>
    </div>
    """, unsafe_allow_html=True)

    user_options = {f"{u['username']} ({u['email']})": u["id"] for u in all_users}
    selected_label = st.selectbox("Choisir un utilisateur", options=list(user_options.keys()), index=0)
    selected_uid = user_options[selected_label]
    selected_user = next(u for u in all_users if u["id"] == selected_uid)

    col_info, col_actions = st.columns([2, 1], gap="large")

    with col_info:
        # Infos générales
        st.markdown(f"""
        <div class="adm-card">
            <div class="adm-card-title">{selected_user['username']}</div>
            <div style="color:#64748B;margin-bottom:.8rem;">{selected_user['email']}</div>
            <div style="display:flex;gap:.6rem;flex-wrap:wrap;">
                {profile_pill(selected_user.get('profile','Modéré'))}
                <span class="pill pill-blue">Capital initial : {fmt_money(selected_user.get('initial_capital'))}</span>
                <span class="pill pill-green">Cash actuel : {fmt_money(selected_user.get('cash_balance'))}</span>
                <span class="pill pill-purple">Inscrit le {fmt_date(selected_user.get('created_at'))}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Ordres
        orders = admin_get_user_orders(selected_uid)
        with st.expander(f"📋 Ordres ({len(orders)})", expanded=True):
            if not orders:
                st.caption("Aucun ordre enregistré.")
            else:
                for o in orders:
                    otype = o.get("order_type", "")
                    label_cls = "order-buy" if otype == "BUY" else "order-sell"
                    label_txt = "Achat" if otype == "BUY" else "Vente"
                    st.markdown(f"""
                    <div style="padding:.55rem 0;border-bottom:1px solid #EEF4FF;">
                        <span class="order-chip {label_cls}">{label_txt}</span>
                        <b style="margin-left:.5rem;">{o.get('ticker','')}</b>
                        · Qté : <b>{float(o.get('quantity',0)):.2f}</b>
                        · Prix : <b>{fmt_money(o.get('price'))}</b>
                        · Total : <b>{fmt_money(o.get('total'))}</b>
                        <span style="color:#94A3B8;font-size:.82rem;float:right;">{fmt_date(o.get('created_at'))}</span>
                    </div>
                    """, unsafe_allow_html=True)

        # Analyses
        analyses = admin_get_user_analyses(selected_uid)
        with st.expander(f"🧠 Analyses IA ({len(analyses)})", expanded=False):
            if not analyses:
                st.caption("Aucune analyse enregistrée.")
            else:
                for a in analyses:
                    tickers = a.get("recommended_tickers", "") or "—"
                    st.markdown(f"""
                    <div style="padding:.55rem 0;border-bottom:1px solid #EEF4FF;">
                        {profile_pill(a.get('profil','Modéré'))}
                        · Score : <b>{a.get('score','—')}/100</b>
                        · Actions : <b>{tickers}</b>
                        <span style="color:#94A3B8;font-size:.82rem;float:right;">{fmt_date(a.get('created_at'))}</span>
                    </div>
                    """, unsafe_allow_html=True)

    with col_actions:
        st.markdown("""
        <div class="adm-card">
            <div class="adm-card-title">Actions</div>
            <div class="adm-card-sub">Opérations irréversibles sur ce compte.</div>
        </div>
        """, unsafe_allow_html=True)

        # Bloquer suppression de soi-même
        is_self = (selected_uid == user_id)
        is_target_admin = int(selected_user.get("is_admin", 0) or 0) == 1

        if is_self:
            st.warning("Vous ne pouvez pas supprimer votre propre compte.")
        elif is_target_admin:
            st.warning("Impossible de supprimer un autre compte admin.")
        else:
            st.markdown(f"""
            <div style="background:#FFF1F2;border:1px solid #FECDD3;border-radius:16px;
                        padding:1rem 1.2rem;margin-bottom:.8rem;">
                <div style="color:#BE123C;font-weight:800;margin-bottom:.35rem;">⚠ Supprimer ce compte</div>
                <div style="color:#9F1239;font-size:.88rem;line-height:1.5;">
                    Supprime définitivement <b>{selected_user['username']}</b>,
                    tous ses ordres, analyses, avis et positions.
                </div>
            </div>
            """, unsafe_allow_html=True)

            confirm_key = f"confirm_delete_{selected_uid}"
            confirm = st.checkbox("Je confirme la suppression", key=confirm_key)

            if st.button(
                "🗑 Supprimer ce compte",
                type="primary",
                use_container_width=True,
                disabled=not confirm,
                key=f"btn_delete_{selected_uid}",
            ):
                admin_delete_user(selected_uid)
                st.success(f"Compte {selected_user['username']} supprimé.")
                st.rerun()


# ============================================================
# TAB 2 — AVIS
# ============================================================

with tab_feedbacks:
    fb_stats = get_feedback_stats()
    all_fbs  = get_all_feedbacks()

    # Stats rapides
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="adm-kpi">
            <div class="adm-kpi-value">{fb_stats['avg_rating']:.1f} / 5</div>
            <div class="adm-kpi-label">Note moyenne</div>
            <div style="color:#F59E0B;font-size:1.1rem;margin-top:.3rem;">{stars(round(fb_stats['avg_rating']))}</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="adm-kpi">
            <div class="adm-kpi-value">{fb_stats['total']}</div>
            <div class="adm-kpi-label">Avis au total</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        top_cat = list(fb_stats["by_category"].keys())[0] if fb_stats["by_category"] else "—"
        st.markdown(f"""
        <div class="adm-kpi">
            <div class="adm-kpi-value" style="font-size:1.3rem;">{top_cat}</div>
            <div class="adm-kpi-label">Catégorie dominante</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Filtres
    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        filter_rating = st.selectbox(
            "Filtrer par note",
            options=["Toutes", "5 ★", "4 ★", "3 ★", "2 ★", "1 ★"],
            index=0,
        )
    with col_f2:
        categories_present = ["Toutes"] + sorted(set(f.get("category","") for f in all_fbs if f.get("category")))
        filter_cat = st.selectbox("Filtrer par catégorie", options=categories_present, index=0)

    # Application des filtres
    filtered = all_fbs
    if filter_rating != "Toutes":
        note_val = int(filter_rating[0])
        filtered = [f for f in filtered if int(f.get("rating", 0)) == note_val]
    if filter_cat != "Toutes":
        filtered = [f for f in filtered if f.get("category") == filter_cat]

    st.markdown(f"""
    <div class="adm-card">
        <div class="adm-card-title">Avis clients ({len(filtered)})</div>
        <div class="adm-card-sub">Tous les retours soumis par les utilisateurs après simulation.</div>
    </div>
    """, unsafe_allow_html=True)

    if not filtered:
        st.info("Aucun avis ne correspond aux filtres sélectionnés.")
    else:
        for fb in filtered:
            fb_id    = fb.get("id")
            note     = int(fb.get("rating", 3))
            cat      = fb.get("category", "Général")
            msg      = fb.get("message", "")
            uname    = fb.get("username", "—")
            email    = fb.get("email", "—")
            date_str = fmt_date(fb.get("created_at"))

            col_fb, col_del = st.columns([10, 1])
            with col_fb:
                st.markdown(f"""
                <div class="fb-row">
                    <div class="fb-row-header">
                        <div style="display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;">
                            <span class="fb-stars">{stars(note)}</span>
                            <span class="pill pill-blue">{cat}</span>
                            <span class="pill pill-purple">{uname}</span>
                            <span class="fb-meta">{email}</span>
                        </div>
                        <div class="fb-meta">{date_str}</div>
                    </div>
                    <div class="fb-msg">{msg}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                if st.button("🗑", key=f"del_fb_{fb_id}", help="Supprimer cet avis"):
                    admin_delete_feedback(fb_id)
                    st.rerun()