"""
Learning Streak Builder - Application Web
Version web de l'application de suivi d'apprentissage gamifié
"""

import json
import os
import random
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps



from flask import Flask, request, jsonify, session, send_from_directory
from dotenv import load_dotenv
from groq import Groq

from database import (
    init_db,
    get_user,
    create_user as db_create_user,
    update_user_streak,
    update_user_points,
    insert_learning_log,
    insert_badge,
    get_user_badges,
    count_user_logs,
    count_unique_subjects,
    get_daily_challenge,
    insert_daily_challenge,
    update_user_interests,
    execute_query,
    DatabaseConnection,
)

load_dotenv()

app = Flask(__name__, static_folder="webapp", static_url_path="")
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

# Groq AI client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ─── Badges & challenges (same as bot.py) ───────────────────────────────────

BADGES = {
    "first_step": {"name": "🌱 Premier Pas", "description": "Première session loguée"},
    "week_warrior": {"name": "🔥 Guerrier Hebdomadaire", "description": "7 jours consécutifs"},
    "month_master": {"name": "🏆 Maître du Mois", "description": "30 jours consécutifs"},
    "century": {"name": "💯 Centurion", "description": "100 sessions au total"},
    "explorer": {"name": "🗺️ Explorateur", "description": "Explorer 10 sujets différents"},
    "dedicated": {"name": "⚡ Dédié", "description": "Atteindre le niveau 5"},
    "marathon": {"name": "🎯 Marathon", "description": "50 jours consécutifs"},
    "polymath": {"name": "🧠 Polymathe", "description": "Explorer 25 sujets différents"},
    "quiz_novice": {"name": "🎓 Apprenti Quiz", "description": "Réussir 5 quiz"},
    "quiz_expert": {"name": "🏅 Expert Quiz", "description": "Réussir 20 quiz"},
    "perfect_score": {"name": "💎 Score Parfait", "description": "Obtenir 100% à un quiz"},
}

CHALLENGE_CATEGORIES = {
    "science": [
        "Recherche comment fonctionne la physique quantique",
        "Découvre les dernières avancées en biologie cellulaire",
        "Explore le concept de l'espace-temps",
        "Apprends comment fonctionne l'ADN",
        "Étudie le principe de la relativité",
    ],
    "technologie": [
        "Découvre ce qu'est le machine learning",
        "Explore les bases de la blockchain",
        "Apprends un nouveau langage de programmation",
        "Comprends comment fonctionne l'Internet",
        "Étudie les algorithmes de tri",
    ],
    "histoire": [
        "Découvre un événement historique majeur du 20e siècle",
        "Explore l'histoire d'une civilisation ancienne",
        "Apprends sur la révolution industrielle",
        "Étudie les causes d'une guerre mondiale",
        "Recherche l'histoire de ton pays",
    ],
    "art": [
        "Découvre un mouvement artistique",
        "Explore l'œuvre d'un artiste célèbre",
        "Apprends sur l'histoire de la musique classique",
        "Étudie les techniques de peinture",
        "Découvre l'architecture gothique",
    ],
    "philosophie": [
        "Explore un courant philosophique",
        "Lis sur Socrate et ses idées",
        "Découvre l'existentialisme",
        "Apprends sur l'éthique et la morale",
        "Étudie le stoïcisme",
    ],
    "langues": [
        "Apprends 10 nouveaux mots dans une langue étrangère",
        "Découvre l'origine d'expressions courantes",
        "Explore la linguistique",
        "Pratique la prononciation d'une nouvelle langue",
        "Étudie la grammaire d'une langue",
    ],
}

# ─── Helpers ─────────────────────────────────────────────────────────────────


def _user_id_from_username(username: str) -> int:
    """Derive a stable numeric user_id from a username (deterministic hash)."""
    return int(hashlib.sha256(username.encode()).hexdigest()[:15], 16)


