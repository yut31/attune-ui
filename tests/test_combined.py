"""Regression checks and a synthetic end-to-end integration test."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'base/src'), str(ROOT / 'neuro-attention/src')]
from nova2026.config import PROJECT_ROOT
from nova2026.architecture.cnn import EEGNet
from nova2026.data.channels import EEG_CHANNELS
from nova2026.inference import save_checkpoint, LapsePredictor
from combined_pipeline import CombinedPipeline
from decoder import LAGS, design


def load_labeler():
    spec = importlib.util.spec_from_file_location('label_pvt', ROOT / 'base/scripts/legacy/labelPVT.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BaseRegressionTests(unittest.TestCase):
    def test_dataset_root_survives_parent_repository(self):
        self.assertEqual(PROJECT_ROOT, ROOT / 'base')

    def test_small_sessions_do_not_become_all_positive(self):
        module = load_labeler()  # also proves importing doesn't start dataset processing
        for count in (0, 1, 9):
            positive, negative = module.split_by_reaction_time(np.zeros((count, 4)))
            self.assertEqual(len(positive) + len(negative), 0)
        trials = np.column_stack([np.arange(20), np.zeros((20, 3))])
        positive, negative = module.split_by_reaction_time(trials)
        np.testing.assert_array_equal(positive[:, 0], [18, 19])
        self.assertEqual(len(negative), 18)

    def test_empty_annotations(self):
        class Raw:
            annotations = []
        self.assertEqual(load_labeler().get_trials(Raw()).shape, (0, 4))


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)
        torch.manual_seed(7)
        cls.temp = tempfile.TemporaryDirectory()
        cls.checkpoint = Path(cls.temp.name) / 'synthetic.pt'
        model = EEGNet(chn=len(EEG_CHANNELS)).eval()
        with torch.no_grad():
            model(torch.zeros(1, len(EEG_CHANNELS), 256))
        save_checkpoint(model, cls.checkpoint, EEG_CHANNELS)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        rng = np.random.default_rng(12)
        # Synthetic AAD montage; deliberately differs from the base montage.
        self.channels = [f'aad-{i}' for i in range(64)]
        weights = rng.normal(size=64 * len(LAGS))
        eeg = rng.normal(size=(960, 64))
        recon = design(eeg) @ weights
        self.pipeline = CombinedPipeline(self.checkpoint, weights, aad_channels=self.channels)
        self.inputs = dict(
            lapse_window=rng.normal(size=(62, 256)), lapse_channels=EEG_CHANNELS,
            lapse_sample_rate=128, lapse_units='uV', lapse_preprocessing='pvt_0.5_45Hz',
            lapse_end_time_s=15., aad_window=eeg, aad_channels=self.channels,
            aad_sample_rate=64, aad_preprocessing='aad_1_9Hz_zscore',
            envelopes=np.stack([-recon, recon]), aad_end_time_s=15., envelope_end_time_s=15.,
        )

    def test_both_models_and_mixer(self):
        result = self.pipeline.decide(**self.inputs)
        self.assertTrue(0 <= result.lapse_score <= 1)
        self.assertEqual(result.attended_talker, 1)
        self.assertGreater(result.correlations[1], .999)
        for _ in range(100):
            output = self.pipeline.mix(np.ones(128), np.zeros(128))
        self.assertTrue(np.all(output < .4))  # talker A is now ducked

    def test_training_exports_loadable_checkpoint(self):
        spec = importlib.util.spec_from_file_location(
            'train_eegnet', ROOT / 'base/scripts/training/trainEEGNet.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.EPOCHS = 1
        module.DEVICE = torch.device('cpu')
        path = Path(self.temp.name) / 'one_epoch.pt'
        data = np.random.default_rng(5).normal(size=(4, 62, 256)).astype(np.float32)
        score = module.train_one_fold(data, [0, 1, 0, 1], data[:2], [0, 1], path)
        self.assertTrue(np.isfinite(score))
        predictor = LapsePredictor(path)
        value = predictor.predict(data[0], channels=EEG_CHANNELS, sample_rate=128,
                                  units='uV', preprocessing='pvt_0.5_45Hz')
        self.assertTrue(0 <= value <= 1)

    def test_wrong_channel_order_rejected(self):
        self.inputs['lapse_channels'] = EEG_CHANNELS[::-1]
        with self.assertRaisesRegex(ValueError, 'electrode'):
            self.pipeline.decide(**self.inputs)

    def test_downsampled_aad_cannot_be_used_as_lapse_input(self):
        self.inputs['lapse_sample_rate'] = 64
        with self.assertRaisesRegex(ValueError, '128 Hz'):
            self.pipeline.decide(**self.inputs)

    def test_misaligned_audio_rejected(self):
        self.inputs['envelope_end_time_s'] = 14.
        with self.assertRaisesRegex(ValueError, 'timestamp'):
            self.pipeline.decide(**self.inputs)

    def test_nonfinite_eeg_rejected(self):
        self.inputs['aad_window'][0, 0] = np.nan
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            self.pipeline.decide(**self.inputs)

    def test_stale_decision_rejected(self):
        self.pipeline.decide(**self.inputs)
        with self.assertRaisesRegex(ValueError, 'increase'):
            self.pipeline.decide(**self.inputs)


if __name__ == '__main__':
    unittest.main()
