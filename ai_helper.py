import time
import re
from database import get_user_cash_balance, get_portfolio_positions

def _generate_portfolio_analysis(user_id: int) -> str:
    try:
        cash = get_user_cash_balance(user_id)
        positions = get_portfolio_positions(user_id)
    except Exception:
        cash = 0.0
        positions = []
        
    if not positions:
        return f"J'ai analysé votre compte. Vous n'avez actuellement aucune action dans votre portefeuille. Votre solde disponible pour la simulation est de **{cash:,.2f} $**.\n\nJe vous conseille de commencer par utiliser l'onglet **Analyse IA** pour découvrir des actions solides adaptées à votre profil de risque, puis de passer un ordre d'achat fictif."

    analysis = f"Voici l'analyse de votre portefeuille actuel :\n\nVous disposez de **{cash:,.2f} $** en liquidités.\n\n**Vos positions :**\n"
    total_invested = 0
    for pos in positions:
        ticker, company_name, qty, avg_price = pos
        valeur = qty * avg_price
        total_invested += valeur
        analysis += f"- **{company_name} ({ticker})** : {qty} actions achetées à {avg_price}$ (Valeur approx: {valeur:,.2f}$)\n"
    
    analysis += f"\n**Total investi :** ~{total_invested:,.2f} $\n\n"
    analysis += "Conseil expert : Assurez-vous que vos investissements soient diversifiés sur au moins 3 ou 4 secteurs différents (ex: technologie, santé, énergie) pour limiter la volatilité."
    return analysis

def _generate_market_news() -> str:
    return """Voici les grandes tendances du marché aujourd'hui :

- **Le secteur Technologique (IA et Cloud)** continue de porter les indices américains à la hausse, avec une très forte demande en semi-conducteurs.
- **La Santé et l'Énergie** restent des secteurs défensifs solides face aux incertitudes sur les taux d'intérêt.
- **Inflation et Taux** : Les banques centrales maintiennent une politique de prudence, ce qui profite généralement aux actions ayant des flux de trésorerie stables.

*Note de marché : Si vous cherchez à investir, l'IA et la transition énergétique restent d'excellents paris à long terme, mais veillez à la surévaluation de certaines valeurs tech.*"""

def _generate_beginner_guide() -> str:
    return """Bienvenue dans FinPilot ! Puisque vous débutez, voici la marche à suivre pas-à-pas pour prendre l'application en main sans stress :

1. **Remplir votre Profil (Analyse IA)** : Allez dans l'onglet *Analyse IA* et répondez au questionnaire. L'application va détecter votre profil (prudent, dynamique...) et vous proposer un "Top 5" des meilleures actions pour vous.
2. **Passer votre premier Ordre** : Depuis ce même Top 5, vous pourrez cliquer sur "Achat" pour ajouter une action à votre portefeuille virtuel en utilisant votre capital de départ de 10 000 $.
3. **Suivre vos gains (Portefeuille)** : Allez dans l'onglet *Portefeuille* pour voir l'évolution de vos actions et de vos bénéfices. Vous pourrez aussi y revendre vos actions quand vous le souhaiterez.

N'ayez pas peur de tester, c'est une plateforme de **simulation**. Vous ne risquez pas de vrai argent !"""

def _generate_investment_ideas() -> str:
    return """Voici quelques idées de secteurs rentables et solides pour débuter :

1. **Les Semi-conducteurs et l'IA** (ex: NVIDIA, Microsoft) : Croissance explosive, mais parfois volatile.
2. **La Santé** (ex: Johnson & Johnson, Pfizer) : Un secteur défensif qui résiste très bien aux crises économiques.
3. **L'Énergie et Services Publics** : Utiles pour toucher des dividendes réguliers avec très peu de risques.
4. **La Consommation de Base** (ex: Coca-Cola, Walmart) : Des entreprises dont on aura toujours besoin, même en récession.

Je vous recommande de mixer 1 action de croissance (Tech) avec 2 actions défensives (Santé/Consommation) pour commencer un portefeuille équilibré."""

