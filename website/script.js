// Animations pour les compteurs
function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = 2000;
    const increment = target / (duration / 16);
    let current = 0;

    const updateCounter = () => {
        current += increment;
        if (current < target) {
            element.textContent = Math.floor(current);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    };

    updateCounter();
}

// Observer pour déclencher les animations au scroll
const observerOptions = {
    threshold: 0.5,
    rootMargin: '0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const counters = entry.target.querySelectorAll('.stat-number');
            counters.forEach(counter => {
                if (!counter.classList.contains('animated')) {
                    animateCounter(counter);
                    counter.classList.add('animated');
                }
            });
        }
    });
}, observerOptions);

// Observer la section stats
document.addEventListener('DOMContentLoaded', () => {
    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        observer.observe(statsSection);
    }
});

// Smooth scroll pour les liens de navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Données de démo pour les commandes
const demoResponses = {
    '!start': {
        type: 'embed',
        title: '🎉 Bienvenue au Learning Streak Builder!',
        description: 'Félicitations ! Tu as rejoint la communauté des apprenants!',
        fields: [
            { name: 'Comment commencer?', value: 'Utilise `!log` pour enregistrer ta première session d\'apprentissage' },
            { name: 'Besoin d\'aide?', value: 'Tape `!help` pour voir toutes les commandes' }
        ]
    },
    '!log Python 30 Appris les classes': {
        type: 'success',
        message: '✅ Session enregistrée avec succès!\n\n📚 Sujet: Python\n⏱️ Durée: 30 minutes\n📝 Description: Appris les classes\n\n🔥 Streak: 1 jour\n⭐ Points gagnés: +305 points\n🎯 Niveau: 1\n\n🏆 Badge débloqué: 🌱 Premier Pas'
    },
    '!stats': {
        type: 'embed',
        title: '📊 Tes Statistiques',
        fields: [
            { name: 'Streak actuel', value: '15 jours 🔥' },
            { name: 'Meilleur streak', value: '18 jours' },
            { name: 'Points totaux', value: '2,450 ⭐' },
            { name: 'Niveau', value: '5 🎯' },
            { name: 'Sessions totales', value: '47 sessions' },
            { name: 'Sujets explorés', value: '12 sujets différents' }
        ]
    },
    '!challenge': {
        type: 'embed',
        title: '🎯 Défi du Jour',
        description: 'Découvre comment les algorithmes de compression JPEG sacrifient des détails invisibles pour réduire la taille des images',
        fields: [
            { name: 'Catégorie', value: '📖 Technologie' },
            { name: '💡 Pourquoi ce défi?', value: 'Cette technique fascinante combine mathématiques et psychologie visuelle. Tu découvriras comment nos yeux peuvent être "trompés" de manière bénéfique. Commence par rechercher "DCT transform" et "chroma subsampling" pour comprendre les deux piliers de cette compression.' },
            { name: 'Comment participer?', value: 'Explore ce sujet et logue ta session avec `!log`' }
        ]
    },
    '!badges': {
        type: 'embed',
        title: '🏆 Tes Badges',
        description: 'Badges débloqués (4/8):',
        fields: [
            { name: '✅ 🌱 Premier Pas', value: 'Première session loguée' },
            { name: '✅ 🔥 Guerrier Hebdomadaire', value: '7 jours consécutifs' },
            { name: '✅ 🗺️ Explorateur', value: 'Explorer 10 sujets différents' },
            { name: '✅ ⚡ Dédié', value: 'Atteindre le niveau 5' },
            { name: '🔒 🏆 Maître du Mois', value: '30 jours consécutifs (Progression: 15/30)' },
            { name: '🔒 🎯 Marathon', value: '50 jours consécutifs' },
            { name: '🔒 💯 Centurion', value: '100 sessions au total (Progression: 47/100)' },
            { name: '🔒 🧠 Polymathe', value: 'Explorer 25 sujets différents' }
        ]
    },
    '!leaderboard': {
        type: 'embed',
        title: '🏆 Classement des Apprenants',
        description: 'Top 10 des apprenants les plus actifs',
        fields: [
            { name: '🥇 Alice', value: 'Streak: 45 jours | Points: 8,920 | Niveau: 9' },
            { name: '🥈 Bob', value: 'Streak: 32 jours | Points: 6,150 | Niveau: 7' },
            { name: '🥉 Charlie', value: 'Streak: 28 jours | Points: 5,340 | Niveau: 7' },
            { name: '**4.** David', value: 'Streak: 23 jours | Points: 4,780 | Niveau: 6' },
            { name: '**5.** Emma', value: 'Streak: 20 jours | Points: 4,125 | Niveau: 6' },
            { name: '**6.** Frank', value: 'Streak: 15 jours | Points: 2,450 | Niveau: 5' }
        ]
    }
};

// Fonction pour créer un message utilisateur
function createUserMessage(command) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'demo-user-message';
    messageDiv.innerHTML = `<strong>Toi:</strong> ${command}`;
    return messageDiv;
}

