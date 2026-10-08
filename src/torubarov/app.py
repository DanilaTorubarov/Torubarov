from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g
import mysql.connector
import hashlib
from llama_cpp import Llama

# Загружаем модель один раз при старте приложения
# Путь укажите свой, куда скачали GGUF
llm = Llama(
    model_path="/home/guest/models/smollm2/SmolLM2-360M-Instruct-Q4_K_M.gguf",
    n_ctx=4096,       # размер контекста
    n_threads=4,      # количество потоков CPU
    verbose=False
)
app = Flask(__name__)
app.secret_key = "adaAUIYtf76g218ro;1ihy89a"
COST_PER_REQUEST = 5.00 
DB_CONFIG = {
    "host": "185.114.247.43",
    "port": 3306,
    "database": "sch688_vvedenie",
    "user": "sch688_vvedenie",
    "password": "Qwerty123",
}

SALT = b"KamalinSigma"

def current_user():
    """Возвращает dict с данными текущего юзера или None."""
    if "user_id" not in session:
        return None
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(
        "SELECT id, username, email, balance, Is_admin FROM users WHERE id = %s",
        (session["user_id"],)
    )
    user = cur.fetchone()
    cur.close()
    return user

def hash_password(password: str) -> str:
    key = hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode('utf-8'),
        salt=SALT,
        iterations=600000,
        dklen=32
    )
    return key.hex()


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ---------- Регистрация ----------
@app.route('/user_register', methods=['POST'])
def user_register():
    req = request.get_json()
    name = req['name']
    login = req['email']
    password = hash_password(req['password'])
    da
    cnx = mysql.connector.connect(**DB_CONFIG)
    cur = cnx.cursor()
    try: 
        cur.execute(
        'INSERT INTO `users`(`username`, `email`, `password_hash`) VALUES (%s, %s, %s)',
        (name, login, password)
        )
    except:
        return jsonify({"status": "ne ok"})
    cnx.commit()
    cur.close()
    cnx.close()
    return jsonify({"status": "ok"})


# ---------- Логин ----------
@app.route('/user_login', methods=['POST'])
def user_login():
    req = request.get_json()
    email = req.get('email')
    password = hash_password(req.get('password', ''))

    cnx = mysql.connector.connect(**DB_CONFIG)
    cur = cnx.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT id, username, email FROM users WHERE email = %s AND password_hash = %s",
            (email, password)
        )
    except: return {"status": "net"}
    user = cur.fetchone()
    cur.close()
    cnx.close()

    if not user:
        return jsonify({"status": "error", "message": "Неверный email или пароль"}), 401

    session["user_id"] = user["id"]
    return jsonify({"status": "ok", "redirect": url_for("lk")})


# ---------- Выход ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- Страницы ----------
@app.route("/")
def registration():
    return render_template('registration.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = hash_password(request.form.get("password", ""))

        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT id, username, email FROM users WHERE email = %s AND password_hash = %s",
            (email, password)
        )
        user = cur.fetchone()
        cur.close()

        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("lk"))
        return render_template("login.html", error="Неверный email или пароль")

    return render_template('login.html')


@app.route("/lk")
def lk():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cur = db.cursor(dictionary=True)
    # Если в таблице нет first_name/last_name/balance — замените на свои поля,
    # например: SELECT username AS first_name, email, 0 AS balance
    cur.execute(
        "SELECT username, email, balance FROM users WHERE id = %s",
        (session["user_id"],)
    )
    user = cur.fetchone()
    cur.close()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template("lk.html", user=user)

@app.route("/become_admin", methods=["POST"])
def become_admin():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Не авторизован"}), 401

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE users SET Is_admin = 1 WHERE id = %s",
        (session["user_id"],)
    )
    db.commit()
    cur.close()
    return jsonify({"status": "ok"})

def require_admin():
    """Возвращает dict текущего админа или None."""
    user = current_user()
    if not user or not user.get("Is_admin"):
        return None
    return user


