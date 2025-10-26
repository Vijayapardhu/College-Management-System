/* Casual College Interactions - Fun & Engaging */

(function() {
    'use strict';

    // Fun motivational messages for students
    const motivationalMessages = [
        "You're doing amazing! 🌟",
        "Keep crushing it! 💪",
        "Learning looks good on you! 📚",
        "You're on fire today! 🔥",
        "Knowledge is power! ⚡",
        "You got this! 💯",
        "Smart cookie! 🍪",
        "Brainiac vibes! 🧠",
        "Future leader right here! 👑",
        "Making progress! 📈"
    ];

    // Fun greeting messages based on time
    const greetings = {
        morning: ["Good morning, champ! ☀️", "Rise and shine! 🌅", "Morning, superstar! 🌞"],
        afternoon: ["Good afternoon! 🌤️", "Hope you're having a great day! ☀️", "Afternoon vibes! 😎"],
        evening: ["Good evening! 🌙", "Evening, rockstar! 🌟", "Night owl mode! 🦉"]
    };

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeConfetti();
        initializeEmojiReactions();
        initializeProgressCelebrations();
        initializeHoverSounds();
        addMotivationalTooltips();
        initializeParticleEffects();
    });

    // Confetti celebration for achievements
    function initializeConfetti() {
        const achievementElements = document.querySelectorAll('[data-achievement]');
        
        achievementElements.forEach(element => {
            element.addEventListener('click', function() {
                createConfetti(this);
                showCelebrationMessage(this.getAttribute('data-achievement'));
            });
        });
    }

    function createConfetti(element) {
        const rect = element.getBoundingClientRect();
        const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
        
        for (let i = 0; i < 30; i++) {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: fixed;
                width: 10px;
                height: 10px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                top: ${rect.top + rect.height / 2}px;
                left: ${rect.left + rect.width / 2}px;
                border-radius: 50%;
                pointer-events: none;
                z-index: 9999;
            `;
            
            document.body.appendChild(confetti);
            
            const angle = (Math.PI * 2 * i) / 30;
            const velocity = 5 + Math.random() * 5;
            const vx = Math.cos(angle) * velocity;
            const vy = Math.sin(angle) * velocity;
            
            animateConfetti(confetti, vx, vy);
        }
    }

    function animateConfetti(element, vx, vy) {
        let x = parseFloat(element.style.left);
        let y = parseFloat(element.style.top);
        let opacity = 1;
        
        function update() {
            x += vx;
            y += vy + 0.5; // gravity
            opacity -= 0.02;
            
            element.style.left = x + 'px';
            element.style.top = y + 'px';
            element.style.opacity = opacity;
            
            if (opacity > 0) {
                requestAnimationFrame(update);
            } else {
                element.remove();
            }
        }
        
        update();
    }

    function showCelebrationMessage(achievement) {
        const message = document.createElement('div');
        message.className = 'fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 bg-white rounded-2xl shadow-2xl p-8 text-center';
        message.innerHTML = `
            <div class="text-6xl mb-4 animate-bounce">🎉</div>
            <h3 class="text-2xl font-bold text-gray-900 mb-2">${achievement}</h3>
            <p class="text-gray-600">Way to go! Keep it up!</p>
        `;
        
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translate(-50%, -50%) scale(0.8)';
            message.style.transition = 'all 0.3s ease';
            setTimeout(() => message.remove(), 300);
        }, 2000);
    }

    // Emoji reactions for cards
    function initializeEmojiReactions() {
        const cards = document.querySelectorAll('.metric-card, .dashboard-card, .action-card');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', function(e) {
                if (this.dataset.emojiReaction !== 'added') {
                    addFloatingEmoji(this, getRandomEmoji());
                    this.dataset.emojiReaction = 'added';
                }
            });
            
            card.addEventListener('mouseleave', function() {
                setTimeout(() => {
                    this.dataset.emojiReaction = '';
                }, 3000);
            });
        });
    }

    function getRandomEmoji() {
        const emojis = ['✨', '⭐', '🌟', '💫', '🎯', '🚀', '💡', '🏆', '👏', '💪'];
        return emojis[Math.floor(Math.random() * emojis.length)];
    }

    function addFloatingEmoji(element, emoji) {
        const emojiEl = document.createElement('div');
        emojiEl.textContent = emoji;
        emojiEl.style.cssText = `
            position: absolute;
            top: 50%;
            right: -20px;
            font-size: 1.5rem;
            pointer-events: none;
            z-index: 10;
            animation: floatUp 2s ease-out forwards;
        `;
        
        element.style.position = 'relative';
        element.appendChild(emojiEl);
        
        setTimeout(() => emojiEl.remove(), 2000);
    }

    // Progress celebrations
    function initializeProgressCelebrations() {
        const progressBars = document.querySelectorAll('.progress-bar-fill');
        
        progressBars.forEach(bar => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const percentage = parseInt(bar.style.width || '0');
                        if (percentage >= 90) {
                            showProgressCelebration(bar, '🎉 Almost there!');
                        } else if (percentage >= 75) {
                            showProgressCelebration(bar, '💪 Great progress!');
                        } else if (percentage >= 50) {
                            showProgressCelebration(bar, '👍 Halfway there!');
                        }
                        observer.unobserve(entry.target);
                    }
                });
            });
            
            observer.observe(bar);
        });
    }

    function showProgressCelebration(element, message) {
        const badge = document.createElement('div');
        badge.className = 'absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-bold px-3 py-1 rounded-full whitespace-nowrap';
        badge.textContent = message;
        
        element.parentElement.style.position = 'relative';
        element.parentElement.appendChild(badge);
        
        setTimeout(() => {
            badge.style.opacity = '0';
            badge.style.transform = 'translate(-50%, -10px)';
            badge.style.transition = 'all 0.3s ease';
            setTimeout(() => badge.remove(), 300);
        }, 3000);
    }

    // Hover sound effects (optional)
    function initializeHoverSounds() {
        // Create audio context for button clicks
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        document.querySelectorAll('.btn, .action-card').forEach(element => {
            element.addEventListener('click', function() {
                playClickSound(audioContext);
            });
        });
    }

    function playClickSound(context) {
        const oscillator = context.createOscillator();
        const gainNode = context.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(context.destination);
        
        oscillator.frequency.value = 800;
        gainNode.gain.setValueAtTime(0.1, context.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, context.currentTime + 0.1);
        
        oscillator.start(context.currentTime);
        oscillator.stop(context.currentTime + 0.1);
    }

    // Motivational tooltips
    function addMotivationalTooltips() {
        const buttons = document.querySelectorAll('.btn-primary, .btn-success');
        
        buttons.forEach(button => {
            button.addEventListener('mouseenter', function() {
                if (!this.dataset.motivational) {
                    const message = motivationalMessages[Math.floor(Math.random() * motivationalMessages.length)];
                    this.dataset.motivational = message;
                    this.title = message;
                }
            });
        });
    }

    // Particle effects on scroll
    function initializeParticleEffects() {
        const gradientHeaders = document.querySelectorAll('.gradient-header');
        
        gradientHeaders.forEach(header => {
            createParticles(header);
        });
    }

    function createParticles(container) {
        for (let i = 0; i < 15; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: absolute;
                width: ${4 + Math.random() * 8}px;
                height: ${4 + Math.random() * 8}px;
                background: rgba(255, 255, 255, ${0.1 + Math.random() * 0.3});
                border-radius: 50%;
                top: ${Math.random() * 100}%;
                left: ${Math.random() * 100}%;
                animation: float ${5 + Math.random() * 10}s ease-in-out infinite;
                animation-delay: ${Math.random() * 5}s;
            `;
            
            container.style.position = 'relative';
            container.style.overflow = 'hidden';
            container.appendChild(particle);
        }
    }

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes floatUp {
            0% {
                transform: translateY(0) scale(1);
                opacity: 1;
            }
            100% {
                transform: translateY(-100px) scale(1.5);
                opacity: 0;
            }
        }
        
        @keyframes float {
            0%, 100% {
                transform: translate(0, 0);
            }
            25% {
                transform: translate(10px, -10px);
            }
            50% {
                transform: translate(-10px, -20px);
            }
            75% {
                transform: translate(10px, -10px);
            }
        }
    `;
    document.head.appendChild(style);

    // Export to window
    window.CasualInteractions = {
        createConfetti,
        showCelebrationMessage,
        addFloatingEmoji,
        showProgressCelebration
    };

})();

// Fun loading messages
const loadingMessages = [
    "Brewing some knowledge... ☕",
    "Fetching awesome data... 🚀",
    "Loading brilliance... ✨",
    "Preparing something cool... 😎",
    "Getting things ready... 🎯",
    "Almost there... ⚡",
    "Hold tight... 🎪",
    "Making magic happen... 🎩"
];

// Random motivational message on page load
document.addEventListener('DOMContentLoaded', function() {
    const hour = new Date().getHours();
    let timeOfDay;
    
    if (hour < 12) timeOfDay = 'morning';
    else if (hour < 18) timeOfDay = 'afternoon';
    else timeOfDay = 'evening';
    
    const greetingMessages = {
        morning: ["Good morning, champ! ☀️", "Rise and shine! 🌅", "Morning, superstar! 🌞"],
        afternoon: ["Good afternoon! 🌤️", "Hope you're having a great day! ☀️", "Afternoon vibes! 😎"],
        evening: ["Good evening! 🌙", "Evening, rockstar! 🌟", "Night owl mode! 🦉"]
    };
    
    const greeting = greetingMessages[timeOfDay][Math.floor(Math.random() * greetingMessages[timeOfDay].length)];
    console.log(`%c${greeting}`, 'font-size: 20px; font-weight: bold; color: #3b82f6;');
});


