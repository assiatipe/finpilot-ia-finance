import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finpilot.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row) -> dict:
    if row is None:
        return {}
    return {key: row[key] for key in row.keys()}


def _column_exists(cursor, table_name, column_name):
    columns = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(col["name"] == column_name for col in columns)


def _add_column_if_missing(cursor, table_name, column_name, column_sql):
    if not _column_exists(cursor, table_name, column_name):
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}")


def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        cash_balance REAL DEFAULT NULL,
        initial_capital REAL DEFAULT NULL,
        capital_configured INTEGER DEFAULT 0,
        profile TEXT DEFAULT 'Modéré',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    _add_column_if_missing(c, "users", "initial_capital", "REAL DEFAULT NULL")
    _add_column_if_missing(c, "users", "capital_configured", "INTEGER DEFAULT 0")
    _add_column_if_missing(c, "users", "is_admin", "INTEGER DEFAULT 0")
    _add_column_if_missing(c, "users", "profile", "TEXT DEFAULT 'Modéré'")

    c.execute("""CREATE TABLE IF NOT EXISTS portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        ticker TEXT NOT NULL,
        company_name TEXT NOT NULL,
        quantity REAL NOT NULL DEFAULT 0,
        avg_buy_price REAL NOT NULL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(user_id, ticker)
    )""")

    _add_column_if_missing(c, "portfolio", "company_name", "TEXT DEFAULT ''")
    _add_column_if_missing(c, "portfolio", "avg_buy_price", "REAL DEFAULT 0")

    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        ticker TEXT NOT NULL,
        order_type TEXT NOT NULL,
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        total REAL NOT NULL,
        cash_after REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")

    _add_column_if_missing(c, "orders", "order_type", "TEXT DEFAULT 'BUY'")
    _add_column_if_missing(c, "orders", "total", "REAL DEFAULT 0")
    _add_column_if_missing(c, "orders", "cash_after", "REAL DEFAULT 0")

    c.execute("""CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        profil TEXT NOT NULL,
        score INTEGER NOT NULL,
        recommended_tickers TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")

    _add_column_if_missing(c, "analyses", "recommended_tickers", "TEXT")
    _add_column_if_missing(c, "analyses", "notes", "TEXT")

    c.execute("""CREATE TABLE IF NOT EXISTS watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        ticker TEXT NOT NULL,
        company_name TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(user_id, ticker)
    )""")

    # ── TABLE FEEDBACKS ───────────────────────────────────────────────────────
    c.execute("""CREATE TABLE IF NOT EXISTS feedbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
        category TEXT NOT NULL DEFAULT 'Général',
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")

    _add_column_if_missing(c, "feedbacks", "category", "TEXT DEFAULT 'Général'")
    _add_column_if_missing(c, "feedbacks", "message", "TEXT DEFAULT ''")
    _add_column_if_missing(c, "feedbacks", "created_at", "TEXT")
    _add_column_if_missing(c, "orders", "created_at", "TEXT")
    _add_column_if_missing(c, "analyses", "created_at", "TEXT")
    _add_column_if_missing(c, "users", "cash_balance", "REAL DEFAULT NULL")

    conn.commit()
    conn.close()