def login_required(f):
    """Decorator: returns 401 if no session."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Non authentifié"}), 401
        return f(*args, **kwargs)
    return wrapper


def update_streak(user_id: int) -> int:
    user = get_user(user_id)
    if not user:
        return 0
    current_streak = user[2]
    longest_streak = user[3]
    last_log_date = user[6]
    today = datetime.now().date()
    if last_log_date:
        last_date = datetime.fromisoformat(last_log_date).date()
        days_diff = (today - last_date).days
        if days_diff == 0:
            new_streak = current_streak
        elif days_diff == 1:
            new_streak = current_streak + 1
        else:
            new_streak = 1
    else:
        new_streak = 1
    new_longest = max(longest_streak, new_streak)
    update_user_streak(user_id, new_streak, new_longest, today.isoformat())
    return new_streak


def calculate_points(duration: int, streak: int) -> int:
    return duration * 10 + streak * 5


def calculate_level(total_points: int) -> int:
    return max(1, int((total_points / 100) ** 0.5))


def check_and_award_badges(user_id: int):
    user = get_user(user_id)
    if not user:
        return []
    current_streak = int(user[2])
    level = int(user[5])
    total_logs = count_user_logs(user_id)
    unique_subjects = count_unique_subjects(user_id)
    earned_badge_names = get_user_badges(user_id)
    new_badges = []
    checks = [
        (total_logs == 1, "first_step"),
        (current_streak >= 7, "week_warrior"),
        (current_streak >= 30, "month_master"),
        (current_streak >= 50, "marathon"),
        (total_logs >= 100, "century"),
        (unique_subjects >= 10, "explorer"),
        (unique_subjects >= 25, "polymath"),
        (level >= 5, "dedicated"),
    ]
    for condition, key in checks:
        if condition and key not in earned_badge_names:
            new_badges.append(key)
    now = datetime.now().isoformat()
    for badge_key in new_badges:
        badge = BADGES[badge_key]
        insert_badge(user_id, badge["name"], badge["description"], now)
    return new_badges


# ─── Error handlers (return JSON instead of HTML) ────────────────────────────

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Route introuvable"}), 404
    return send_from_directory(app.static_folder, "index.html")

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Méthode non autorisée"}), 405

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Erreur serveur interne"}), 500


# ─── Static files ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# ─── Auth endpoints ──────────────────────────────────────────────────────────

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = (data or {}).get("username", "").strip()
    if not username or len(username) < 2 or len(username) > 30:
        return jsonify({"error": "Nom d'utilisateur invalide (2-30 caractères)"}), 400

    user_id = _user_id_from_username(username)
    existing = get_user(user_id)
    if existing:
        return jsonify({"error": "Ce nom d'utilisateur est déjà pris"}), 409

    now = datetime.now().isoformat()
    db_create_user(user_id, username, now)
    session["user_id"] = user_id
    session["username"] = username
    return jsonify({"message": "Inscription réussie!", "username": username})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = (data or {}).get("username", "").strip()
    if not username:
        return jsonify({"error": "Nom d'utilisateur requis"}), 400

    user_id = _user_id_from_username(username)
    user = get_user(user_id)
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    session["user_id"] = user_id
    session["username"] = username
    return jsonify({"message": "Connexion réussie!", "username": username})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Déconnexion réussie"})


@app.route("/api/me")
def me():
    if "user_id" not in session:
        return jsonify({"logged_in": False})
    user = get_user(session["user_id"])
    if not user:
        session.clear()
        return jsonify({"logged_in": False})
    return jsonify({
        "logged_in": True,
        "username": session["username"],
        "current_streak": user[2],
        "longest_streak": user[3],
        "total_points": user[4],
        "level": user[5],
        "interests": json.loads(user[8]) if user[8] else [],
    })


# ─── Log a session ───────────────────────────────────────────────────────────

@app.route("/api/log", methods=["POST"])
@login_required
def log_session():
    data = request.get_json() or {}
    subject = data.get("subject", "").strip()
    duration = data.get("duration")
    description = data.get("description", "").strip()

    if not subject:
        return jsonify({"error": "Sujet requis"}), 400
    try:
        duration = int(duration)
    except (TypeError, ValueError):
        return jsonify({"error": "Durée invalide"}), 400
    if duration <= 0 or duration > 1440:
        return jsonify({"error": "Durée entre 1 et 1440 minutes"}), 400

    user_id = session["user_id"]
    user = get_user(user_id)

    new_streak = update_streak(user_id)
    points = calculate_points(duration, new_streak)
    new_total = user[4] + points
    new_level = calculate_level(new_total)
    update_user_points(user_id, new_total, new_level)

    now = datetime.now().isoformat()
    insert_learning_log(user_id, subject, description, duration, now, points)

    new_badges = check_and_award_badges(user_id)
    badges_info = [{"name": BADGES[b]["name"], "description": BADGES[b]["description"]} for b in new_badges]

    return jsonify({
        "subject": subject,
        "duration": duration,
        "points_earned": points,
        "streak": new_streak,
        "level": new_level,
        "total_points": new_total,
        "new_badges": badges_info,
    })


# ─── Stats ────────────────────────────────────────────────────────────────────

@app.route("/api/stats")
@login_required
def stats():
    user_id = session["user_id"]
    user = get_user(user_id)

    log_stats = execute_query(
        "SELECT COUNT(*), SUM(duration), COUNT(DISTINCT subject) FROM learning_logs WHERE user_id = {ph}",
        (user_id,), fetch_one=True
    )
    total_logs = log_stats[0] if log_stats else 0
    total_minutes = log_stats[1] if log_stats and log_stats[1] else 0
    unique_subjects = log_stats[2] if log_stats else 0

    top_subjects = execute_query(
        "SELECT subject, COUNT(*) as count FROM learning_logs WHERE user_id = {ph} GROUP BY subject ORDER BY count DESC LIMIT 5",
        (user_id,), fetch_all=True
    ) or []

    badge_count_row = execute_query(
        "SELECT COUNT(*) FROM badges WHERE user_id = {ph}", (user_id,), fetch_one=True
    )
    badge_count = badge_count_row[0] if badge_count_row else 0

    created_at = user[7] if user[7] else None

    return jsonify({
        "username": session["username"],
        "current_streak": user[2],
        "longest_streak": user[3],
        "total_points": user[4],
        "level": user[5],
        "total_sessions": total_logs,
        "total_minutes": total_minutes,
        "unique_subjects": unique_subjects,
        "badge_count": badge_count,
        "total_badges": len(BADGES),
        "top_subjects": [{"subject": s[0], "count": s[1]} for s in top_subjects],
        "created_at": created_at,
    })


# ─── Badges ───────────────────────────────────────────────────────────────────

@app.route("/api/badges")
@login_required
def badges():
    user_id = session["user_id"]
    earned = execute_query(
        "SELECT badge_name, badge_description, earned_date FROM badges WHERE user_id = {ph}",
        (user_id,), fetch_all=True
    ) or []

    earned_names = [b[0] for b in earned]
    earned_list = [{"name": b[0], "description": b[1], "earned_date": b[2]} for b in earned]
    locked = [{"name": v["name"], "description": v["description"]}
              for v in BADGES.values() if v["name"] not in earned_names]

    return jsonify({"earned": earned_list, "locked": locked, "total": len(BADGES)})


# ─── History ──────────────────────────────────────────────────────────────────

@app.route("/api/history")
@login_required
def history():
    user_id = session["user_id"]
    limit = min(int(request.args.get("limit", 10)), 50)
    logs = execute_query(
        "SELECT subject, description, duration, log_date, points_earned FROM learning_logs WHERE user_id = {ph} ORDER BY log_date DESC LIMIT {ph}",
        (user_id, limit), fetch_all=True
    ) or []

    return jsonify([
        {"subject": l[0], "description": l[1], "duration": l[2], "date": l[3], "points": l[4]}
        for l in logs
    ])


# ─── Leaderboard ──────────────────────────────────────────────────────────────

@app.route("/api/leaderboard")
def leaderboard():
    rows = execute_query(
        "SELECT username, current_streak, longest_streak, total_points, level FROM users ORDER BY total_points DESC LIMIT 10",
        fetch_all=True
    ) or []

    return jsonify([
        {"username": r[0], "streak": r[1], "longest_streak": r[2], "points": r[3], "level": r[4]}
        for r in rows
    ])


# ─── Interests ────────────────────────────────────────────────────────────────

@app.route("/api/interests", methods=["POST"])
@login_required
def set_interests():
    data = request.get_json() or {}
    interests = data.get("interests", [])
    if isinstance(interests, str):
        interests = [i.strip() for i in interests.split(",") if i.strip()]
    if not interests:
        return jsonify({"error": "Au moins un centre d'intérêt requis"}), 400

    update_user_interests(session["user_id"], json.dumps(interests))
    return jsonify({"interests": interests})


# ─── Challenge ────────────────────────────────────────────────────────────────

@app.route("/api/challenge")
def challenge():
    today = datetime.now().date().isoformat()
    existing = get_daily_challenge(today)

    if existing:
        full_text = existing[0]
        category = existing[1]
    else:
        # Try AI generation
        category = random.choice(list(CHALLENGE_CATEGORIES.keys()))
        try:
            user_context = ""
            if "user_id" in session:
                user = get_user(session["user_id"])
                if user and user[8]:
                    try:
                        ints = json.loads(user[8])
                        if ints:
                            user_context = f"\nCentres d'intérêt de l'utilisateur : {', '.join(ints)}"
                    except Exception:
                        pass

            prompt = f"""Crée un défi d'apprentissage unique et motivant pour la catégorie : {category}
{user_context}
Le défi doit être réalisable en 15-30 minutes, concret et original.

