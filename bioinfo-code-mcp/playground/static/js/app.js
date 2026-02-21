/**
 * Bioinformatics Playground — Frontend Application
 *
 * Handles the code editor (CodeMirror), execution, template loading,
 * API search, theme toggling, and result display.
 */

(function () {
    "use strict";

    // ── State ──────────────────────────────────────────────────────────
    const SESSION_ID = document.getElementById("session-id").value;
    let editor = null;
    let isRunning = false;

    // ── Initialize CodeMirror ──────────────────────────────────────────
    function initEditor() {
        const container = document.getElementById("editor-container");
        const isDark = document.documentElement.getAttribute("data-theme") === "dark";

        editor = CodeMirror(container, {
            value: '# Welcome to the Bioinformatics Playground!\n# Select a starter project from the sidebar, or write your own code.\n#\n# Available: ncbi, uniprot, pdb, ensembl, blast, seq_utils, fmt, state\n# All API calls are async — use: result = await ncbi.search_pubmed("query")\n# Use state dict to persist data: state["key"] = value\n\n# Try this:\nprint("Hello, Bioinformatics!")\nreturn {"status": "ready"}',
            mode: "python",
            theme: isDark ? "dracula" : "default",
            lineNumbers: true,
            matchBrackets: true,
            autoCloseBrackets: true,
            styleActiveLine: true,
            indentUnit: 4,
            tabSize: 4,
            indentWithTabs: false,
            lineWrapping: false,
            extraKeys: {
                "Ctrl-Enter": runCode,
                "Cmd-Enter": runCode,
                "Ctrl-/": "toggleComment",
                "Cmd-/": "toggleComment",
                Tab: function (cm) {
                    if (cm.somethingSelected()) {
                        cm.indentSelection("add");
                    } else {
                        cm.replaceSelection("    ", "end");
                    }
                },
            },
        });
    }

    // ── Code Execution ────────────────────────────────────────────────
    async function runCode() {
        if (isRunning) return;

        const code = editor.getValue().trim();
        if (!code) return;

        isRunning = true;
        const runBtn = document.getElementById("btn-run");
        runBtn.disabled = true;
        runBtn.innerHTML = '<span class="spinner"></span> Running...';

        const output = document.getElementById("output-container");
        output.innerHTML = '<div class="output-running"><span class="spinner"></span> Executing...</div>';

        const timeEl = document.getElementById("execution-time");
        timeEl.textContent = "";
        const startTime = performance.now();

        try {
            const resp = await fetch("/api/execute", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: SESSION_ID, code }),
            });
            const data = await resp.json();
            const elapsed = ((performance.now() - startTime) / 1000).toFixed(2);
            timeEl.textContent = `${elapsed}s`;

            if (data.success) {
                output.innerHTML = `<div class="output-success">${escapeHtml(data.result)}</div>`;
            } else {
                output.innerHTML = `<div class="output-error">${escapeHtml(data.result)}</div>`;
            }

            // Update state indicator
            const stateIndicator = document.getElementById("state-indicator");
            const stateKeys = document.getElementById("state-keys");
            if (data.state_keys && data.state_keys.length > 0) {
                stateIndicator.style.display = "inline-block";
                stateKeys.textContent = data.state_keys.join(", ");
            } else {
                stateIndicator.style.display = "none";
            }
        } catch (err) {
            const elapsed = ((performance.now() - startTime) / 1000).toFixed(2);
            timeEl.textContent = `${elapsed}s`;
            output.innerHTML = `<div class="output-error">Network error: ${escapeHtml(err.message)}</div>`;
        } finally {
            isRunning = false;
            runBtn.disabled = false;
            runBtn.innerHTML =
                '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg> Run';
        }
    }

    // ── Template Loading ──────────────────────────────────────────────
    async function loadTemplate(templateId) {
        try {
            const resp = await fetch(`/api/template/${templateId}`);
            if (!resp.ok) return;
            const data = await resp.json();

            editor.setValue(data.code);
            document.getElementById("current-template-name").textContent = data.title;

            // Highlight active template in sidebar
            document.querySelectorAll(".template-item").forEach((el) => {
                el.classList.toggle("active", el.dataset.id === templateId);
            });

            // Clear output
            const output = document.getElementById("output-container");
            output.innerHTML = `<div style="color: var(--text-muted); font-family: var(--font-sans);">
                <strong>${escapeHtml(data.title)}</strong> — ${escapeHtml(data.description)}<br>
                <span style="font-size: 12px;">Press <kbd style="background: var(--bg-tertiary); padding: 1px 5px; border-radius: 3px;">Ctrl+Enter</kbd> or click <strong>Run</strong> to execute.</span>
            </div>`;
        } catch (err) {
            console.error("Failed to load template:", err);
        }
    }

    // ── API Search ────────────────────────────────────────────────────
    let searchTimeout = null;

    async function searchAPIs() {
        const query = document.getElementById("api-search-input").value.trim();
        const module = document.getElementById("api-module-filter").value;
        const container = document.getElementById("api-search-results");

        if (!query && !module) {
            container.innerHTML = '<p class="search-hint">Type to search 40+ bioinformatics operations</p>';
            return;
        }

        try {
            const params = new URLSearchParams();
            if (query) params.set("query", query);
            if (module) params.set("module", module);

            const resp = await fetch(`/api/search?${params}`);
            const data = await resp.json();

            if (data.results.length === 0) {
                container.innerHTML = '<p class="search-hint">No operations found. Try different search terms.</p>';
                return;
            }

            container.innerHTML = data.results
                .map(
                    (op) => `
                <div class="search-result-item" data-example="${escapeAttr(op.example || "")}">
                    <div class="search-result-name">${escapeHtml(op.name)}</div>
                    <div class="search-result-desc">${escapeHtml(op.description)}</div>
                    <div class="search-result-method">${escapeHtml(op.method)}</div>
                    ${op.example ? `<div class="search-result-example">${escapeHtml(op.example)}</div>` : ""}
                </div>
            `
                )
                .join("");

            // Click to insert example into editor
            container.querySelectorAll(".search-result-item").forEach((el) => {
                el.addEventListener("click", () => {
                    const example = el.dataset.example;
                    if (example) {
                        const pos = editor.getCursor();
                        editor.replaceRange(example + "\n", pos);
                        closeModal();
                        editor.focus();
                    }
                });
            });
        } catch (err) {
            container.innerHTML = `<p class="search-hint">Search error: ${escapeHtml(err.message)}</p>`;
        }
    }

    function openModal() {
        document.getElementById("api-search-modal").style.display = "flex";
        setTimeout(() => document.getElementById("api-search-input").focus(), 100);
    }

    function closeModal() {
        document.getElementById("api-search-modal").style.display = "none";
    }

    // ── Theme Toggle ──────────────────────────────────────────────────
    function toggleTheme() {
        const html = document.documentElement;
        const current = html.getAttribute("data-theme");
        const next = current === "dark" ? "light" : "dark";
        html.setAttribute("data-theme", next);
        if (editor) {
            editor.setOption("theme", next === "dark" ? "dracula" : "default");
        }
        localStorage.setItem("playground-theme", next);
    }

    // ── State Reset ───────────────────────────────────────────────────
    async function resetState() {
        try {
            await fetch("/api/reset", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: SESSION_ID }),
            });
            document.getElementById("state-indicator").style.display = "none";
            const output = document.getElementById("output-container");
            output.innerHTML =
                '<div style="color: var(--green);">Session state cleared.</div>';
        } catch (err) {
            console.error("Reset failed:", err);
        }
    }

    // ── Utilities ─────────────────────────────────────────────────────
    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    function escapeAttr(text) {
        return text.replace(/"/g, "&quot;").replace(/'/g, "&#39;");
    }

    // ── Event Binding ─────────────────────────────────────────────────
    function bindEvents() {
        // Run button
        document.getElementById("btn-run").addEventListener("click", runCode);

        // Reset state
        document.getElementById("btn-reset-state").addEventListener("click", resetState);

        // Clear output
        document.getElementById("btn-clear-output").addEventListener("click", () => {
            document.getElementById("output-container").innerHTML = "";
            document.getElementById("execution-time").textContent = "";
        });

        // Theme toggle
        document.getElementById("btn-theme").addEventListener("click", toggleTheme);

        // Sidebar toggle
        document.getElementById("btn-sidebar-toggle").addEventListener("click", () => {
            document.getElementById("sidebar").classList.toggle("collapsed");
        });

        // Template items
        document.querySelectorAll(".template-item").forEach((el) => {
            el.addEventListener("click", () => loadTemplate(el.dataset.id));
        });

        // API search modal
        document.getElementById("btn-api-search").addEventListener("click", openModal);
        document.getElementById("btn-close-modal").addEventListener("click", closeModal);
        document.getElementById("api-search-modal").addEventListener("click", (e) => {
            if (e.target === e.currentTarget) closeModal();
        });

        // API search input (debounced)
        document.getElementById("api-search-input").addEventListener("input", () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(searchAPIs, 300);
        });
        document.getElementById("api-module-filter").addEventListener("change", searchAPIs);

        // Keyboard shortcuts
        document.addEventListener("keydown", (e) => {
            // Escape to close modal
            if (e.key === "Escape") closeModal();
            // Ctrl+K / Cmd+K to open API search
            if ((e.ctrlKey || e.metaKey) && e.key === "k") {
                e.preventDefault();
                openModal();
            }
        });
    }

    // ── Init ──────────────────────────────────────────────────────────
    function init() {
        // Restore theme
        const savedTheme = localStorage.getItem("playground-theme");
        if (savedTheme) {
            document.documentElement.setAttribute("data-theme", savedTheme);
        }

        initEditor();
        bindEvents();
    }

    // Wait for DOM
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