def create_user(username, email, password_hash):
    """
    Création d'un utilisateur sans capital automatique.
    Le capital sera demandé dans l'écran d'accueil après connexion.
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, email, password_hash, cash_balance, initial_capital, capital_configured) "
            "VALUES (?, ?, ?, NULL, NULL, 0)",
            (username, email, password_hash)
        )
        conn.commit()
        uid = c.lastrowid
        conn.close()
        return uid
    except Exception:
        return None


def get_user_by_email(email):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    result = row_to_dict(row) if row else None
    conn.close()
    return result


def get_user_by_id(user_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    result = row_to_dict(row) if row else None
    conn.close()
    return result


def has_user_capital_configured(user_id):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT capital_configured FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()

    if not row:
        return False

    return int(row["capital_configured"] or 0) == 1


def get_user_initial_capital(user_id):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT initial_capital FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()

    if not row or row["initial_capital"] is None:
        return 0.0

    return float(row["initial_capital"])


def set_user_initial_capital(user_id, amount, reset_portfolio=True):
    amount = float(amount)

    if amount <= 0:
        raise ValueError("Le capital initial doit être strictement positif.")

    conn = get_db_connection()

    if reset_portfolio:
        conn.execute("DELETE FROM orders WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM portfolio WHERE user_id = ?", (user_id,))

    conn.execute(
        "UPDATE users SET initial_capital = ?, cash_balance = ?, capital_configured = 1 WHERE id = ?",
        (amount, amount, user_id)
    )

    conn.commit()
    conn.close()


def reset_user_portfolio(user_id, new_capital=None):
    if new_capital is None:
        new_capital = get_user_initial_capital(user_id)

    new_capital = float(new_capital)

    if new_capital <= 0:
        raise ValueError("Capital invalide.")

    conn = get_db_connection()
    conn.execute("DELETE FROM orders WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM portfolio WHERE user_id = ?", (user_id,))
    conn.execute(
        "UPDATE users SET initial_capital = ?, cash_balance = ?, capital_configured = 1 WHERE id = ?",
        (new_capital, new_capital, user_id)
    )
    conn.commit()
    conn.close()


def get_user_cash_balance(user_id):
    conn = get_db_connection()
    row = conn.execute("SELECT cash_balance FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    if not row or row["cash_balance"] is None:
        return 0.0

    return float(row["cash_balance"])


def update_cash_balance(user_id, new_balance):
    conn = get_db_connection()
    conn.execute("UPDATE users SET cash_balance = ? WHERE id = ?", (float(new_balance), user_id))
    conn.commit()
    conn.close()


def get_portfolio_positions(user_id):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT ticker, company_name, quantity, avg_buy_price FROM portfolio WHERE user_id = ? AND quantity > 0",
        (user_id,)
    ).fetchall()
    result = [(r["ticker"], r["company_name"], r["quantity"], r["avg_buy_price"]) for r in rows]
    conn.close()
    return result


def upsert_portfolio_position(user_id, ticker, company_name, qty, avg_price):
    conn = get_db_connection()
    existing = conn.execute(
        "SELECT quantity, avg_buy_price FROM portfolio WHERE user_id = ? AND ticker = ?",
        (user_id, ticker)
    ).fetchone()

    if existing:
        old_qty = float(existing["quantity"])
        old_avg = float(existing["avg_buy_price"])
        new_qty = old_qty + float(qty)

        if new_qty <= 0:
            conn.execute("DELETE FROM portfolio WHERE user_id = ? AND ticker = ?", (user_id, ticker))
        else:
            new_avg = ((old_qty * old_avg) + (float(qty) * float(avg_price))) / new_qty if qty > 0 else old_avg
            conn.execute(
                "UPDATE portfolio SET quantity = ?, avg_buy_price = ? WHERE user_id = ? AND ticker = ?",
                (new_qty, new_avg, user_id, ticker)
            )
    else:
        if qty > 0:
            conn.execute(
                "INSERT INTO portfolio (user_id, ticker, company_name, quantity, avg_buy_price) VALUES (?, ?, ?, ?, ?)",
                (user_id, ticker, company_name, float(qty), float(avg_price))
            )

    conn.commit()
    conn.close()


def add_order(user_id, ticker, order_type, qty, price, total, cash_after):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO orders (user_id, ticker, order_type, quantity, price, total, cash_after) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, ticker, order_type, float(qty), float(price), float(total), float(cash_after))
    )
    conn.commit()
    conn.close()


def get_user_orders(user_id):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, user_id, ticker, order_type, quantity, price, total, cash_after, created_at "
        "FROM orders WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    result = [row_to_dict(r) for r in rows]
    conn.close()
    return result


def save_analysis(user_id, profil, score, recommended_tickers="", notes=""):
    """
    Sauvegarde une analyse IA dans l'historique.

    Paramètres attendus :
    - user_id : identifiant utilisateur
    - profil : Prudent / Modéré / Dynamique
    - score : score du questionnaire
    - recommended_tickers : texte ou liste des tickers recommandés
    - notes : détails complémentaires affichables dans l'historique
    """
    if isinstance(recommended_tickers, (list, tuple, set)):
        recommended_tickers = ", ".join(str(t).strip() for t in recommended_tickers if str(t).strip())

    recommended_tickers = str(recommended_tickers or "").strip()
    notes = str(notes or "").strip()

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO analyses (user_id, profil, score, recommended_tickers, notes) VALUES (?, ?, ?, ?, ?)",
        (user_id, profil, int(score), recommended_tickers, notes)
    )
    conn.execute("UPDATE users SET profile = ? WHERE id = ?", (profil, user_id))
    conn.commit()
    conn.close()


def load_user_history(user_id):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, user_id, profil, score, recommended_tickers, notes, created_at "
        "FROM analyses WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    result = [row_to_dict(r) for r in rows]
    conn.close()
    return result


def load_user_recommended_actions(user_id):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT recommended_tickers FROM analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    result = []

    if row and row["recommended_tickers"]:
        tickers = row["recommended_tickers"].split(",")
        result = [{"ticker": t.strip()} for t in tickers if t.strip()]

    conn.close()
    return result


def get_watchlist(user_id):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT ticker, company_name FROM watchlist WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    result = [row_to_dict(r) for r in rows]
    conn.close()
    return result


def add_to_watchlist(user_id, ticker, company_name):
    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT OR IGNORE INTO watchlist (user_id, ticker, company_name) VALUES (?, ?, ?)",
            (user_id, ticker, company_name)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


# =============================================================================
# FEEDBACKS
# =============================================================================

FEEDBACK_CATEGORIES = [
    "Général",
    "Interface",
    "Analyse IA",
    "Simulation",
    "Portefeuille",
    "Performance",
    "Suggestion",
]


def save_feedback(user_id: int, rating: int, category: str, message: str) -> bool:
    """
    Enregistre un avis utilisateur.
    Retourne True si l'insertion a réussi, False sinon.
    """
    if not (1 <= rating <= 5):
        return False
    if not message or not message.strip():
        return False

    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO feedbacks (user_id, rating, category, message) VALUES (?, ?, ?, ?)",
            (user_id, int(rating), category.strip(), message.strip())
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def get_user_feedbacks(user_id: int) -> list:
    """Retourne tous les avis d'un utilisateur, du plus récent au plus ancien."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, rating, category, message, created_at FROM feedbacks "
        "WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    result = [row_to_dict(r) for r in rows]
    conn.close()
    return result


