import React from 'react';
import { FeedbackPanel } from './FeedbackPanel.js';
const h = React.createElement;
export function Dashboard({ state, command, busy = false, commandError = null }) {
  const inactive = state.stale || state.streams.some(s => s.type === 'session' && ['stopped', 'error'].includes(s.values.status));
  return h('main', null,
    h('h1', null, 'ATTUNE — Transport Debug'),
    h('p', null, 'Neuro-Adaptive Hearing · Python mock data only. No participant measurements or audio playback.'),
    h('p', { role: 'status' }, `Connection: ${state.connection} · ${state.stale ? 'STALE / unavailable live connection' : 'Live transport'}`),
    h('button', { disabled: busy || state.connection !== 'connected', onClick: () => command('start') }, 'Start mock session'),
    ' ', h('button', { disabled: busy || state.connection !== 'connected', onClick: () => command('stop') }, 'Stop session'),
    commandError && h('p', { role: 'alert' }, commandError),
    h('p', null, `Session: ${state.sessionId ?? 'none'} · Sequence: ${state.sequence} · Rejected packets: ${state.rejected}`),
    state.error && h('p', null, `Transport note: ${state.error}`),
    h('p', null, 'null = unavailable; unknown packet types are retained without interpretation. Timestamps are session-relative seconds.'),
    state.streams.length === 0 && h('p', null, 'Waiting for result packets.'),
    h(FeedbackPanel, { stream: state.streams.findLast(s => s.type === 'feedback'), stale: state.stale, inactive: state.streams.some(s => s.type === 'session' && ['stopped', 'error'].includes(s.values.status)) }),
    ...state.streams.filter(stream => stream.type !== 'feedback').map(stream => h('section', { key: JSON.stringify([stream.source, stream.type]) },
      h('h2', null, stream.type === 'prediction' ? 'Prediction result' : `${stream.type} / ${stream.source}`),
      stream.type === 'prediction' ? h(React.Fragment, null,
        stream.simulated === true && stream.values.metadata.mock === true && h('strong', {className: 'development-badge'}, 'SIMULATED · DEVELOPMENT ONLY · NO SCIENTIFIC INTERPRETATION'),
        h('p', {role: 'status'}, inactive ? 'Historical prediction — not current' : 'Current session prediction'),
        h('p', null, `Provider: ${stream.values.providerId ?? stream.source} · Task: ${stream.values.task ?? 'unavailable'} · Status: ${stream.values.status ?? 'unavailable'}`),
        h('p', null, stream.values.outputs.map(output => `${output.name ?? 'output'} · Value: ${String(output.value)} · Semantic type: ${output.semanticType ?? 'unavailable'}`).join(' · ') || stream.values.reasons.join(', ')),
        h('pre', null, JSON.stringify(stream.values, null, 2))) : h(React.Fragment, null,
        h('p', null, `${stream.known ? 'Registered decoder' : 'Unknown packet fallback'} · ${stream.simulated === true ? 'SIMULATED' : 'Simulation status unavailable / not declared'} · t=${stream.timestamp} · seq=${stream.sequence}`),
        h('pre', null, JSON.stringify(stream.values, null, 2))))),
  );
}
