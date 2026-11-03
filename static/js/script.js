/**
 * Apla Shetkari – AI Helper for Farmers
 * Frontend Interaction Script
 * Handles multilingual UI, AI chatbot, speech recognition, crop recommendations, and dashboards.
 */

// UI Dictionary for English, Hindi, and Marathi translations
const TRANSLATIONS = {
    en: {
        askPlaceholder: "Ask any farming question (e.g. fertilizer for wheat, cotton pest control)...",
        sendBtn: "Send",
        clearingChat: "Chat history cleared.",
        confirmClear: "Are you sure you want to clear your chat history?",
        listening: "Listening... Speak your farming question now.",
        speechError: "Could not access microphone or recognize speech.",
        generatingRecs: "🌾 AI Agronomist is analyzing your soil, climate & irrigation data...",
        copied: "Copied!",
        emptyMsg: "Please type or speak a farming question first."
    },
    hi: {
        askPlaceholder: "खेती से जुड़ा कोई भी प्रश्न पूछें (जैसे गेहूं के लिए खाद, कपास में कीट नियंत्रण)...",
        sendBtn: "भेजें",
        clearingChat: "चैट इतिहास मिटा दिया गया।",
        confirmClear: "क्या आप वाकई अपना चैट इतिहास साफ़ करना चाहते हैं?",
        listening: "सुन रहे हैं... कृपया अपना खेती का सवाल बोलें।",
        speechError: "माइक्रोफ़ोन तक पहुंच नहीं हो सकी या आवाज़ नहीं पहचानी गई।",
        generatingRecs: "🌾 कृषि AI आपकी मिट्टी, मौसम और सिंचाई का विश्लेषण कर रहा है...",
        copied: "कॉपी किया गया!",
        emptyMsg: "कृपया पहले अपना सवाल लिखें या बोलें।"
    },
    mr: {
        askPlaceholder: "शेतीसंबंधी कोणताही प्रश्न विचारा (उदा. गव्हासाठी खत, सोयाबीन कीड नियंत्रण)...",
        sendBtn: "विचारा",
        clearingChat: "संभाषण इतिहास साफ केला.",
        confirmClear: "तुम्हाला संभाषण इतिहास खरोखर मिटवायचा आहे का?",
        listening: "ऐकत आहे... कृपया आपला शेतीचा प्रश्न बोला.",
        speechError: "मायक्रोफोन ऍक्सेस करता आला नाही किंवा आवाज ओळखता आला नाही.",
        generatingRecs: "🌾 कृषी AI आपल्या माती, हवामान आणि पाण्याचे विश्लेषण करत आहे...",
        copied: "कॉपी केले!",
        emptyMsg: "कृपया आधी शेतीचा प्रश्न टाइप करा किंवा बोला."
    }
};

// Global state
let currentLanguage = localStorage.getItem('apla_shetkari_lang') || 'en';

document.addEventListener('DOMContentLoaded', () => {
    initLanguageSelector();
    initMobileNav();
    initAlertDismiss();
    initPasswordToggle();
    initChatbot();
    initCropRecommendationForm();
    initDashboardTabs();
});

/* ===================================================================
   Language Selector & Persistence
   =================================================================== */
function initLanguageSelector() {
    const langSelectors = document.querySelectorAll('.lang-selector-element');
    
    // Set initial value in dropdowns
    langSelectors.forEach(select => {
        select.value = currentLanguage;
        select.addEventListener('change', (e) => {
            currentLanguage = e.target.value;
            localStorage.setItem('apla_shetkari_lang', currentLanguage);
            updateUILanguage(currentLanguage);
            
            // Sync all language dropdowns on page
            langSelectors.forEach(s => s.value = currentLanguage);
        });
    });

    updateUILanguage(currentLanguage);
}

function updateUILanguage(lang) {
    const dict = TRANSLATIONS[lang] || TRANSLATIONS.en;
    
    // Update chat input placeholder if present
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.placeholder = dict.askPlaceholder;
    }

    // Update active language selector in chat header
    const chatLangSelect = document.getElementById('chat-lang-select');
    if (chatLangSelect) {
        const langMap = { en: 'English', hi: 'Hindi', mr: 'Marathi' };
        chatLangSelect.value = langMap[lang] || 'English';
    }
}

/* ===================================================================
   Mobile Navigation Toggle
   =================================================================== */
function initMobileNav() {
    const toggle = document.querySelector('.nav-mobile-toggle');
    const links = document.querySelector('.nav-links');
    if (toggle && links) {
        toggle.addEventListener('click', () => {
            links.classList.toggle('show');
            const icon = toggle.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            }
        });
    }
}

/* ===================================================================
   Alert Dismissal
   =================================================================== */
function initAlertDismiss() {
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const alert = e.target.closest('.alert');
            if (alert) alert.remove();
        });
    });

    // Auto dismiss after 7 seconds
    setTimeout(() => {
        document.querySelectorAll('.alert:not(.alert-persistent)').forEach(alert => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        });
    }, 7000);
}

/* ===================================================================
   Password Visibility Toggle
   =================================================================== */