Réponds UNIQUEMENT avec :
Ligne 1 : Le défi (une phrase claire)
Ligne 2 : (vide)
Ligne 3+ : Explication captivante (2-3 phrases)"""

            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Tu es un expert en pédagogie créative."},
                    {"role": "user", "content": prompt},
                ],
                temperature=1.0,
                max_tokens=400,
            )
            full_text = response.choices[0].message.content.strip()
        except Exception:
            full_text = random.choice(CHALLENGE_CATEGORIES[category])

        insert_daily_challenge(full_text, category, today)

    if "\n\n" in full_text:
        parts = full_text.split("\n\n", 1)
        title, explanation = parts[0], parts[1]
    elif "\n" in full_text:
        parts = full_text.split("\n", 1)
        title, explanation = parts[0], parts[1]
    else:
        title, explanation = full_text, ""

    return jsonify({"title": title, "explanation": explanation, "category": category})


# ─── AI Suggest ───────────────────────────────────────────────────────────────

@app.route("/api/suggest")
@login_required
def suggest():
    user_id = session["user_id"]
    user = get_user(user_id)
    interests = json.loads(user[8]) if user[8] else []
    if not interests:
        return jsonify({"error": "Définis d'abord tes centres d'intérêt"}), 400

    recent = execute_query(
        "SELECT subject FROM learning_logs WHERE user_id = {ph} ORDER BY log_date DESC LIMIT 5",
        (user_id,), fetch_all=True
    )
    recent_subjects = [r[0] for r in recent] if recent else []

    try:
        prompt = f"""Suggère un sujet d'apprentissage précis pour quelqu'un qui s'intéresse à : {', '.join(interests)}.
