import { request } from './api.js';
import { el, clear, title, human, notice } from './dom.js';
export async function dashboard(project) {
  title(`${project.title} overview`, project.tagline);
  const root = clear();
  try {
    const data = await request('/api/dashboard');
    const metrics = el('div', undefined, 'metrics');
    for (const m of data.metrics) {
      const card = el('article', undefined, 'metric');
      card.append(el('small', m.label), el('strong', typeof m.value === 'object' ? Object.entries(m.value).map(([k, v]) => `${k} ${v.toLocaleString()}`).join(' · ') : Number(m.value).toLocaleString()), el('span', 'LIVE LOCAL DATABASE', 'caption'));
      metrics.append(card);
    }
    root.append(metrics);
    const grid = el('div', undefined, 'two-column');
    const chartPanel = el('article', undefined, 'panel');
    chartPanel.append(el('h2', 'Operational snapshot'), el('p', 'Recorded values and configured targets. No predicted outcomes.', 'small'));
    const canvas = el('canvas', undefined, 'chart');
    canvas.setAttribute('aria-label', data.bars.map(b => `${b.label}: ${b.value}; target ${b.target}`).join('; '));
    canvas.setAttribute('role', 'img');
    chartPanel.append(canvas);
    const directory = el('article', undefined, 'panel');
    directory.append(el('h2', 'Resource inventory'));
    const counts = el('div', undefined, 'counts');
    for (const [key, value] of Object.entries(data.counts)) {
      const n = el('div', undefined, 'count');
      n.append(el('span', human(key)), el('strong', value));
      counts.append(n);
    }
    directory.append(counts);
    grid.append(chartPanel, directory);
    root.append(grid);
    root.append(el('p', project.limitation, 'intro'));
    const draw = () => {
      const dpr = window.devicePixelRatio || 1;
      const width = canvas.clientWidth || 400;
      canvas.width = width * dpr;
      canvas.height = 220 * dpr;
      const c = canvas.getContext('2d');
      c.scale(dpr, dpr);
      c.font = '12px system-ui';
      const max = Math.max(1, ...data.bars.flatMap(b => [b.value, b.target]));
      const accent = getComputedStyle(document.body).getPropertyValue('--accent');
      data.bars.slice(0, 5).forEach((bar, i) => {
        const y = 18 + i * 39;
        c.fillStyle = '#9eaac0';
        c.fillText(`${bar.label} · ${bar.value} / ${bar.target}`, 0, y);
        c.fillStyle = '#2c3548';
        c.fillRect(0, y + 9, width, 7);
        c.fillStyle = accent;
        c.fillRect(0, y + 9, Math.max(2, width * bar.value / max), 7);
      });
    };
    requestAnimationFrame(draw);
  } catch (error) {
    notice(error.message, true);
    root.append(el('p', 'Connect with the local operator token to view this workspace.', 'empty'));
  }
}
