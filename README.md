# ATTUNE UI

ATTUNE is the user-facing Neuro-Adaptive Hearing dashboard. It is a plain HTML/CSS/JavaScript interface with no React, Vite, npm, or external resources required.

The production copy currently lives at `neuro-attention/src/ui.html`. The UI expects a same-origin `GET /state` endpoint. It uses the current backend fields documented in `INTEGRATION.md` and understands the optional future `lapse_score` field.

When `lapse_score` is missing or invalid, Real Mode shows `Awaiting pipeline` and does not invent a value. Demo Mode is clearly labeled and uses deterministic simulated attention, vigilance, EEG, and signal-quality illustrations. Demo values are not participant measurements or real EEG assessments. Signal quality and artifact status are simulated in Demo Mode only; the real pipeline currently does not provide them.

To integrate the UI, serve this `ui.html` from the same origin as the backend endpoint, or replace the existing production `neuro-attention/src/ui.html` with this verified copy. Preserve the `/state` contract and keep Demo Mode disclosures visible.