// Fonction pour créer un message bot
function createBotMessage(response) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'demo-bot-message';
    
    if (response.type === 'embed') {
        let html = `<div style="border-left: 4px solid var(--primary); padding-left: 1rem;">`;
        html += `<h4 style="margin-bottom: 0.75rem;">${response.title}</h4>`;
        if (response.description) {
            html += `<p style="color: var(--text-secondary); margin-bottom: 1rem;">${response.description}</p>`;
        }
        if (response.fields) {
            response.fields.forEach(field => {
                html += `<div style="margin-bottom: 0.75rem;">`;
                html += `<strong>${field.name}:</strong><br>`;
                html += `<span style="color: var(--text-secondary);">${field.value}</span>`;
                html += `</div>`;
            });
        }
        html += `</div>`;
        messageDiv.innerHTML = html;
    } else if (response.type === 'success') {
        messageDiv.innerHTML = `<pre style="white-space: pre-wrap; font-family: inherit;">${response.message}</pre>`;
    }
    
    return messageDiv;
}

// Fonction pour envoyer une commande de démo
function sendDemoCommand(command) {
    const chatMessages = document.getElementById('chatMessages');
    
    // Supprime le message de bienvenue si présent
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    // Ajoute le message utilisateur
    const userMessage = createUserMessage(command);
    chatMessages.appendChild(userMessage);
    
    // Scroll vers le bas
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Simule un délai avant la réponse du bot
    setTimeout(() => {
        const response = demoResponses[command];
        if (response) {
            const botMessage = createBotMessage(response);
            chatMessages.appendChild(botMessage);
            
            // Animation d'apparition
            botMessage.style.opacity = '0';
            botMessage.style.transform = 'translateY(10px)';
            setTimeout(() => {
                botMessage.style.transition = 'all 0.3s ease';
                botMessage.style.opacity = '1';
                botMessage.style.transform = 'translateY(0)';
            }, 10);
            
            // Scroll vers le bas
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }, 500);
}

// Fonction pour effacer la démo
function clearDemo() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <p>👋 Bienvenue ! Essaie différentes commandes ci-dessous pour voir le bot en action.</p>
        </div>
    `;
}

// Fonction pour copier le code
function copyCode(button) {
    const codeBlock = button.previousElementSibling;
    const code = codeBlock.textContent;
    
    navigator.clipboard.writeText(code).then(() => {
        const originalText = button.textContent;
        button.textContent = '✅ Copié!';
        button.style.background = 'var(--secondary)';
        
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
        }, 2000);
    }).catch(err => {
        console.error('Erreur lors de la copie:', err);
        button.textContent = '❌ Erreur';
        setTimeout(() => {
            button.textContent = '📋';
        }, 2000);
    });
}

// Animation au scroll pour les cartes
const cardObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '0';
            entry.target.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                entry.target.style.transition = 'all 0.6s ease';
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }, 100);
            
            cardObserver.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.1
});

// Observer toutes les cartes
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.feature-card, .command-card, .tech-card, .stat-card');
    cards.forEach((card, index) => {
        card.style.transitionDelay = `${index * 0.05}s`;
        cardObserver.observe(card);
    });
});

// Effet parallax léger sur le hero
document.addEventListener('mousemove', (e) => {
    const hero = document.querySelector('.hero');
    if (hero) {
        const x = (e.clientX / window.innerWidth - 0.5) * 20;
        const y = (e.clientY / window.innerHeight - 0.5) * 20;
        
        const heroVisual = document.querySelector('.hero-visual');
        if (heroVisual) {
            heroVisual.style.transform = `translate(${x}px, ${y}px)`;
            heroVisual.style.transition = 'transform 0.3s ease';
        }
    }
});

// Navbar transparent jusqu'au scroll
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        navbar.style.background = 'rgba(10, 14, 39, 0.98)';
        navbar.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.background = 'rgba(10, 14, 39, 0.95)';
        navbar.style.boxShadow = 'none';
    }
    
    lastScroll = currentScroll;
});

// Easter egg: Konami code
let konamiCode = [];
const konamiSequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // ↑↑↓↓←→←→BA

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.keyCode);
    
    if (konamiCode.length > konamiSequence.length) {
        konamiCode.shift();
    }
    
    if (konamiCode.toString() === konamiSequence.toString()) {
        activateEasterEgg();
        konamiCode = [];
    }
});

function activateEasterEgg() {
    // Effet confettis ou animation spéciale
    const body = document.body;
    body.style.animation = 'rainbow 2s linear';
    
    // Notification
    const notification = document.createElement('div');
    notification.textContent = '🎉 Easter Egg débloqué! Tu es un vrai gamer! 🎮';
    notification.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--primary);
        color: white;
        padding: 2rem 3rem;
        border-radius: 16px;
        font-size: 1.5rem;
        font-weight: bold;
        z-index: 10000;
        box-shadow: 0 8px 32px rgba(88, 101, 242, 0.6);
        animation: fadeInUp 0.5s ease;
    `;
    
    body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.5s ease';
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

// Animation CSS pour l'easter egg
const style = document.createElement('style');
style.textContent = `
    @keyframes rainbow {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; transform: translate(-50%, -50%); }
        to { opacity: 0; transform: translate(-50%, -60%); }
    }
`;
document.head.appendChild(style);

console.log('%c🎓 Learning Streak Builder', 'color: #5865F2; font-size: 24px; font-weight: bold;');
console.log('%cMerci de visiter notre site! 🚀', 'color: #57F287; font-size: 16px;');
console.log('%cTape le Konami Code pour une surprise... 👀', 'color: #FEE75C; font-size: 12px;');
