export const $ = id => document.getElementById(id);
export function el(tag, text, cls) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = String(text);
  if (cls) node.className = cls;
  return node;
}
export function notice(message, error = false) {
  $('notice').textContent = message;
  $('notice').classList.toggle('error', error);
}
export function title(value, subtitle = '') {
  $('title').textContent = value;
  $('subtitle').textContent = subtitle;
  $('breadcrumb').textContent = value;
}
export function clear() {
  $('content').replaceChildren();
  notice('');
  return $('content');
}
export function human(value) {
  return value.replaceAll('_', ' ').replace(/\b\w/g, s => s.toUpperCase());
}
export function button(text, callback, cls = 'secondary') {
  const b = el('button', text, cls);
  b.type = 'button';
  b.addEventListener('click', callback);
  return b;
}
