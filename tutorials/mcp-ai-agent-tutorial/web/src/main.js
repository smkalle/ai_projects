// Basic JS to integrate with FastAPI backend

let API_BASE_URL = (window.API_BASE_URL) || (window.localStorage.getItem('API_BASE_URL')) || (window.API_BASE_URL_DEFAULT || 'http://localhost:8000');

const $ = (sel) => document.querySelector(sel);
const el = (tag, cls) => { const e = document.createElement(tag); if (cls) e.className = cls; return e; };

async function api(path, opts = {}) {
  const url = `${API_BASE_URL}${path}`;
  const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

async function refreshHealth() {
  try {
    const t0 = performance.now();
    const data = await api('/health');
    const dt = Math.round(performance.now() - t0);
    $('#api-health').innerHTML = `Health: <span class="font-medium text-green-600">Online</span> (${dt} ms)`;
  } catch (e) {
    $('#api-health').innerHTML = `Health: <span class="font-medium text-red-600">Offline</span>`;
  }
}

async function refreshAgents() {
  try {
    const list = await api('/agents');
    const sel = $('#agent-select');
    sel.innerHTML = '';
    if (!list?.length) {
      const opt = el('option'); opt.textContent = 'No agents'; opt.value = ''; sel.appendChild(opt);
      return;
    }
    for (const id of list) {
      const opt = el('option'); opt.textContent = id; opt.value = id; sel.appendChild(opt);
    }
  } catch (e) {
    console.error(e);
  }
}

async function refreshTools() {
  const sel = $('#agent-select');
  const agent = sel.value;
  const container = $('#tools');
  container.innerHTML = '';
  if (!agent) return;
  try {
    const { tools } = await api(`/agents/${agent}/tools`);
    if (!tools?.length) {
      container.textContent = 'No tools available.';
      return;
    }
    for (const t of tools) {
      const card = el('div', 'rounded-lg border p-3 dark:border-gray-700');
      const name = t.name || 'Unnamed';
      const desc = t.description || '';
      const id = `exec-${name}`;
      card.innerHTML = `
        <div class="font-medium text-gray-900 dark:text-gray-100">${name}</div>
        <div class="mb-2 text-sm text-gray-600 dark:text-gray-300">${desc}</div>
        <textarea id="${id}-params" class="hs-input w-full text-xs" rows="3" placeholder='{"arg": "value"}'></textarea>
        <div class="mt-2 flex items-center gap-2">
          <button data-tool="${name}" class="exec-tool rounded-md bg-indigo-600 px-2 py-1 text-xs font-medium text-white hover:bg-indigo-500">Execute</button>
          <span id="${id}-status" class="text-xs text-gray-500"></span>
        </div>
      `;
      container.appendChild(card);
    }
    // bind exec buttons
    container.querySelectorAll('.exec-tool').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const name = e.currentTarget.getAttribute('data-tool');
        const sel = $('#agent-select');
        const agent = sel.value;
        const status = $(`#exec-${name}-status`);
        const ta = $(`#exec-${name}-params`);
        if (!agent) { status.textContent = 'No agent selected'; return; }
        let params = {};
        try { params = ta.value ? JSON.parse(ta.value) : {}; }
        catch { status.textContent = 'Invalid JSON'; return; }
        status.textContent = 'Running...';
        try {
          const res = await api(`/agents/${agent}/tools`, { method: 'POST', body: JSON.stringify({ tool_name: name, parameters: params }) });
          status.textContent = 'Done';
          appendChat('tool', `${name}: ${JSON.stringify(res.result).slice(0, 500)}`);
        } catch (err) {
          status.textContent = 'Failed';
        }
      });
    });
  } catch (e) {
    container.textContent = 'Failed to load tools.';
  }
}

function appendChat(role, content) {
  const row = el('div', 'mb-2');
  row.innerHTML = `<div class="text-xs text-gray-500">${role}</div><div class="rounded-md bg-white p-2">${content}</div>`;
  $('#chat-log').appendChild(row);
  $('#chat-log').scrollTop = $('#chat-log').scrollHeight;
}

async function main() {
  await refreshHealth();
  await refreshAgents();

  // Theme init
  try {
    const saved = window.localStorage.getItem('theme') || 'light';
    if (saved === 'dark') document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
  } catch {}

  // API URL init
  $('#api-url').value = API_BASE_URL;

  $('#theme-toggle').addEventListener('click', () => {
    const d = document.documentElement.classList.toggle('dark');
    try { window.localStorage.setItem('theme', d ? 'dark' : 'light'); } catch {}
  });

  $('#save-api-url').addEventListener('click', () => {
    const v = $('#api-url').value.trim();
    if (!v) return;
    API_BASE_URL = v.replace(/\/$/, '');
    try { window.localStorage.setItem('API_BASE_URL', API_BASE_URL); } catch {}
    refreshHealth();
  });

  $('#create-agent').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const cfg = {
      model: fd.get('model'),
      provider: fd.get('provider'),
      api_key: fd.get('api_key'),
      temperature: 0.7,
      max_tokens: 2000,
      mcp_servers: (fd.get('mcp_servers') || '').split(',').map(s => s.trim()).filter(Boolean)
    };
    $('#create-status').textContent = 'Creating...';
    try {
      const resp = await api('/agents/create', { method: 'POST', body: JSON.stringify(cfg) });
      $('#create-status').textContent = `Created ${resp.agent_id}`;
      await refreshAgents();
      await refreshTools();
    } catch (err) {
      $('#create-status').textContent = 'Failed to create agent';
      console.error(err);
    }
  });

  $('#agent-select').addEventListener('change', async () => {
    $('#chat-log').innerHTML = '';
    await refreshTools();
  });

  $('#chat-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const agent = $('#agent-select').value;
    const msg = $('#chat-input').value.trim();
    if (!agent || !msg) return;
    appendChat('user', msg);
    $('#chat-input').value = '';
    try {
      const res = await api(`/agents/${agent}/chat`, { method: 'POST', body: JSON.stringify({ message: msg }) });
      appendChat('assistant', res.response);
    } catch (err) {
      appendChat('assistant', 'Error: failed to get response.');
    }
  });

  $('#refresh-tools').addEventListener('click', async () => {
    await refreshTools();
  });
}

main();