def get_all_feedbacks() -> list:
    """
    Retourne tous les avis de tous les utilisateurs (usage admin).
    Joint avec la table users pour afficher le nom.
    """
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT f.id, f.rating, f.category, f.message, f.created_at,
               u.username, u.email
        FROM feedbacks f
        JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
        """
    ).fetchall()
    result = [row_to_dict(r) for r in rows]
    conn.close()
    return result


def get_feedback_stats() -> dict:
    """
    Retourne des statistiques agrégées sur les avis :
    - note moyenne globale
    - nombre total d'avis
    - répartition par note (1 à 5)
    - répartition par catégorie
    """
    conn = get_db_connection()

    row = conn.execute(
        "SELECT COUNT(*) as total, AVG(rating) as avg_rating FROM feedbacks"
    ).fetchone()

    total = int(row["total"] or 0)
    avg_rating = round(float(row["avg_rating"] or 0), 2)

    dist_rows = conn.execute(
        "SELECT rating, COUNT(*) as cnt FROM feedbacks GROUP BY rating ORDER BY rating"
    ).fetchall()
    distribution = {str(r["rating"]): int(r["cnt"]) for r in dist_rows}

    cat_rows = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM feedbacks GROUP BY category ORDER BY cnt DESC"
    ).fetchall()
    by_category = {r["category"]: int(r["cnt"]) for r in cat_rows}

    conn.close()

    return {
        "total": total,
        "avg_rating": avg_rating,
        "distribution": distribution,
        "by_category": by_category,
    }


def user_has_given_feedback_today(user_id: int) -> bool:
    """
    Vérifie si l'utilisateur a déjà soumis un avis aujourd'hui
    (limite anti-spam : 1 avis par jour).
    """
    conn = get_db_connection()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM feedbacks "
        "WHERE user_id = ? AND DATE(created_at) = DATE('now')",
        (user_id,)
    ).fetchone()
    conn.close()
    return int(row["cnt"] or 0) > 0


# =============================================================================
# ADMIN
# =============================================================================

def is_user_admin(user_id: int) -> bool:
    """Retourne True si l'utilisateur est admin."""
    conn = get_db_connection()
    row = conn.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if not row:
        return False
    return int(row["is_admin"] or 0) == 1


