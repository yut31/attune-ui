import React from 'react';
const h = React.createElement;
const value = (v, suffix = '') => typeof v === 'number' && Number.isFinite(v) ? `${v}${suffix}` : 'Unavailable';
export function StatusPill({ children }) { return h('span', { className: 'status-pill' }, children); }
export function Header({ state, session }) {
  return h('header', { className: 'dashboard-header' },
    h('div', null, h('h1', null, 'ATTUNE'), h('p', null, 'Neuro-Adaptive Hearing')),
    h('div', { className: 'header-status', role: 'status' },
      h(StatusPill, null, `Connection: ${state.connection}`),
      h(StatusPill, null, `Session: ${session ?? 'awaiting'}`),
      state.stale && h(StatusPill, null, 'STALE / unavailable live connection')));
}
export function VoiceSource({ speaker, selected, correlation }) {
  return h('div', { className: `voice-source${selected ? ' selected' : ''}`, 'aria-label': `Speaker ${speaker}${selected ? ', focused' : ''}` },
    h('div', { className: 'voice-orbit', 'aria-hidden': true }, h('span', null, speaker)),
    h('h3', null, `Speaker ${speaker}`), h('p', null, selected ? 'Focused speaker' : 'Voice source'),
    h('div', { className: 'correlation' }, h('span', null, 'Correlation'), h('strong', null, value(correlation))));
}
export function PredictionCard({ stream, inactive }) {
  const data = stream?.values ?? {};
  const decision = inactive ? 'unavailable' : (Object.hasOwn(data, 'decision') ? data.decision : data.attended) ?? 'unavailable';
  const label = ['A', 'B'].includes(decision) ? `Focused on Speaker ${decision}` : decision === 'uncertain' ? 'Focus is uncertain' : 'Awaiting a current prediction';
  return h('section', { className: 'card focus-card', 'aria-label': 'Focus prediction' },
    h('div', { className: 'card-heading' }, h('h2', null, 'Focus prediction'), h(StatusPill, null, stream?.simulated ? 'SIMULATED' : 'Source status not declared')),
    h('p', { className: 'focus-title' }, label),
    h('div', { className: 'voice-grid' }, ...['A', 'B'].map(speaker => h(VoiceSource, { key: speaker, speaker, selected: decision === speaker, correlation: data[`correlation${speaker}`] }))),
    h('div', { className: 'focus-summary' }, h('span', null, `Prediction state: ${decision}`), h('span', null, 'Confidence: Unavailable')),
    inactive && h('p', { className: 'muted' }, 'Session inactive or connection stale. Values are historical.'));
}
export function StatusCard({ title, rows }) {
  return h('section', { className: 'card' }, h('h2', null, title), h('dl', { className: 'metric-list' }, ...rows.map(([label, content]) => h('div', { key: label }, h('dt', null, label), h('dd', null, content ?? 'Unavailable')))));
}
export function LiveSignalPanel({ stream, inactive }) {
  const samples = stream?.values.samples?.[0];
  // Display coordinates only, fixed illustrative scale; no filtering or inference.
  const points = samples?.map((v, i) => `${i * 600 / Math.max(1, samples.length - 1)},${60 - Math.max(-1, Math.min(1, v)) * 45}`).join(' ');
  return h('section', { className: 'card signal-card' },
    h('div', { className: 'card-heading' }, h('h2', null, 'Live signal / history'), h(StatusPill, null, inactive ? 'Historical / inactive' : stream?.simulated ? 'SIMULATED display' : 'Display data')),
    samples?.length > 1 ? h('svg', { viewBox: '0 0 600 120', role: 'img', 'aria-label': 'EEG display samples, first channel', className: 'signal-trace' }, h('polyline', { points, fill: 'none', stroke: 'currentColor', strokeWidth: 2 })) : h('div', { className: 'signal-empty' }, 'Awaiting EEG display data'),
    h('p', { className: 'muted' }, samples?.length > 1 ? `First channel · ${stream.values.channels?.[0] ?? 'Unnamed'} · t=${stream.timestamp} s · Display scale ±1 (clipped)` : 'A space for incoming signal samples. No measurements available yet.'));
}
export function SessionControls({ state, command, busy, commandError }) {
  return h('section', { className: 'card session-controls', 'aria-label': 'Session controls' },
    h('div', null, h('h2', null, 'Your session'), h('p', null, 'Development stream · no hardware or audio playback')),
    h('div', { className: 'button-group' }, h('button', { className: 'primary', disabled: busy || state.connection !== 'connected', onClick: () => command('start') }, 'Start mock session'), h('button', { disabled: busy || state.connection !== 'connected', onClick: () => command('stop') }, 'Stop session')),
    commandError && h('p', { role: 'alert' }, commandError));
}
export { value as displayValue };
