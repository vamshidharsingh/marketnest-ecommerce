import { request, downloadCSV } from './api.js';
import { $, el, clear, title, human, button, notice } from './dom.js';
let closeRecord = () => {};
$('record-close').addEventListener('click', () => $('record-dialog').close());
export async function resourceView(name, schema) {
  title(human(name), schema.description);
  const root = clear();
  let page = 0;
  let search = '';
  let generation = 0;
  const panel = el('article', undefined, 'panel');
  const tools = el('div', undefined, 'resource-toolbar');
  const filter = el('input');
  filter.placeholder = 'Search records…';
  filter.setAttribute('aria-label', 'Search records');
  filter.type = 'search';
  tools.append(filter, button('Search', () => {
    search = filter.value;
    page = 0;
    load();
  }), button('Export CSV', () => downloadCSV(name).catch(e => notice(e.message, true))));
  if (schema.writable) tools.append(button('New record', () => edit(null), 'primary'));
  panel.append(tools);
  const wrap = el('div', undefined, 'table-wrap');
  panel.append(wrap);
  const pages = el('div', undefined, 'pagination');
  panel.append(pages);
  root.append(panel);
  if (!schema.writable) root.append(el('p', 'This resource is maintained by business workflows. Open Workflows to perform an operation.', 'intro'));
  async function load() {
    const sequence = ++generation;
    try {
      const data = await request(`/api/resources/${name}?limit=20&offset=${page * 20}&search=${encodeURIComponent(search)}`);
      if (sequence !== generation || !panel.isConnected) return;
      wrap.replaceChildren();
      pages.replaceChildren();
      if (!data.items.length) {
        wrap.append(el('p', 'No records match this view.', 'empty'));
      } else {
        const table = el('table');
        const thead = el('thead');
        const head = el('tr');
        const columns = ['id', ...Object.keys(schema.fields)];
        for (const col of columns) head.append(el('th', human(col)));
        if (schema.writable) head.append(el('th', 'Actions'));
        thead.append(head);
        table.append(thead);
        const tbody = el('tbody');
        for (const row of data.items) {
          const tr = el('tr');
          for (const col of columns) {
            const td = el('td', row[col]);
            td.title = String(row[col]);
            tr.append(td);
          }
          if (schema.writable) {
            const td = el('td');
            td.append(button('Edit', () => edit(row)), button('Delete', async () => {
              if (!confirm(`Delete record ${row.id}?`)) return;
              try {
                await request(`/api/resources/${name}/${row.id}?version=${row._version}`, {
                  method: 'DELETE'
                });
                await load();
              } catch (e) {
                notice(e.message, true);
              }
            }));
            tr.append(td);
          }
          tbody.append(tr);
        }
        table.append(tbody);
        wrap.append(table);
      }
      const prev = button('Previous', () => {
        page--;
        load();
      });
      prev.disabled = page === 0;
      const next = button('Next', () => {
        page++;
        load();
      });
      next.disabled = data.items.length < 20;
      pages.append(prev, el('span', `Page ${page + 1} · ${data.total} total records`, 'small'), next);
    } catch (e) {
      notice(e.message, true);
    }
  }
  function edit(row) {
    $('record-title').textContent = row ? 'Edit record' : 'New record';
    $('record-error').textContent = '';
    const fields = $('record-fields');
    fields.replaceChildren();
    const inputs = {};
    for (const [key, rule] of Object.entries(schema.fields)) {
      const label = el('label', human(key));
      let input;
      if (rule.enum) {
        input = el('select');
        for (const option of rule.enum) {
          const o = el('option', option);
          o.value = option;
          input.append(o);
        }
      } else {
        input = el('input');
        input.type = rule.type === 'string' ? 'text' : 'number';
        if (rule.type !== 'string') {
          input.step = rule.type === 'integer' ? '1' : 'any';
          if (rule.minimum !== undefined) input.min = rule.minimum;
          if (rule.maximum !== undefined) input.max = rule.maximum;
        }
        if (rule.format === 'date') input.type = 'date';
        if (rule.format === 'email') input.type = 'email';
        if (rule.ref) input.placeholder = `Existing ${rule.ref} id`;
        if (rule.format === 'datetime') input.placeholder = '2027-01-15T09:00:00+00:00';
      }
      input.name = key;
      input.required = true;
      input.value = row ? row[key] : rule.enum ? rule.enum[0] : '';
      label.append(input);
      fields.append(label);
      inputs[key] = input;
    }
    closeRecord = async event => {
      event.preventDefault();
      const save = $('record-save');
      save.disabled = true;
      try {
        const payload = {};
        for (const [key, rule] of Object.entries(schema.fields)) payload[key] = rule.type === 'string' ? inputs[key].value : Number(inputs[key].value);
        if (row) payload._version = row._version;
        await request(`/api/resources/${name}${row ? '/' + row.id : ''}`, {
          method: row ? 'PUT' : 'POST',
          body: JSON.stringify(payload)
        });
        $('record-dialog').close();
        await load();
      } catch (e) {
        $('record-error').textContent = e.message;
      } finally {
        save.disabled = false;
      }
    };
    $('record-dialog').showModal();
  }
  await load();
}
$('record-form').addEventListener('submit', event => closeRecord(event));
