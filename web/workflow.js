import { command } from './api.js';
import { el, clear, title, human } from './dom.js';
export function workflowView(project) {
  title('Business workflows', 'Execute transactional operations with explicit inputs.');
  const root = clear();
  const grid = el('div', undefined, 'workflow-grid');
  for (const action of project.actions) {
    const form = el('form', undefined, 'panel');
    form.append(el('h3', action.title));
    const inputs = {};
    for (const [name, value] of Object.entries(action.example)) {
      const label = el('label', human(name));
      const input = el('input');
      input.name = name;
      input.value = value;
      input.type = typeof value === 'number' ? 'number' : 'text';
      if (typeof value === 'number') {
        input.min = '1';
        input.step = '1';
      }
      input.required = name !== 'coupon_code';
      label.append(input);
      form.append(label);
      inputs[name] = input;
    }
    const submit = el('button', 'Run workflow');
    const result = el('pre', 'Results appear here.');
    result.setAttribute('aria-live', 'polite');
    form.append(submit, result);
    form.addEventListener('submit', async event => {
      event.preventDefault();
      submit.disabled = true;
      try {
        const payload = {};
        for (const [name, value] of Object.entries(action.example)) payload[name] = typeof value === 'number' ? Number(inputs[name].value) : inputs[name].value;
        const data = await command(action.name, payload);
        result.textContent = JSON.stringify(data, null, 2);
      } catch (e) {
        result.textContent = e.message;
      } finally {
        submit.disabled = false;
      }
    });
    grid.append(form);
  }
  root.append(grid, el('p', 'Reference and key values make retried operations safe. Change them when you intend to create a new independent operation. Returned IDs can be copied into later workflow forms.', 'intro'));
}
