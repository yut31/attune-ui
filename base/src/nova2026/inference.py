"""Checkpoint contract for inference on PVT-preprocessed EEG windows.

Inputs are already filtered 0.5–45 Hz, resampled to 128 Hz, ordered by the
training electrode names, and expressed in microvolts (as in labelPVT.py).
"""
from pathlib import Path

import numpy as np
import torch

from nova2026.architecture.cnn import EEGNet


def save_checkpoint(model, path, channels):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "format_version": 1,
        "state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
        "channels": list(channels),
        "sample_rate": 128,
        "samples": 256,
        "units": "uV",
        "preprocessing": "pvt_0.5_45Hz",
        "classes": ["usual_response", "slowest_session_decile"],
    }, path)


class LapsePredictor:
    def __init__(self, path):
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
        expected = {"format_version": 1, "sample_rate": 128, "samples": 256,
                    "units": "uV", "preprocessing": "pvt_0.5_45Hz",
                    "classes": ["usual_response", "slowest_session_decile"]}
        for key, value in expected.items():
            if checkpoint.get(key) != value:
                raise ValueError(f"Incompatible lapse checkpoint: {key} must be {value!r}")
        self.channels = checkpoint["channels"]
        if not self.channels or len(set(self.channels)) != len(self.channels):
            raise ValueError("Checkpoint must specify unique electrode names")
        self.model = EEGNet(chn=len(self.channels))
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.eval()

    def predict(self, window, *, channels, sample_rate, units, preprocessing):
        if list(channels) != self.channels:
            raise ValueError("Lapse electrode names/order do not match the checkpoint")
        if sample_rate != 128 or units != "uV" or preprocessing != "pvt_0.5_45Hz":
            raise ValueError("Lapse input must use PVT preprocessing, 128 Hz, and microvolts")
        window = np.asarray(window, dtype=np.float32)
        if window.shape != (len(self.channels), 256) or not np.isfinite(window).all():
            raise ValueError("Expected a finite (channels, 256) lapse window")
        with torch.inference_mode():
            scores = self.model(torch.from_numpy(window.copy()).unsqueeze(0)).softmax(dim=1)
        return float(scores[0, 1])