def set_user_admin(user_id: int, admin: bool = True):
    """Accorde ou retire les droits admin à un utilisateur."""
    conn = get_db_connection()
    conn.execute("UPDATE users SET is_admin = ? WHERE id = ?", (1 if admin else 0, user_id))
    conn.commit()
    conn.close()


def admin_get_all_users() -> list:
    """
    Retourne tous les utilisateurs avec leurs statistiques :
    nombre d'ordres, nombre d'analyses, nombre d'avis, capital initial, cash actuel.
    """
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT
            u.id,
            u.username,
            u.email,
            u.profile,
            u.cash_balance,
            u.initial_capital,
            u.capital_configured,
            u.is_admin,
            u.created_at,
            COUNT(DISTINCT o.id)  AS nb_orders,
            COUNT(DISTINCT a.id)  AS nb_analyses,
            COUNT(DISTINCT f.id)  AS nb_feedbacks
        FROM users u
        LEFT JOIN orders    o ON o.user_id = u.id
        LEFT JOIN analyses  a ON a.user_id = u.id
        LEFT JOIN feedbacks f ON f.user_id = u.id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """).fetchall()
    result = [row_to_dict(r) for r in rows]
    conn.close()
    return result


def admin_get_user_orders(user_id: int) -> list:
    """Retourne tous les ordres d'un utilisateur donné."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT ticker, order_type, quantity, price, total, cash_after, created_at "
        "FROM orders WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    result = [row_to_dict(r) for r in rows]
    conn.close()
    return result


def admin_get_user_analyses(user_id: int) -> list:
    """Retourne toutes les analyses d'un utilisateur donné."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT profil, score, recommended_tickers, notes, created_at "
        "FROM analyses WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    result = [row_to_dict(r) for r in rows]
    conn.close()
    return result


def admin_delete_user(user_id: int):
    """
    Supprime un utilisateur et toutes ses données associées
    (ordres, portfolio, analyses, feedbacks, watchlist).
    """
    conn = get_db_connection()
    conn.execute("DELETE FROM orders    WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM portfolio WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM analyses  WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM feedbacks WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM watchlist WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM users     WHERE id = ?",      (user_id,))
    conn.commit()
    conn.close()


def admin_delete_feedback(feedback_id: int):
    """Supprime un avis spécifique."""
    conn = get_db_connection()
    conn.execute("DELETE FROM feedbacks WHERE id = ?", (feedback_id,))
    conn.commit()
    conn.close()


def admin_get_global_stats() -> dict:
    """
    Statistiques globales de la plateforme pour le dashboard admin :
    - nb utilisateurs total
    - nb ordres total
    - nb analyses total
    - nb avis total
    - volume total simulé ($)
    - note moyenne des avis
    """
    conn = get_db_connection()

    users_row = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
    orders_row = conn.execute(
        "SELECT COUNT(*) as cnt, COALESCE(SUM(total), 0) as volume FROM orders"
    ).fetchone()
    analyses_row = conn.execute("SELECT COUNT(*) as cnt FROM analyses").fetchone()
    fb_row = conn.execute(
        "SELECT COUNT(*) as cnt, COALESCE(AVG(rating), 0) as avg_r FROM feedbacks"
    ).fetchone()

    conn.close()

    return {
        "nb_users":     int(users_row["cnt"]    or 0),
        "nb_orders":    int(orders_row["cnt"]   or 0),
        "nb_analyses":  int(analyses_row["cnt"] or 0),
        "nb_feedbacks": int(fb_row["cnt"]       or 0),
        "volume_total": float(orders_row["volume"] or 0),
        "avg_rating":   round(float(fb_row["avg_r"] or 0), 2),
    }