Niveau : {user[5]}, Streak : {user[2]} jours, Sujets récents : {', '.join(recent_subjects) or 'Aucun'}.

Format :
Sujet : [titre précis]
Pourquoi : [explication courte]
Comment commencer : [conseil pratique]"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Tu es un conseiller d'apprentissage expert."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=400,
        )
        suggestion = response.choices[0].message.content.strip()
    except Exception:
        cat = random.choice(list(CHALLENGE_CATEGORIES.keys()))
        suggestion = random.choice(CHALLENGE_CATEGORIES[cat])

    return jsonify({"suggestion": suggestion, "interests": interests, "recent": recent_subjects})


# ─── Quiz ─────────────────────────────────────────────────────────────────────

@app.route("/api/quiz/generate", methods=["POST"])
@login_required
def quiz_generate():
    data = request.get_json() or {}
    topic = data.get("topic", "").strip()

    if not topic:
        user = get_user(session["user_id"])
        interests = json.loads(user[8]) if user[8] else []
        if not interests:
            return jsonify({"error": "Spécifie un sujet ou définis tes centres d'intérêt"}), 400
        topic = random.choice(interests)

    try:
        prompt = f"""Génère 3 questions de quiz (QCM) sur le sujet : {topic}

Format JSON strict :
[
  {{"question": "...", "options": ["A","B","C","D"], "correct": 0, "explanation": "..."}}
]"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Réponds uniquement en JSON valide."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=1500,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        questions = json.loads(content.strip())
    except Exception:
        questions = [
            {
                "question": f"Quelle est une caractéristique importante de {topic} ?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": 0,
                "explanation": "Question de secours",
            }
        ]

    return jsonify({"topic": topic, "questions": questions})


@app.route("/api/quiz/submit", methods=["POST"])
@login_required
def quiz_submit():
    data = request.get_json() or {}
    topic = data.get("topic", "quiz")
    score = int(data.get("score", 0))
    total = int(data.get("total", 1))

    if total <= 0:
        return jsonify({"error": "Données invalides"}), 400
    score = max(0, min(score, total))

    user_id = session["user_id"]
    user = get_user(user_id)
    percentage = (score / total) * 100

    base_points = score * 50
    if percentage == 100:
        bonus = 100
    elif percentage >= 66:
        bonus = 50
    else:
        bonus = 0
    total_earned = base_points + bonus

    new_total = user[4] + total_earned
    new_level = calculate_level(new_total)
    update_user_points(user_id, new_total, new_level)

    now = datetime.now().isoformat()
    execute_query(
        "INSERT INTO quiz_results (user_id, category, score, total_questions, points_earned, quiz_date) VALUES ({ph},{ph},{ph},{ph},{ph},{ph})",
        (user_id, topic, score, total, total_earned, now),
    )

    # Check quiz badges
    qr = execute_query("SELECT COUNT(*) FROM quiz_results WHERE user_id = {ph}", (user_id,), fetch_one=True)
    total_quizzes = qr[0] if qr else 0
    pr = execute_query("SELECT COUNT(*) FROM quiz_results WHERE user_id = {ph} AND score = total_questions", (user_id,), fetch_one=True)
    perfect_scores = pr[0] if pr else 0

    earned_names = get_user_badges(user_id)
    new_badges = []
    if total_quizzes >= 5 and "quiz_novice" not in earned_names:
        new_badges.append("quiz_novice")
    if total_quizzes >= 20 and "quiz_expert" not in earned_names:
        new_badges.append("quiz_expert")
    if perfect_scores >= 1 and "perfect_score" not in earned_names:
        new_badges.append("perfect_score")

    for key in new_badges:
        b = BADGES[key]
        insert_badge(user_id, b["name"], b["description"], now)

    return jsonify({
        "score": score,
        "total": total,
        "percentage": percentage,
        "points_earned": total_earned,
        "total_points": new_total,
        "level": new_level,
        "new_badges": [{"name": BADGES[k]["name"], "description": BADGES[k]["description"]} for k in new_badges],
    })


# ─── AI Chat ─────────────────────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    if not message or len(message) > 1000:
        return jsonify({"error": "Message invalide"}), 400

    user_id = session["user_id"]
    user = get_user(user_id)
    user_context = ""
    if user:
        user_context = f"\nUtilisateur : streak {user[2]}j, niveau {user[5]}, {user[4]} pts"

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"Tu es Learning Streak Builder, un assistant d'apprentissage motivant. Réponds en français, de façon concise et motivante avec des emojis.{user_context}",
                },
                {"role": "user", "content": message},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        reply = response.choices[0].message.content
    except Exception:
        reply = "😊 Je suis là pour t'aider ! Explore les différentes sections de l'app pour suivre ton apprentissage ! 📚"

    return jsonify({"reply": reply})


# ─── Boot ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    print(f"🚀 Learning Streak Builder Web - http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
