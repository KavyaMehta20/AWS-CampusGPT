/**
 * CampusGPT Frontend Chat Client.
 * Handles chat messaging, streaming UX, citation rendering,
 * and the collapsible 'How CampusGPT answered' trace panel.
 */

const API_BASE = typeof API_BASE_URL !== 'undefined' ? API_BASE_URL : '';

// DOM Elements
const messagesContainer = document.getElementById('messages-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const universityTitle = document.getElementById('university-title');
const modelBadge = document.getElementById('model-badge');
const configBtn = document.getElementById('config-btn');
const configModal = document.getElementById('config-modal');
const configJson = document.getElementById('config-json');

let runtimeConfig = null;

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
  fetchConfig();
  if (configBtn) {
    configBtn.addEventListener('click', toggleConfigModal);
  }
});

async function fetchConfig() {
  try {
    const res = await fetch(`${API_BASE}/api/config`);
    if (res.ok) {
      runtimeConfig = await res.json();
      universityTitle.textContent = `${runtimeConfig.university_name} CampusGPT`;
      modelBadge.textContent = `Model: ${runtimeConfig.gemini_model}`;
      configJson.textContent = JSON.stringify(runtimeConfig, null, 2);
    }
  } catch (err) {
    console.warn("Could not fetch remote config, using defaults:", err);
    modelBadge.textContent = "Backend Offline / Local";
  }
}

function toggleConfigModal() {
  configModal.classList.toggle('hidden');
}

function askPreset(question) {
  userInput.value = question;
  handleSend(new Event('submit'));
}

async function handleSend(e) {
  if (e) e.preventDefault();
  const question = userInput.value.trim();
  if (!question) return;

  // Append user message
  appendUserMessage(question);
  userInput.value = '';
  setLoadingState(true);

  // Placeholder bot message
  const botMessageEl = createBotMessageElement();
  messagesContainer.appendChild(botMessageEl);
  scrollToBottom();

  try {
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });

    if (!response.ok) {
      let errorDetail = "Server returned an error";
      try {
        const errJson = await response.json();
        errorDetail = errJson.detail || errorDetail;
      } catch (_) {}

      if (response.status === 429) {
        renderBotError(botMessageEl, "Rate Limit Exceeded (429): Google AI Studio quota hit. Please wait a moment and try again.");
      } else {
        renderBotError(botMessageEl, `Backend Error (${response.status}): ${errorDetail}`);
      }
      return;
    }

    const data = await response.json();
    renderBotResponse(botMessageEl, data);
  } catch (err) {
    renderBotError(
      botMessageEl,
      "Cannot connect to CampusGPT backend. Is the FastAPI server running on port 8000? Check the terminal for errors."
    );
  } finally {
    setLoadingState(false);
    scrollToBottom();
  }
}

function appendUserMessage(text) {
  const el = document.createElement('div');
  el.className = 'message user-message';
  el.innerHTML = `
    <div class="avatar">👤</div>
    <div class="bubble"><p>${escapeHtml(text)}</p></div>
  `;
  messagesContainer.appendChild(el);
  scrollToBottom();
}

function createBotMessageElement() {
  const el = document.createElement('div');
  el.className = 'message bot-message';
  el.innerHTML = `
    <div class="avatar">🎓</div>
    <div class="bubble">
      <div class="bot-text"><p><em>Thinking and retrieving university documents...</em></p></div>
    </div>
  `;
  return el;
}

function renderBotError(messageEl, errorMessage) {
  const bubble = messageEl.querySelector('.bubble');
  bubble.innerHTML = `
    <div class="bot-text" style="color: var(--danger);">
      <p>⚠️ <strong>Error:</strong> ${escapeHtml(errorMessage)}</p>
    </div>
  `;
}

