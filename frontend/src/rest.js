export function createRestClient(fetchImpl = globalThis.fetch) {
  async function request(path, method = 'GET', signal) {
    const response = await fetchImpl(`/api/${path}`, { method, signal, cache: 'no-store' });
    if (!response.ok) throw Error(`HTTP ${response.status} (${path})`);
    return response.json();
  }
  return {
    health: signal => request('health', 'GET', signal),
    state: signal => request('state', 'GET', signal),
    start: signal => request('session/start', 'POST', signal),
    stop: signal => request('session/stop', 'POST', signal),
  };
}
