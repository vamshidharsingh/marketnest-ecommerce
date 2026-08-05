import { $ } from './dom.js';
export function applyTheme(project) {
  document.body.classList.add(project.domain);
  $('brand').textContent = project.title;
  document.title = `${project.title} · Operations Studio`;
}
