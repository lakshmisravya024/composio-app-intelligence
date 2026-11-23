
let allRows = [];

const $ = (s) => document.querySelector(s);

async function load() {
    try {
        const response = await fetch('../data/research_results.json');

        if (!response.ok) {
            throw new Error('Could not load research_results.json');
        }

        allRows = await response.json();

        render();
        updateMetrics();
        renderInsights();

        try {
            const verificationResponse =
                await fetch('../data/verification.json');

            if (!verificationResponse.ok) {
                throw new Error('Verification file unavailable');
            }

            const v = await verificationResponse.json();

            $('#verified').textContent =
                v.status === 'complete' ? `${v.accuracy}%` : 'NOT RUN';

            $('#verification').textContent =
                v.status === 'complete'
                    ? `${v.checked} checked · ${v.correct} correct · ${v.accuracy}% field agreement`
                    : 'Verification has not been completed.';

        } catch {
            $('#verified').textContent = 'NOT RUN';
            $('#verification').textContent =
                'Verification has not been completed.';
        }

    } catch (error) {
        $('#patterns').textContent =
            'Unable to load research data. Check the JSON file path and run your local server.';
        console.error(error);
    }
}

function updateMetrics() {
    $('#total').textContent = `${allRows.length} apps in dataset`;

    $('#review').textContent =
        allRows.filter(x => x.human_review_required).length;

    $('#evidence').textContent =
        allRows.filter(x => (x.evidence || []).length > 0).length;
}

function countBy(field) {
    const counts = {};

    allRows.forEach(row => {
        let value = row[field];

        if (Array.isArray(value)) {
            value = value.join(', ') || 'Unknown';
        }

        value = String(value || 'Unknown');

        counts[value] = (counts[value] || 0) + 1;
    });

    return counts;
}

function renderBars(title, counts) {
    const entries = Object.entries(counts)
        .sort((a, b) => b[1] - a[1]);

    const max = Math.max(...entries.map(x => x[1]), 1);

    return `
        <div class="insight-card">
            <h3>${esc(title)}</h3>
            ${entries.map(([name, count]) => `
                <div class="bar-row">
                    <div class="bar-label">
                        <span>${esc(name)}</span>
                        <b>${count}</b>
                    </div>
                    <div class="bar-track">
                        <div class="bar-fill"
                             style="width:${count / max * 100}%">
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderInsights() {
    const patterns = $('#patterns');

    const html = `
        <div class="insight-grid">
            ${renderBars('API Type', countBy('api_type'))}
            ${renderBars('Authentication Methods', countBy('auth_methods'))}
            ${renderBars('MCP Availability', countBy('mcp_status'))}
            ${renderBars('Buildability', countBy('buildability'))}
            ${renderBars('Access Model', countBy('access_model'))}
        </div>
    `;

    patterns.innerHTML = html;
}

function render() {
    const q = ($('#filter').value || '').toLowerCase();

    const rows = allRows.filter(x =>
        (x.app || '').toLowerCase().includes(q) ||
        (x.category || '').toLowerCase().includes(q)
    );

    $('#rows').innerHTML = rows.map(x => `
        <tr>
            <td><b>${esc(x.app)}</b></td>
            <td>${esc(x.category)}</td>
            <td>${esc((x.auth_methods || []).join(', '))}</td>
            <td>${esc(x.access_model)}</td>
            <td>${esc(x.api_type)} / ${esc(x.api_breadth)}</td>
            <td>${esc(x.mcp_status)}</td>
            <td>${esc(x.buildability)}</td>
            <td>
                ${(x.evidence || []).map(e =>
                    `<a href="${esc(e.url)}"
                        target="_blank"
                        rel="noopener">source</a>`
                ).join(' · ') || '—'}
            </td>
        </tr>
    `).join('') || '<tr><td colspan="8">No matching apps.</td></tr>';
}

function esc(s) {
    return String(s ?? '—').replace(/[&<>"']/g, c => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }[c]));
}

$('#filter').addEventListener('input', render);

load();
