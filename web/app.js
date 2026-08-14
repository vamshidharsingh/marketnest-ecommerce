import { request, setToken } from './api.js';
import { $, el, clear, title, button, human, notice } from './dom.js';
import { applyTheme } from './theme.js';
import { dashboard } from './dashboard.js';
import { resourceView } from './resource.js';
import { workflowView } from './workflow.js';
let meta;
let current = 'overview';
async function navigate(view) {
  current = view;
  for (const b of document.querySelectorAll('nav button')) b.classList.toggle('active', b.dataset.view === view);
  if (view === 'overview') await dashboard(meta.project);else if (view === 'workflows') workflowView(meta.project);else if (view === 'audit') {
    title('Audit trail', 'Metadata-only change history; payload values are excluded.');
    const root = clear();
    try {
      const data = await request('/api/audit');
      const panel = el('div', undefined, 'table-wrap');
      const table = el('table');
      const head = el('tr');
      for (const name of ['Sequence', 'Action', 'Resource', 'Record', 'Timestamp']) head.append(el('th', name));
      const thead = el('thead');
      thead.append(head);
      table.append(thead);
      const body = el('tbody');
      for (const row of data.items) {
        const tr = el('tr');
        for (const name of ['sequence', 'action', 'resource', 'record_id', 'occurred_at']) tr.append(el('td', row[name]));
        body.append(tr);
      }
      table.append(body);
      panel.append(table);
      root.append(panel);
    } catch (e) {
      notice(e.message, true);
    }
  } else await resourceView(view, meta.schemas[view]);
}
function nav(id, text, view) {
  const b = button(text, () => navigate(view));
  b.dataset.view = view;
  $(id).append(b);
}
$('auth-button').addEventListener('click', () => $('auth-dialog').showModal());
$('auth-close').addEventListener('click', () => $('auth-dialog').close());
$('auth-form').addEventListener('submit', async event => {
  event.preventDefault();
  setToken($('token').value);
  $('auth-dialog').close();
  try {
    await request('/api/dashboard');
    $('connection').textContent = 'Connected · local operator';
    await navigate(current);
  } catch (e) {
    $('connection').textContent = 'Access denied';
    notice(e.message, true);
  }
});
try {
  meta = await request('/api/meta');
  applyTheme(meta.project);
  nav('navigation', 'Overview', 'overview');
  nav('navigation', 'Workflows', 'workflows');
  nav('navigation', 'Audit trail', 'audit');
  for (const name of Object.keys(meta.schemas)) nav('resources', human(name), name);
  await navigate('overview');
} catch (e) {
  title('Workspace unavailable');
  notice(e.message, true);
}