@app.route("/admin")
def admin_panel():
    me = require_admin()
    if not me:
        return redirect(url_for("lk"))

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(
        "SELECT id, username, email, balance, Is_admin FROM users ORDER BY id"
    )
    users = cur.fetchall()
    cur.close()

    return render_template("admin.html", users=users, current_user_id=me["id"])


@app.route("/admin/action", methods=["POST"])
def admin_action():
    me = require_admin()
    if not me:
        return jsonify({"status": "error", "message": "Доступ запрещён"}), 403

    req = request.get_json(silent=True) or {}
    action = req.get("action")
    user_id = req.get("user_id")

    if not isinstance(user_id, int):
        return jsonify({"status": "error", "message": "Некорректный user_id"}), 400

    db = get_db()
    cur = db.cursor()

    try:
        if action == "set_admin":
            value = 1 if int(req.get("value", 0)) else 0
            if user_id == me["id"] and value == 0:
                return jsonify({"status": "error",
                                "message": "Нельзя снять админа с самого себя"}), 400
            cur.execute("UPDATE users SET Is_admin = %s WHERE id = %s", (value, user_id))

        elif action == "delete":
            if user_id == me["id"]:
                return jsonify({"status": "error",
                                "message": "Нельзя удалить самого себя"}), 400
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))

        elif action == "set_balance":
            value = float(req.get("value", 0))
            cur.execute("UPDATE users SET balance = %s WHERE id = %s", (value, user_id))

        else:
            return jsonify({"status": "error", "message": "Неизвестное действие"}), 400

        db.commit()
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()

    return jsonify({"status": "ok"})

@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("chat.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    if "user_id" not in session:
        return jsonify({"error": "Не авторизован"}), 401

    req = request.get_json(silent=True) or {}
    message = (req.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Пустое сообщение"}), 400

    db = get_db()
    cur = db.cursor(dictionary=True)

    # 1. Проверяем баланс
    cur.execute("SELECT balance FROM users WHERE id = %s", (session["user_id"],))
    row = cur.fetchone()
    if row is None:
        cur.close()
        session.clear()
        return jsonify({"error": "Пользователь не найден"}), 401

    balance = float(row["balance"] or 0)
    if balance < COST_PER_REQUEST:
        cur.close()
        return jsonify({
            "error": f"Недостаточно средств. Баланс: {balance:.2f} ₽, "
                     f"нужно: {COST_PER_REQUEST:.2f} ₽"
        }), 402   # 402 Payment Required

    # 2. Списываем деньги ДО запроса (чтобы нельзя было накрутить при сбое)
    cur.execute(
        "UPDATE users SET balance = balance - %s WHERE id = %s",
        (COST_PER_REQUEST, session["user_id"])
    )
    db.commit()
    cur.close()

    # 3. Делаем запрос к нейросети
    try:
        # ----- ваш вызов модели -----
        # Вариант с llama-cpp-python:
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": message}],
             max_tokens=256, temperature=0.7
         )
        reply = response["choices"][0]["message"]["content"]

        # Вариант с Ollama через requests:
        # import requests as rq
        # r = rq.post("http://127.0.0.1:11434/api/chat",
        #             json={"model": "smollm2-local",
        #                   "messages": [{"role": "user", "content": message}],
        #                   "stream": False}, timeout=120)
        # reply = r.json()["message"]["content"]

        # Заглушка:
        #reply = f"Ты написал: «{message}». (заглушка)"
        # ----------------------------

        return jsonify({
            "reply": reply,
            "new_balance": balance - COST_PER_REQUEST
        })

    except Exception as e:
        # 4. Если модель упала — возвращаем деньги
        cur = db.cursor()
        cur.execute(
            "UPDATE users SET balance = balance + %s WHERE id = %s",
            (COST_PER_REQUEST, session["user_id"])
        )
        db.commit()
        cur.close()
        return jsonify({"error": f"Ошибка нейросети: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)