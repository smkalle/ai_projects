/**
 * AI Commerce Agent - Frontend Application
 *
 * Handles chat interaction, product browsing, UCP discovery,
 * and session management.
 */

const API_BASE = '';
const SESSION_ID = 'session_' + Math.random().toString(36).substr(2, 9);

// --- DOM Elements ---
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const btnSend = document.getElementById('btn-send');
const productList = document.getElementById('product-list');
const categoryFilter = document.getElementById('category-filter');
const intentDisplay = document.getElementById('intent-display');
const matchedProducts = document.getElementById('matched-products');
const cartStatus = document.getElementById('cart-status');
const checkoutStatus = document.getElementById('checkout-status');
const sessionIdDisplay = document.getElementById('session-id');

// --- State ---
let isProcessing = false;

// --- Initialize ---
document.addEventListener('DOMContentLoaded', () => {
    sessionIdDisplay.textContent = SESSION_ID.substring(0, 12) + '...';
    loadProducts();

    // Event listeners
    chatForm.addEventListener('submit', handleChatSubmit);
    categoryFilter.addEventListener('change', () => loadProducts(categoryFilter.value));
    document.getElementById('btn-ucp-discover').addEventListener('click', showUCPDiscovery);
    document.getElementById('btn-clear-session').addEventListener('click', clearSession);
});

// --- Chat ---

async function handleChatSubmit(e) {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query || isProcessing) return;

    addMessage(query, 'user');
    chatInput.value = '';
    setProcessing(true);

    // Show typing indicator
    const typingId = showTypingIndicator();

    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, session_id: SESSION_ID }),
        });

        removeTypingIndicator(typingId);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        addMessage(data.response, 'assistant');

        // Update UI state
        updateIntent(data.intent);
        updateMatchedProducts(data.products);
        updateSessionState(data);

    } catch (err) {
        removeTypingIndicator(typingId);
        addMessage(`Error: ${err.message}. Make sure the server is running and OPENAI_API_KEY is set.`, 'assistant');
    }

    setProcessing(false);
}

function addMessage(content, role) {
    const div = document.createElement('div');
    div.className = `message ${role}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessage(content);

    div.appendChild(contentDiv);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessage(text) {
    if (!text) return '<p>No response received.</p>';

    // Convert markdown-like formatting
    let html = text
        // Code blocks
        .replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
        // Inline code
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        // Bold
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // Lists
        .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
        // Line breaks to paragraphs
        .split('\n\n')
        .map(p => {
            p = p.trim();
            if (p.startsWith('<li>')) {
                return '<ul>' + p + '</ul>';
            }
            if (p.startsWith('<pre>')) {
                return p;
            }
            return '<p>' + p.replace(/\n/g, '<br>') + '</p>';
        })
        .join('');

    return html;
}

function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.id = id;
    div.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function setProcessing(state) {
    isProcessing = state;
    btnSend.disabled = state;
    chatInput.disabled = state;
    if (!state) chatInput.focus();
}

function sendQuickQuery(query) {
    chatInput.value = query;
    chatForm.dispatchEvent(new Event('submit'));
}

// --- Products ---

async function loadProducts(category = '') {
    try {
        const params = new URLSearchParams();
        if (category) params.set('category', category);

        const response = await fetch(`${API_BASE}/api/products?${params}`);
        if (!response.ok) throw new Error('Failed to load products');

        const data = await response.json();
        renderProductList(data.products);
    } catch (err) {
        productList.innerHTML = `<p class="text-muted">Could not load products. Ensure merchant server is running.</p>`;
    }
}

function renderProductList(products) {
    if (!products || products.length === 0) {
        productList.innerHTML = '<p class="text-muted">No products found</p>';
        return;
    }

    productList.innerHTML = products.map(p => `
        <div class="product-card" onclick="sendQuickQuery('Tell me about ${p.name}')">
            <div class="product-name">${escapeHtml(p.name)}</div>
            <div class="product-price">$${p.price.toFixed(2)}</div>
            <div class="product-meta">
                <span class="product-category">${escapeHtml(p.category || 'General')}</span>
                ${p.rating ? ` &middot; ${p.rating}/5` : ''}
                ${p.brand ? ` &middot; ${escapeHtml(p.brand)}` : ''}
            </div>
        </div>
    `).join('');
}

// --- State Updates ---

function updateIntent(intent) {
    if (!intent) return;
    intentDisplay.textContent = intent;
    intentDisplay.className = `intent-badge ${intent}`;

    // Highlight architecture flow step
    const steps = document.querySelectorAll('.flow-step');
    steps.forEach(s => s.classList.remove('active'));

    const stepMap = {
        'search': 2,   // RAG Retrieval
        'buy': 3,      // UCP Actions
        'cart': 3,      // UCP Actions
        'checkout': 3,  // UCP Actions
        'general': 4,   // LLM Response
    };

    const idx = stepMap[intent];
    if (idx !== undefined && steps[idx]) {
        steps[idx].classList.add('active');
    }
}

function updateMatchedProducts(products) {
    if (!products || products.length === 0) {
        matchedProducts.innerHTML = '<p class="text-muted">No products matched</p>';
        return;
    }

    matchedProducts.innerHTML = products.slice(0, 5).map(p => `
        <div class="matched-product-item">
            <span class="mp-name">${escapeHtml(p.name || 'Unknown')}</span>
            <span class="mp-price">$${(p.price || 0).toFixed(2)}</span>
        </div>
    `).join('');
}

function updateSessionState(data) {
    if (data.cart_id) {
        cartStatus.textContent = data.cart_id.substring(0, 8) + '...';
    }
    if (data.checkout_id) {
        checkoutStatus.textContent = data.checkout_details?.status || 'Created';
    }
}

// --- UCP Discovery ---

async function showUCPDiscovery() {
    const modal = document.getElementById('ucp-modal');
    const body = document.getElementById('ucp-modal-body');
    modal.classList.remove('hidden');
    body.innerHTML = '<p>Loading UCP manifest...</p>';

    try {
        const response = await fetch(`${API_BASE}/api/ucp/discover`);
        if (!response.ok) throw new Error('Failed to fetch UCP manifest');

        const data = await response.json();
        body.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    } catch (err) {
        body.innerHTML = `<p>Error: ${err.message}. Ensure the merchant server is running.</p>`;
    }
}

function closeModal() {
    document.getElementById('ucp-modal').classList.add('hidden');
}

// Close modal on backdrop click
document.getElementById('ucp-modal')?.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) closeModal();
});

// --- Session ---

async function clearSession() {
    try {
        await fetch(`${API_BASE}/api/session/${SESSION_ID}`, { method: 'DELETE' });
    } catch (err) {
        // Ignore errors
    }

    // Clear UI
    chatMessages.innerHTML = `
        <div class="message assistant">
            <div class="message-content">
                <p>Session cleared. How can I help you today?</p>
            </div>
        </div>
    `;
    cartStatus.textContent = 'Empty';
    checkoutStatus.textContent = 'None';
    intentDisplay.textContent = '-';
    intentDisplay.className = 'intent-badge';
    matchedProducts.innerHTML = '<p class="text-muted">No products matched yet</p>';
}

// --- Utilities ---

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Keyboard shortcut: Escape to close modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});
