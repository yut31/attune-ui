"""Join PVT lapse inference and auditory attention inference on aligned windows.

Call with separately preprocessed windows from the SAME recording ending at the
same instant. Never feed the 64 Hz AAD signal into the 128 Hz PVT model.
The lapse score is reported alongside the talker decision; it does not yet
change audio gain. Requires nova2026 to be installed in this Python environment.
"""
from dataclasses import asdict, dataclass

import numpy as np

from config import FS, DECISION_WINDOW_S
from decoder import RealtimeDecoder, LAGS, _corr
from attention_mixer import AttentionMixer
from nova2026.inference import LapsePredictor


@dataclass(frozen=True)
class CombinedDecision:
    end_time_s: float
    lapse_score: float
    attended_talker: int
    correlations: tuple[float, float]

    def to_dict(self):
        return asdict(self)


class CombinedPipeline:
    def __init__(self, lapse_checkpoint, aad_weights, *, aad_channels):
        self.lapse = LapsePredictor(lapse_checkpoint)
        self.aad_channels = list(aad_channels)
        if not self.aad_channels or len(set(self.aad_channels)) != len(self.aad_channels):
            raise ValueError("AAD electrode names must be unique and ordered as in training")
        weights = np.asarray(aad_weights, dtype=float)
        if weights.shape != (len(self.aad_channels) * len(LAGS),) or not np.isfinite(weights).all():
            raise ValueError("AAD weights do not match the electrode/lag configuration")
        self.decoder = RealtimeDecoder(weights)
        self.mixer = AttentionMixer()
        self.last_end_time = None

    def decide(self, *, lapse_window, lapse_channels, lapse_sample_rate,
               lapse_units, lapse_preprocessing, lapse_end_time_s,
               aad_window, aad_channels, aad_sample_rate, aad_preprocessing,
               envelopes, aad_end_time_s, envelope_end_time_s):
        """AAD input: (time, channels), 1–9 Hz bandpass + per-channel z-score.

        Envelopes: (2, time), already aligned with EEG, at 64 Hz and bandpassed
        1–9 Hz. Channel names are a contract provided from the training recording;
        old .npy AAD weights do not contain that information themselves.
        The PVT window covers the last 2 seconds; AAD covers 15 seconds.
        """
        times = np.asarray([lapse_end_time_s, aad_end_time_s, envelope_end_time_s], dtype=float)
        if not np.isfinite(times).all() or np.ptp(times) > 1e-6:
            raise ValueError("Both EEG windows and audio envelopes must end at the same timestamp")
        if self.last_end_time is not None and aad_end_time_s <= self.last_end_time:
            raise ValueError("Decision timestamps must increase")
        if list(aad_channels) != self.aad_channels or aad_sample_rate != FS:
            raise ValueError("AAD electrode order/sample rate differs from its training contract")
        if aad_preprocessing != "aad_1_9Hz_zscore":
            raise ValueError("AAD window must use its own bandpass and z-score preprocessing")
        eeg = np.asarray(aad_window, dtype=float)
        env = np.asarray(envelopes, dtype=float)
        n = int(DECISION_WINDOW_S * FS)
        if eeg.shape != (n, len(self.aad_channels)) or env.shape != (2, n):
            raise ValueError(f"Expected {n} aligned AAD samples and two envelope tracks")
        if not np.isfinite(eeg).all() or not np.isfinite(env).all():
            raise ValueError("AAD input contains nonfinite samples")
        lapse_score = self.lapse.predict(
            lapse_window, channels=lapse_channels, sample_rate=lapse_sample_rate,
            units=lapse_units, preprocessing=lapse_preprocessing,
        )
        # Positive EEG lags need future samples. Omit the unsupported trailing
        # edge, instead of scoring reconstruction based on zero-filled EEG.
        valid = n - int(max(LAGS))
        recon = self.decoder.reconstruct(eeg)[:valid]
        corrs = tuple(_corr(recon, track[:valid]) for track in env)
        attended = self.mixer.set_decision(corrs)
        self.last_end_time = float(aad_end_time_s)
        return CombinedDecision(float(aad_end_time_s), lapse_score, attended, corrs)

    def mix(self, talker_a, talker_b):
        """Use the existing ramping AAD mixer between joint decisions."""
        return self.mixer.process([talker_a, talker_b])