function initPasswordToggle() {
    document.querySelectorAll('.password-toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const group = btn.closest('.password-input-group');
            const input = group ? group.querySelector('input') : null;
            const icon = btn.querySelector('i');
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    if (icon) {
                        icon.classList.remove('fa-eye');
                        icon.classList.add('fa-eye-slash');
                    }
                } else {
                    input.type = 'password';
                    if (icon) {
                        icon.classList.remove('fa-eye-slash');
                        icon.classList.add('fa-eye');
                    }
                }
            }
        });
    });
}

/* ===================================================================
   AI Chatbot Functionality
   =================================================================== */
function initChatbot() {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    const voiceBtn = document.getElementById('voice-input-btn');
    const chatLangSelect = document.getElementById('chat-lang-select');

    if (!chatForm || !chatInput || !chatMessages) return;

    // Scroll chat window to bottom on load
    scrollChatToBottom();

    // Suggested questions click
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const question = chip.getAttribute('data-question') || chip.innerText.trim();
            chatInput.value = question;
            sendMessage(question);
        });
    });

    // Chat form submit
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const msg = chatInput.value.trim();
        if (msg) {
            sendMessage(msg);
        }
    });

    // Clear chat history
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', async () => {
            const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
            if (confirm(dict.confirmClear)) {
                try {
                    const res = await fetch('/clear-history', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    if (res.ok) {
                        // Clear message nodes except the initial welcome greeting
                        chatMessages.innerHTML = `
                            <div class="chat-message-row ai-row">
                                <div class="chat-avatar-mini ai-avatar-mini">
                                    <i class="fas fa-robot"></i>
                                </div>
                                <div class="message-bubble">
                                    <p><strong>नमस्कार! मी आपला शेतकरी AI आहे.</strong> 🌾</p>
                                    <p>मी आपल्या शेतातील पिके, खते, कीड नियंत्रण आणि हवामानाशी संबंधित सर्व प्रश्नांची उत्तरे देण्यास तयार आहे. खालीलपैकी कोणताही प्रश्न निवडा किंवा आपला स्वतःचा प्रश्न विचारा!</p>
                                    <div class="message-meta">
                                        <span><i class="far fa-clock"></i> Just now</span>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                } catch (err) {
                    console.error("Failed to clear chat:", err);
                }
            }
        });
    }

    // Speech-to-Text via Web Speech API
    if (voiceBtn) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;

            voiceBtn.addEventListener('click', () => {
                const langCodeMap = { en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN' };
                recognition.lang = langCodeMap[currentLanguage] || 'en-IN';

                try {
                    recognition.start();
                    voiceBtn.classList.add('recording');
                    const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
                    chatInput.placeholder = dict.listening;
                } catch (e) {
                    recognition.stop();
                    voiceBtn.classList.remove('recording');
                }
            });

            recognition.onresult = (event) => {
                const speechText = event.results[0][0].transcript;
                chatInput.value = speechText;
                voiceBtn.classList.remove('recording');
                updateUILanguage(currentLanguage);
                // Automatically send speech question
                if (speechText.trim()) {
                    sendMessage(speechText.trim());
                }
            };

            recognition.onerror = () => {
                voiceBtn.classList.remove('recording');
                updateUILanguage(currentLanguage);
            };

            recognition.onend = () => {
                voiceBtn.classList.remove('recording');
                updateUILanguage(currentLanguage);
            };
        } else {
            voiceBtn.style.display = 'none';
        }
    }

    // Send Message Handler
    async function sendMessage(messageText) {
        // Append user bubble
        appendUserMessage(messageText);
        chatInput.value = '';
        chatInput.disabled = true;

        // Show typing indicator
        if (typingIndicator) {
            typingIndicator.style.display = 'flex';
            scrollChatToBottom();
        }

        // Determine language to send
        let requestLang = 'English';
        if (chatLangSelect) {
            requestLang = chatLangSelect.value;
        } else {
            const map = { en: 'English', hi: 'Hindi', mr: 'Marathi' };
            requestLang = map[currentLanguage] || 'English';
        }

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: messageText,
                    language: requestLang
                })
            });

            const data = await response.json();

            // Hide typing indicator
            if (typingIndicator) typingIndicator.style.display = 'none';
            chatInput.disabled = false;
            chatInput.focus();

            if (data.success && data.response) {
                appendAIMessage(data.response);
            } else {
                const errMsg = data.error || "Unable to get advice right now. Please check your connection.";
                appendAIMessage(errMsg, true);
            }
        } catch (error) {
            if (typingIndicator) typingIndicator.style.display = 'none';
            chatInput.disabled = false;
            chatInput.focus();
            appendAIMessage("⚠️ Server connection error. Please verify the Flask server is running.", true);
        }

        scrollChatToBottom();
    }

    function appendUserMessage(text) {
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const row = document.createElement('div');
        row.className = 'chat-message-row user-row';
        row.innerHTML = `
            <div class="chat-avatar-mini user-avatar-mini">
                <i class="fas fa-user"></i>
            </div>
            <div class="message-bubble">
                <p>${escapeHTML(text)}</p>
                <div class="message-meta">
                    <span>${timeStr}</span>
                </div>
            </div>
        `;
        // Insert before typing indicator
        if (typingIndicator) {
            chatMessages.insertBefore(row, typingIndicator);
        } else {
            chatMessages.appendChild(row);
        }
        scrollChatToBottom();
    }

    function appendAIMessage(markdownText, isError = false) {
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const formattedHTML = formatMarkdown(markdownText);
        const row = document.createElement('div');
        row.className = 'chat-message-row ai-row';
        row.innerHTML = `
            <div class="chat-avatar-mini ai-avatar-mini">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-bubble ${isError ? 'error-bubble' : ''}">
                ${formattedHTML}
                <div class="message-meta">
                    <span><i class="far fa-clock"></i> ${timeStr}</span>
                    <button class="btn-copy-msg" onclick="copyMessageText(this)" title="Copy advice">
                        <i class="far fa-copy"></i> Copy
                    </button>
                </div>
            </div>
        `;
        if (typingIndicator) {
            chatMessages.insertBefore(row, typingIndicator);
        } else {
            chatMessages.appendChild(row);
        }
        scrollChatToBottom();
    }

    function scrollChatToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Global copy helper
window.copyMessageText = function(btn) {
    const bubble = btn.closest('.message-bubble');
    if (!bubble) return;
    
    // Clone and remove meta elements before copying text
    const clone = bubble.cloneNode(true);
    const meta = clone.querySelector('.message-meta');
    if (meta) meta.remove();
    
    const textToCopy = clone.innerText.trim();
    navigator.clipboard.writeText(textToCopy).then(() => {
        const original = btn.innerHTML;
        btn.innerHTML = `<i class="fas fa-check"></i> ${TRANSLATIONS[currentLanguage]?.copied || 'Copied!'}`;
        setTimeout(() => btn.innerHTML = original, 2000);
    });
};

/* ===================================================================
   Crop Recommendation Form Interactions
   =================================================================== */
function initCropRecommendationForm() {
    const form = document.getElementById('crop-recommendation-form');
    const loadingCard = document.getElementById('crop-loading-state');
    const resultsContainer = document.getElementById('crop-results-container');

    if (!form) return;

    form.addEventListener('submit', () => {
        if (loadingCard) {
            loadingCard.style.display = 'block';
            loadingCard.scrollIntoView({ behavior: 'smooth' });
        }
    });
}

/* ===================================================================
   Dashboard Tabs Switcher
   =================================================================== */
function initDashboardTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-content-panel');

    if (!tabButtons.length) return;

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab');

            tabButtons.forEach(b => b.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetPanel = document.getElementById(targetId);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

/* ===================================================================
   Utility Helpers
   =================================================================== */
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

/**
 * Converts standard AI markdown output into clean, structured HTML.
 * Handles bolding, bullet points, numbered lists, headings, and links.
 */
function formatMarkdown(text) {
    if (!text) return '';

    // Sanitize basic tags first
    let clean = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Headings
    clean = clean.replace(/^### (.*?)$/gm, '<h5 style="margin: 10px 0 4px; color: var(--primary-dark); font-weight: 700;">$1</h5>');
    clean = clean.replace(/^## (.*?)$/gm, '<h4 style="margin: 12px 0 6px; color: var(--primary-dark); font-weight: 800;">$1</h4>');
    clean = clean.replace(/^# (.*?)$/gm, '<h3 style="margin: 14px 0 8px; color: var(--primary-dark); font-weight: 800;">$1</h3>');

    // Bold text (**text**)
    clean = clean.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic (*text*)
    clean = clean.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Links [text](url)
    clean = clean.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color: var(--primary-main); text-decoration: underline;">$1</a>');

    // Process lists and paragraphs
    const lines = clean.split('\n');
    let inList = false;
    let listType = '';
    let result = [];

    for (let line of lines) {
        const trimmed = line.trim();

        // Bullet points (* or -)
        if (trimmed.startsWith('* ') || trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
            if (!inList) {
                result.push('<ul style="margin: 8px 0 8px 20px; list-style-type: disc;">');
                inList = true;
                listType = 'ul';
            }
            result.push(`<li>${trimmed.substring(2)}</li>`);
        }
        // Numbered list (1. 2. etc)
        else if (/^\d+\.\s+/.test(trimmed)) {
            if (!inList) {
                result.push('<ol style="margin: 8px 0 8px 20px;">');
                inList = true;
                listType = 'ol';
            }
            const content = trimmed.replace(/^\d+\.\s+/, '');
            result.push(`<li>${content}</li>`);
        }
        else {
            if (inList) {
                result.push(listType === 'ul' ? '</ul>' : '</ol>');
                inList = false;
            }
            if (trimmed.length > 0) {
                // If it's already a heading tag don't wrap in <p>
                if (trimmed.startsWith('<h') && trimmed.endsWith('>')) {
                    result.push(trimmed);
                } else {
                    result.push(`<p style="margin-bottom: 8px;">${trimmed}</p>`);
                }
            }
        }
    }

    if (inList) {
        result.push(listType === 'ul' ? '</ul>' : '</ol>');
    }

    return result.join('');
}
