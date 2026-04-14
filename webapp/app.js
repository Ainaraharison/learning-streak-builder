/* Learning Streak Builder – Frontend JS */
(function () {
    "use strict";

    // ─── Helpers ─────────────────────────────────────────────────────────────
    const $ = (s) => document.querySelector(s);
    const $$ = (s) => document.querySelectorAll(s);

    async function api(path, opts = {}) {
        const res = await fetch(`/api${path}`, {
            ...opts,
            headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
        });
        const text = await res.text();
        let data;
        try {
            data = JSON.parse(text);
        } catch {
            throw new Error("Le serveur a renvoyé une réponse inattendue. Vérifie que l'app est lancée.");
        }
        if (!res.ok) throw new Error(data.error || "Erreur serveur");
        return data;
    }

    function toast(msg, type = "info") {
        const el = document.createElement("div");
        el.className = `toast ${type}`;
        el.textContent = msg;
        $("#toast-container").appendChild(el);
        setTimeout(() => el.remove(), 4000);
    }

    function show(el) { el.classList.remove("hidden"); }
    function hide(el) { el.classList.add("hidden"); }

    // ─── Auth ────────────────────────────────────────────────────────────────
    const authScreen = $("#auth-screen");
    const appScreen = $("#app-screen");

    async function checkSession() {
        try {
            const d = await api("/me");
            if (d.logged_in) {
                enterApp(d.username, d.interests);
            }
        } catch { /* not logged in */ }
    }

    function enterApp(username, interests) {
        authScreen.classList.remove("active");
        appScreen.classList.add("active");
        $("#nav-user").textContent = username;
        if (interests && interests.length) {
            renderTags(interests);
        }
        loadDashboard();
    }

    function exitApp() {
        appScreen.classList.remove("active");
        authScreen.classList.add("active");
        $("#auth-username").value = "";
        $("#auth-error").textContent = "";
    }

    $("#btn-login").addEventListener("click", async () => {
        const username = $("#auth-username").value.trim();
        if (!username) return;
        try {
            await api("/login", { method: "POST", body: JSON.stringify({ username }) });
            const me = await api("/me");
            enterApp(me.username, me.interests);
        } catch (e) {
            $("#auth-error").textContent = e.message;
        }
    });

    $("#btn-register").addEventListener("click", async () => {
        const username = $("#auth-username").value.trim();
        if (!username) return;
        try {
            await api("/register", { method: "POST", body: JSON.stringify({ username }) });
            const me = await api("/me");
            enterApp(me.username, me.interests);
            toast("Bienvenue ! 🎉", "success");
        } catch (e) {
            $("#auth-error").textContent = e.message;
        }
    });

    $("#auth-username").addEventListener("keydown", (e) => {
        if (e.key === "Enter") $("#btn-login").click();
    });

    $("#btn-logout").addEventListener("click", async () => {
        await api("/logout", { method: "POST" });
        exitApp();
    });

    // ─── Tabs ────────────────────────────────────────────────────────────────
    $$(".nav-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            $$(".nav-btn").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            $$(".tab-content").forEach((t) => t.classList.remove("active"));
            $(`#tab-${btn.dataset.tab}`).classList.add("active");

            // lazy-load data
            const tab = btn.dataset.tab;
            if (tab === "dashboard") loadDashboard();
            if (tab === "challenge") loadChallenge();
            if (tab === "leaderboard") loadLeaderboard();
        });
    });

    // ─── Dashboard ───────────────────────────────────────────────────────────
    async function loadDashboard() {
        try {
            const [stats, badges, history] = await Promise.all([
                api("/stats"),
                api("/badges"),
                api("/history?limit=5"),
            ]);
            renderStats(stats);
            renderBadges(badges);
            renderHistory(history);
        } catch (e) {
            toast(e.message, "error");
        }
    }

    function renderStats(s) {
        $("#s-streak").textContent = s.current_streak;
        $("#s-best").textContent = s.longest_streak;
        $("#s-points").textContent = s.total_points.toLocaleString();
        $("#s-level").textContent = s.level;
        $("#s-sessions").textContent = s.total_sessions;
        const h = Math.floor(s.total_minutes / 60);
        const m = s.total_minutes % 60;
        $("#s-time").textContent = h > 0 ? `${h}h${m > 0 ? m : ""}` : `${m}min`;

        // Level progress
        const currentLevelPoints = (s.level * s.level) * 100;
        const nextLevelPoints = ((s.level + 1) * (s.level + 1)) * 100;
        const progress = Math.min(100, ((s.total_points - currentLevelPoints) / (nextLevelPoints - currentLevelPoints)) * 100);
        $("#level-progress").style.width = `${Math.max(0, progress)}%`;
        $("#level-label").textContent = `Niveau ${s.level} → ${s.level + 1}  •  ${s.total_points} / ${nextLevelPoints} pts`;

        // Badge counter
        $("#badge-counter").textContent = `(${s.badge_count}/${s.total_badges})`;

        // Top subjects
        const cont = $("#top-subjects");
        if (!s.top_subjects.length) {
            cont.innerHTML = '<p style="color:var(--text-muted);font-size:.9rem">Aucun sujet encore</p>';
            return;
        }
        const max = s.top_subjects[0].count;
        cont.innerHTML = s.top_subjects
            .map(
                (t) => `
            <div class="subject-bar-row">
                <span class="subject-name">${esc(t.subject)}</span>
                <div class="subject-bar-bg"><div class="subject-bar-fill" style="width:${(t.count / max) * 100}%"></div></div>
                <span class="subject-count">${t.count}</span>
            </div>`
            )
            .join("");
    }

    function renderBadges(b) {
        const grid = $("#badges-grid");
        grid.innerHTML =
            b.earned
                .map((x) => `<span class="badge-item">${esc(x.name)}</span>`)
                .join("") +
            b.locked
                .map((x) => `<span class="badge-item locked">🔒 ${esc(x.description)}</span>`)
                .join("");
    }

    function renderHistory(list) {
        const cont = $("#history-list");
        if (!list.length) {
            cont.innerHTML = '<p style="color:var(--text-muted);font-size:.9rem">Aucune session encore</p>';
            return;
        }
        cont.innerHTML = list
            .map((l) => {
                const d = new Date(l.date);
                const fmt = d.toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit", year: "numeric" });
                return `<div class="history-item">
                    <div><strong>📖 ${esc(l.subject)}</strong>${l.description ? " – " + esc(l.description.slice(0, 60)) : ""}</div>
                    <div class="history-meta">⏱️ ${l.duration}min • 🎯 ${l.points}pts • ${fmt}</div>
                </div>`;
            })
            .join("");
    }

    // ─── Interests ───────────────────────────────────────────────────────────
    function renderTags(list) {
        $("#interests-tags").innerHTML = list.map((t) => `<span class="tag">${esc(t)}</span>`).join("");
    }

    $("#btn-interests").addEventListener("click", async () => {
        const raw = $("#interests-input").value.trim();
        if (!raw) return;
        try {
            const d = await api("/interests", {
                method: "POST",
                body: JSON.stringify({ interests: raw }),
            });
            renderTags(d.interests);
            $("#interests-input").value = "";
            toast("Centres d'intérêt sauvegardés ✅", "success");
        } catch (e) {
            toast(e.message, "error");
        }
    });

    // ─── Log Session ─────────────────────────────────────────────────────────
    $("#btn-log").addEventListener("click", async () => {
        const subject = $("#log-subject").value.trim();
        const duration = $("#log-duration").value;
        const description = $("#log-desc").value.trim();
        if (!subject || !duration) {
            toast("Sujet et durée requis", "error");
            return;
        }
        const btn = $("#btn-log");
        btn.disabled = true;
        try {
            const d = await api("/log", {
                method: "POST",
                body: JSON.stringify({ subject, duration: parseInt(duration), description }),
            });
            const box = $("#log-result");
            box.classList.remove("hidden", "error");
            let text = `✅ Session enregistrée !

📚 Sujet : ${d.subject}
⏱️ Durée : ${d.duration} min
🎯 Points gagnés : +${d.points_earned}
🔥 Streak : ${d.streak} jour(s)
📊 Niveau : ${d.level}
💰 Total : ${d.total_points} pts`;

            if (d.new_badges.length) {
                text += `\n\n🏆 Nouveaux badges !\n` + d.new_badges.map((b) => `${b.name} – ${b.description}`).join("\n");
            }
            box.textContent = text;

            // Reset form
            $("#log-subject").value = "";
            $("#log-duration").value = "";
            $("#log-desc").value = "";
            toast(`+${d.points_earned} points ! 🔥`, "success");
        } catch (e) {
            const box = $("#log-result");
            box.classList.remove("hidden");
            box.classList.add("error");
            box.textContent = e.message;
        } finally {
            btn.disabled = false;
        }
    });

    // ─── Suggest ─────────────────────────────────────────────────────────────
    $("#btn-suggest").addEventListener("click", async () => {
        const btn = $("#btn-suggest");
        btn.disabled = true;
        btn.textContent = "⏳ Réflexion...";
        try {
            const d = await api("/suggest");
            const box = $("#suggest-result");
            show(box);
            box.classList.remove("error");
            box.textContent = d.suggestion;
        } catch (e) {
            const box = $("#suggest-result");
            show(box);
            box.classList.add("error");
            box.textContent = e.message;
        } finally {
            btn.disabled = false;
            btn.textContent = "Obtenir une suggestion";
        }
    });

    // ─── Challenge ───────────────────────────────────────────────────────────
    async function loadChallenge() {
        show($("#challenge-loading"));
        hide($("#challenge-content"));
        try {
            const d = await api("/challenge");
            $("#challenge-title").textContent = d.title;
            $("#challenge-cat").textContent = `📖 ${d.category.charAt(0).toUpperCase() + d.category.slice(1)}`;
            $("#challenge-explanation").textContent = d.explanation || "";
            hide($("#challenge-loading"));
            show($("#challenge-content"));
        } catch (e) {
            hide($("#challenge-loading"));
            toast(e.message, "error");
        }
    }

    // ─── Leaderboard ─────────────────────────────────────────────────────────
    async function loadLeaderboard() {
        try {
            const list = await api("/leaderboard");
            const medals = ["🥇", "🥈", "🥉"];
            const cont = $("#leaderboard-list");
            if (!list.length) {
                cont.innerHTML = '<p style="color:var(--text-muted)">Aucun apprenant encore</p>';
                return;
            }
            cont.innerHTML = list
                .map(
                    (u, i) => `
                <div class="lb-row">
                    <span class="lb-rank">${medals[i] || i + 1}</span>
                    <span class="lb-name">${esc(u.username)}</span>
                    <div class="lb-stats">
                        <span>Niv. ${u.level}</span>
                        <span>${u.points.toLocaleString()} pts</span>
                        <span>${u.streak} 🔥</span>
                    </div>
                </div>`
                )
                .join("");
        } catch (e) {
            toast(e.message, "error");
        }
    }

    // ─── Quiz ────────────────────────────────────────────────────────────────
    let quizState = { questions: [], topic: "", currentQ: 0, score: 0 };

    $("#btn-quiz-start").addEventListener("click", async () => {
        const topic = $("#quiz-topic").value.trim();
        hide($("#quiz-start"));
        show($("#quiz-loading"));
        hide($("#quiz-result"));
        hide($("#quiz-game"));
        try {
            const d = await api("/quiz/generate", {
                method: "POST",
                body: JSON.stringify({ topic }),
            });
            quizState = { questions: d.questions, topic: d.topic, currentQ: 0, score: 0 };
            hide($("#quiz-loading"));
            show($("#quiz-game"));
            renderQuestion();
        } catch (e) {
            hide($("#quiz-loading"));
            show($("#quiz-start"));
            toast(e.message, "error");
        }
    });

    function renderQuestion() {
        const q = quizState.questions[quizState.currentQ];
        const total = quizState.questions.length;
        const i = quizState.currentQ;

        $("#quiz-game").innerHTML = `
            <div class="quiz-question">
                <h3>Question ${i + 1}/${total} — ${esc(quizState.topic)}</h3>
                <p style="font-size:1.05rem;margin-bottom:1rem;font-weight:500">${esc(q.question)}</p>
                <div class="quiz-options">
                    ${q.options.map((o, idx) => `<button class="quiz-option" data-idx="${idx}">${idx + 1}. ${esc(o)}</button>`).join("")}
                </div>
                <div id="quiz-feedback" class="hidden"></div>
            </div>`;

        $$(".quiz-option").forEach((btn) => {
            btn.addEventListener("click", () => handleAnswer(parseInt(btn.dataset.idx)));
        });
    }

    function handleAnswer(idx) {
        const q = quizState.questions[quizState.currentQ];
        const options = $$(".quiz-option");
        options.forEach((btn) => {
            btn.disabled = true;
            const bIdx = parseInt(btn.dataset.idx);
            if (bIdx === q.correct) btn.classList.add("correct");
            if (bIdx === idx && idx !== q.correct) btn.classList.add("wrong");
        });

        if (idx === q.correct) quizState.score++;

        const feedback = $("#quiz-feedback");
        show(feedback);
        if (q.explanation) {
            feedback.innerHTML = `<div class="quiz-explanation">💡 ${esc(q.explanation)}</div>`;
        }

        const isLast = quizState.currentQ >= quizState.questions.length - 1;
        const btnText = isLast ? "Voir les résultats" : "Question suivante →";
        const nextBtn = document.createElement("button");
        nextBtn.className = "btn btn-primary";
        nextBtn.textContent = btnText;
        nextBtn.addEventListener("click", () => {
            if (isLast) {
                submitQuiz();
            } else {
                quizState.currentQ++;
                renderQuestion();
            }
        });
        $("#quiz-game").appendChild(nextBtn);
    }

    async function submitQuiz() {
        hide($("#quiz-game"));
        try {
            const d = await api("/quiz/submit", {
                method: "POST",
                body: JSON.stringify({
                    topic: quizState.topic,
                    score: quizState.score,
                    total: quizState.questions.length,
                }),
            });

            const box = $("#quiz-result");
            show(box);
            let badgeText = "";
            if (d.new_badges.length) {
                badgeText = `<div style="margin-top:1rem;"><strong>🏆 Nouveaux badges !</strong><br>${d.new_badges.map((b) => `${b.name} – ${b.description}`).join("<br>")}</div>`;
            }
            box.innerHTML = `
                <div class="card" style="text-align:center;">
                    <h2>📊 Résultats du Quiz</h2>
                    <p style="font-size:2rem;font-weight:800;margin:.5rem 0">${d.score}/${d.total}</p>
                    <p style="font-size:1.1rem;color:${d.percentage >= 66 ? "var(--green)" : "var(--accent)"}">${d.percentage.toFixed(0)}%</p>
                    <div style="display:flex;justify-content:center;gap:1.5rem;margin:1rem 0;flex-wrap:wrap">
                        <span>🎯 +${d.points_earned} pts</span>
                        <span>📊 Niveau ${d.level}</span>
                        <span>💰 ${d.total_points.toLocaleString()} pts total</span>
                    </div>
                    ${badgeText}
                    <button class="btn btn-primary" style="margin-top:1rem" onclick="document.querySelector('#quiz-result').classList.add('hidden');document.querySelector('#quiz-start').classList.remove('hidden');">🔄 Nouveau quiz</button>
                </div>`;
        } catch (e) {
            toast(e.message, "error");
            show($("#quiz-start"));
        }
    }

    // ─── Chat ────────────────────────────────────────────────────────────────
    async function sendChat() {
        const input = $("#chat-input");
        const msg = input.value.trim();
        if (!msg) return;
        input.value = "";

        const container = $("#chat-messages");
        container.innerHTML += `<div class="chat-msg user"><p>${esc(msg)}</p></div>`;
        container.scrollTop = container.scrollHeight;

        try {
            const d = await api("/chat", {
                method: "POST",
                body: JSON.stringify({ message: msg }),
            });
            container.innerHTML += `<div class="chat-msg bot"><p>${esc(d.reply)}</p></div>`;
        } catch (e) {
            container.innerHTML += `<div class="chat-msg bot"><p>❌ ${esc(e.message)}</p></div>`;
        }
        container.scrollTop = container.scrollHeight;
    }

    $("#btn-chat-send").addEventListener("click", sendChat);
    $("#chat-input").addEventListener("keydown", (e) => {
        if (e.key === "Enter") sendChat();
    });

    // ─── Util ────────────────────────────────────────────────────────────────
    function esc(str) {
        const d = document.createElement("div");
        d.textContent = str;
        return d.innerHTML;
    }

    // ─── Init ────────────────────────────────────────────────────────────────
    checkSession();
})();
