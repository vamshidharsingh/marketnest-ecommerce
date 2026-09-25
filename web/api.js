let token = sessionStorage.getItem('operator-token') || '';
export function setToken(value) {
  token = value;
  sessionStorage.setItem('operator-token', value);
}
export async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers
    }
  });
  const contentType = response.headers.get('Content-Type') || '';
  const data = contentType.includes('application/json') ? await response.json() : await response.text();
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}
export const command = (action, data) => request(`/api/workflows/${action}`, {
  method: 'POST',
  body: JSON.stringify(data)
});
export function downloadCSV(resource) {
  return request(`/api/export/${resource}`).then(text => {
    const url = URL.createObjectURL(new Blob([text], {
      type: 'text/csv'
    }));
    const a = document.createElement('a');
    a.href = url;
    a.download = `${resource}.csv`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
}