function renderBotResponse(messageEl, data) {
  const bubble = messageEl.querySelector('.bubble');
  const answer = data.answer || "No response generated.";
  const sources = data.sources || [];
  const trace = data.trace;

  let html = `<div class="bot-text">${formatMarkdown(answer)}</div>`;

  // Citations Block
  if (sources.length > 0) {
    html += `
      <div class="citations-box">
        <h5>Verified Sources (${sources.length})</h5>
    `;
    sources.forEach(src => {
      html += `
        <div class="source-item">
          <strong>📄 ${escapeHtml(src.source)}</strong> (${escapeHtml(src.page_or_section)})<br>
          <small style="color: var(--text-muted); font-style: italic;">"${escapeHtml(src.snippet)}"</small>
        </div>
      `;
    });
    html += `</div>`;
  }

  // Collapsible Teaching Trace Accordion
  if (trace) {
    html += renderTraceAccordion(trace);
  }

  bubble.innerHTML = html;
}

function renderTraceAccordion(trace) {
  const guardItems = (trace.guardrails || []).map(g => {
    const tagClass = g.passed ? "tag-pass" : "tag-block";
    const statusText = g.passed ? "PASSED" : "BLOCKED";
    return `<div><span class="trace-tag ${tagClass}">${statusText}</span> <strong>${escapeHtml(g.guard)}:</strong> ${escapeHtml(g.reason)}</div>`;
  }).join('');

  const initialItems = (trace.initial_retrieval || []).map((c, i) => `
    <li><strong>#${i + 1}</strong> [Score: ${c.relevance_score}] ${escapeHtml(c.source)} (${escapeHtml(c.page_or_section)})</li>
  `).join('');

  const rerankItems = (trace.reranked_retrieval || []).map((c, i) => `
    <li><strong>#${i + 1}</strong> [Rerank: ${c.rerank_score ?? c.relevance_score}] ${escapeHtml(c.source)} (${escapeHtml(c.page_or_section)})</li>
  `).join('');

  const mcpInfo = trace.mcp_tool_used ? `
    <div class="trace-section">
      <strong>MCP Tool Invocation:</strong> <code>${escapeHtml(trace.mcp_tool_used)}</code>
      <pre style="margin-top: 4px;">${escapeHtml(JSON.stringify(trace.mcp_result, null, 2))}</pre>
    </div>
  ` : '';

  const timingInfo = Object.entries(trace.timings_ms || {})
    .map(([k, v]) => `${k}: ${v}ms`)
    .join(' | ');

  return `
    <details class="trace-accordion">
      <summary>🔍 How CampusGPT answered (Teaching Trace)</summary>
      <div class="trace-body">
        <div class="trace-section">
          <strong>🛡️ Guardrail Checkpoints:</strong>
          <div style="margin-top: 6px; display: flex; flex-direction: column; gap: 4px;">
            ${guardItems || 'None'}
          </div>
        </div>
        
        <div class="trace-section" style="display: flex; gap: 16px;">
          <div style="flex: 1;">
            <strong>Step 4: Vector Candidates (${trace.initial_retrieval ? trace.initial_retrieval.length : 0})</strong>
            <ol style="margin-left: 18px; margin-top: 4px;">${initialItems || '<li>None</li>'}</ol>
          </div>
          <div style="flex: 1;">
            <strong>Step 5: After Reranking (${trace.reranked_retrieval ? trace.reranked_retrieval.length : 0})</strong>
            <ol style="margin-left: 18px; margin-top: 4px;">${rerankItems || '<li>None</li>'}</ol>
          </div>
        </div>

        ${mcpInfo}

        <div style="font-size: 11px; color: var(--text-muted); text-align: right;">
          ⚡ Timings: ${escapeHtml(timingInfo)}
        </div>
      </div>
    </details>
  `;
}

function setLoadingState(loading) {
  userInput.disabled = loading;
  sendBtn.disabled = loading;
  if (!loading) userInput.focus();
}

function scrollToBottom() {
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHtml(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatMarkdown(text) {
  if (!text) return '';
  let safe = escapeHtml(text);
  // Bold
  safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Newlines to breaks
  safe = safe.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
  return `<p>${safe}</p>`;
}
