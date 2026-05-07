from datetime import datetime
from database import get_conn, get_user_cash_balance, update_user_cash_balance


def buy_stock(user_id: int, ticker: str, nom: str, quantity: int, price: float):
    if quantity <= 0:
        return False, "La quantité doit être strictement positive."

    total_amount = quantity * price
    cash = get_user_cash_balance(user_id)

    if total_amount > cash:
        return False, "Solde insuffisant pour effectuer cet achat."

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT quantity, avg_buy_price FROM portfolio WHERE user_id=? AND ticker=?",
        (user_id, ticker),
    )
    existing = cur.fetchone()

    if existing:
        old_qty, old_avg = existing
        new_qty = old_qty + quantity
        new_avg = ((old_qty * old_avg) + (quantity * price)) / new_qty

        cur.execute(
            """
            UPDATE portfolio
            SET quantity=?, avg_buy_price=?, updated_at=?
            WHERE user_id=? AND ticker=?
            """,
            (new_qty, new_avg, datetime.now().strftime("%Y-%m-%d %H:%M"), user_id, ticker),
        )
    else:
        cur.execute(
            """
            INSERT INTO portfolio (user_id, ticker, nom, quantity, avg_buy_price, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, ticker, nom, quantity, price, datetime.now().strftime("%Y-%m-%d %H:%M")),
        )

    cur.execute(
        """
        INSERT INTO orders (user_id, ticker, nom, side, quantity, price, total_amount, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            ticker,
            nom,
            "BUY",
            quantity,
            price,
            total_amount,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        ),
    )

    conn.commit()
    conn.close()

    update_user_cash_balance(user_id, cash - total_amount)
    return True, f"Achat simulé effectué : {quantity} action(s) de {ticker}."


def sell_stock(user_id: int, ticker: str, nom: str, quantity: int, price: float):
    if quantity <= 0:
        return False, "La quantité doit être strictement positive."

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT quantity, avg_buy_price FROM portfolio WHERE user_id=? AND ticker=?",
        (user_id, ticker),
    )
    existing = cur.fetchone()

    if not existing:
        conn.close()
        return False, "Cette action n'existe pas dans votre portefeuille."

    old_qty, old_avg = existing

    if quantity > old_qty:
        conn.close()
        return False, "Quantité insuffisante dans le portefeuille."

    new_qty = old_qty - quantity
    total_amount = quantity * price

    if new_qty == 0:
        cur.execute(
            "DELETE FROM portfolio WHERE user_id=? AND ticker=?",
            (user_id, ticker),
        )
    else:
        cur.execute(
            """
            UPDATE portfolio
            SET quantity=?, updated_at=?
            WHERE user_id=? AND ticker=?
            """,
            (new_qty, datetime.now().strftime("%Y-%m-%d %H:%M"), user_id, ticker),
        )

    cur.execute(
        """
        INSERT INTO orders (user_id, ticker, nom, side, quantity, price, total_amount, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            ticker,
            nom,
            "SELL",
            quantity,
            price,
            total_amount,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        ),
    )

    conn.commit()
    conn.close()

    cash = get_user_cash_balance(user_id)
    update_user_cash_balance(user_id, cash + total_amount)
    return True, f"Vente simulée effectuée : {quantity} action(s) de {ticker}."


def load_portfolio(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT ticker, nom, quantity, avg_buy_price, updated_at
        FROM portfolio
        WHERE user_id=?
        ORDER BY ticker
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def load_orders(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT ticker, nom, side, quantity, price, total_amount, created_at
        FROM orders
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows