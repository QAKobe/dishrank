const API_BASE = location.origin;

async function pingHealth() {
    try {
        const r = await fetch(`${API_BASE}/health`, { cache: "no-store" });
        const ok = r.ok && (await r.json()).ok;
        setStatus(ok ? "API healthy ✅" : "API not ok", ok);
    } catch {
        setStatus("API unreachable ❌", false);
    }
}
function setStatus(text, ok) {
    document.getElementById('health').textContent = text;
    document.getElementById('health').className = ok ? 'ok' : 'err';
    document.getElementById('barStatus').textContent = text;
}



async function loadDishes() {
    const tbody = document.getElementById('dishRows');
    tbody.innerHTML = '<tr><td colspan="5" class="muted">Loading…</td></tr>';
    try {
        const r = await fetch(`${API_BASE}/dishes`, { cache: "no-store" });
        if (!r.ok) throw new Error(r.status);
        const rows = await r.json();
        document.getElementById('count').textContent = `${rows.length} dish(es)`;
        tbody.innerHTML = rows.map(d => `
          <tr>
            <td>${d.id ?? ''}</td>
            <td>${escapeHtml(d.place)}</td>
            <td>
              ${escapeHtml(d.name)}<br>
              <span class="muted" style="font-size:.8em">
                     ${escapeHtml(d.nickname ?? '')}
             </span>
             </td>
            <td>${escapeHtml(d.category ?? '')}</td>
            <td>${formatRating(d.rating)}</td>
          </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" class="err">Failed to load dishes (${e.message})</td></tr>`;
    }
}

function formatRating(r) { return (typeof r === 'number' && !isNaN(r)) ? r.toFixed(1) : ''; }
function escapeHtml(s) {
    return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

document.getElementById('dishForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const msg = document.getElementById('formMsg');
    msg.textContent = 'Saving…';
    const payload = {
        place: form.place.value.trim(),
        name: form.name.value.trim(),
        category: form.category.value.trim(),
        rating: Number(form.rating.value),
        nickname: (form.nickname.value.trim() || "Anonymous")
    };
    try {
        if (!payload.place || !payload.name || isNaN(payload.rating)) {
            throw new Error('Fill all required fields');
        }
        const r = await fetch(`${API_BASE}/dishes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        msg.textContent = '✅ Added';
        form.reset();
        await loadDishes();
    } catch (e) {
        msg.textContent = '❌ ' + e.message;
    }
});
document.getElementById('refreshBtn').addEventListener('click', loadDishes);

// initial load
pingHealth();
loadDishes();
loadDishes();