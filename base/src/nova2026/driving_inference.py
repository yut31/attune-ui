"""Inference for the separately labeled public driving-task pilot model."""
import numpy as np
import torch
from nova2026.architecture.cnn import EEGNet


class DrivingResponsePredictor:
    def __init__(self, checkpoint_path):
        checkpoint=torch.load(checkpoint_path,map_location='cpu',weights_only=True)
        if checkpoint.get('task')!='driving_slow_response_pilot':
            raise ValueError('Expected the driving slow-response pilot checkpoint')
        self.channels=checkpoint['channels']
        self.preprocessing=checkpoint['preprocessing']
        self.mean=checkpoint['training_mean']
        self.std=checkpoint['training_std']
        self.model=EEGNet(chn=len(self.channels))
        self.model.load_state_dict(checkpoint['state_dict']);self.model.eval()

    def predict(self, window_uv, *, channels, sample_rate, preprocessing):
        """Return a slow-steering-response score for an already preprocessed window.

        This score is not calibrated as a probability of a general attention lapse.
        """
        if list(channels)!=self.channels or sample_rate!=128 or preprocessing!=self.preprocessing:
            raise ValueError('Input montage, rate, or preprocessing differs from training')
        x=np.asarray(window_uv,dtype=np.float32)
        if x.shape!=(len(self.channels),256) or not np.isfinite(x).all():
            raise ValueError('Expected a finite (training channels, 256) microvolt window')
        with torch.inference_mode():
            tensor=(torch.from_numpy(x.copy()).unsqueeze(0)-self.mean)/self.std
            return float(self.model(tensor).softmax(1)[0,1])