def _generate_fallback(prompt: str) -> str:
    # Si c'est un simple mot
    if len(prompt) < 3:
        return "Je suis à votre écoute ! Que souhaitez-vous faire ?"
        
    return """Je n'ai pas bien saisi votre demande. Étant un assistant de simulation 100% local, mes connaissances sont ciblées. 

**Sur quoi souhaitez-vous que l'on discute ?**
- **Votre portefeuille** (tapez "portefeuille")
- **Les actualités du marché** (tapez "actualité")
- **Des idées d'investissement** (tapez "idées")
- **Comment utiliser l'application** (tapez "débutant")

*Vous pouvez aussi me donner le nom d'une action connue (ex: Apple, Tesla, Coca-Cola) pour une analyse rapide !*"""

def _generate_greeting() -> str:
    return "Bonjour ! Je suis ravi de vous parler. En tant qu'expert FinPilot, je peux vous aider à analyser vos investissements ou vous guider sur les marchés. Que choisissez-vous : Analyse de portefeuille, ou Actualités du jour ?"

def _generate_thanks() -> str:
    return "Je vous en prie ! C'est un plaisir de vous aider. N'hésitez pas si vous souhaitez explorer d'autres secteurs ou analyser de nouvelles actions."

def _generate_stock_analysis(stock: str) -> str:
    stock = stock.capitalize()
    return f"""**Analyse rapide de {stock} :**

C'est une entreprise très suivie par les investisseurs de FinPilot. 
- **Type d'action** : Généralement considérée comme une valeur de fond de portefeuille (si c'est une grande marque) ou de croissance (si c'est la tech).
- **Conseil IA** : Avant d'investir dans {stock}, vérifiez toujours ses derniers résultats trimestriels et son niveau d'endettement. 

Voulez-vous que je l'ajoute virtuellement à votre liste de surveillance ?"""

def get_chat_response(messages, user_id, username):
    """
    Génère une réponse simulée en lisant les derniers messages
    et en analysant le texte de l'utilisateur par mots-clés.
    Simule également un stream (Yield).
    """
    
    # On récupère la dernière question de l'utilisateur
    last_user_msg = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            last_user_msg = msg["content"].lower().strip()
            break
            
    # Moteur de règles étendu
    if last_user_msg in ["bonjour", "salut", "hello", "coucou", "yo", "bonsoir"]:
        response_text = _generate_greeting()
    elif last_user_msg in ["merci", "merci beaucoup", "ok", "super", "top", "d'accord", "compris"]:
        response_text = _generate_thanks()
    elif "portefeuille" in last_user_msg or "position" in last_user_msg or "mes actions" in last_user_msg:
        response_text = _generate_portfolio_analysis(user_id)
    elif "actualit" in last_user_msg or "tendance" in last_user_msg or "marché" in last_user_msg or "marche" in last_user_msg:
        response_text = _generate_market_news()
    elif "débutant" in last_user_msg or "debutant" in last_user_msg or "comment utiliser" in last_user_msg or "app" in last_user_msg:
        response_text = _generate_beginner_guide()
    elif "idée" in last_user_msg or "idee" in last_user_msg or "secteur" in last_user_msg or "investir" in last_user_msg:
        response_text = _generate_investment_ideas()
    elif "coca" in last_user_msg or "coca-cola" in last_user_msg:
        response_text = _generate_stock_analysis("Coca-Cola")
    elif "apple" in last_user_msg:
        response_text = _generate_stock_analysis("Apple")
    elif "tesla" in last_user_msg:
        response_text = _generate_stock_analysis("Tesla")
    elif "nvidia" in last_user_msg or "ia" in last_user_msg:
        if "ia" in last_user_msg and len(last_user_msg) < 5:
            response_text = _generate_stock_analysis("NVIDIA (Secteur IA)")
        else:
            response_text = _generate_fallback(last_user_msg)
    else:
        response_text = _generate_fallback(last_user_msg)
        
    # Simulation du délai de réflexion réseau
    time.sleep(0.5)
    
    # Simulation du streaming
    words = response_text.split(" ")
    for word in words:
        yield word + " "
        time.sleep(0.02) # Effet machine à écrire fluide
