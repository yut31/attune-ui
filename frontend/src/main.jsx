import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Dashboard } from './Dashboard.js';
import { createRestClient } from './rest.js';
import { createTransport } from './transport.js';
import { emptyState } from './state.js';
import './style.css';
const rest = createRestClient();
function App() {
  const [state, setState] = useState(emptyState);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  useEffect(() => {
    const transport = createTransport({ rest, onState: setState });
    transport.start();
    return () => transport.stop();
  }, []);
  async function command(name) {
    setBusy(true); setError(null);
    try { await rest[name](AbortSignal.timeout(10000)); }
    catch (e) { setError(`${e.message}. Command outcome may be unknown; inspect session state before retrying.`); }
    finally { setBusy(false); }
  }
  return <Dashboard state={state} busy={busy} commandError={error} command={command} />;
}
createRoot(document.getElementById('root')).render(<App />);
