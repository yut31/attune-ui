"""Static UI contract and isolated live-demo state regression checks."""
from contextlib import ExitStack
from copy import deepcopy
from html.parser import HTMLParser
import importlib.util
from pathlib import Path
import re
import sys
from types import ModuleType
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / 'neuro-attention/src/ui.html'
STATE_FIELDS = (
    'eeg', 'running', 'done', 'attended', 'gain_a_db', 'gain_b_db',
    'corr_a', 'corr_b', 'correct_frac', 'eeg_source', 'audio_source', 'mode', 't',
)


class UIParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.scripts = []
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        self.ids.update(value for name, value in attrs if name == 'id')
        if tag == 'script':
            self.in_script = True

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False

    def handle_data(self, data):
        if self.in_script:
            self.scripts.append(data)


def load_live_demo():
    # Import the real state implementation, but never import its engine dependencies.
    imports = {
        'numpy': (),
        'config': ('FS', 'AUDIO_FS', 'BLOCK_S', 'DECISION_STEP_S',
                   'DECISION_WINDOW_S', 'ALPHA'),
        'envelopes': ('build_envelope_cache',),
        'dataset': ('load_kuleuven_subject', 'preprocess_eeg'),
        'decoder': ('fit_decoder', 'RealtimeDecoder'),
        'attention_mixer': ('AttentionMixer',),
        'audio_sources': ('FileSource', 'MicSource'),
        'eeg_sources': ('ReplayEEG', 'LSLEEG'),
        'demo_realtime': ('_live_envelope', '_corrs'),
    }
    stubs = {}
    for name, attributes in imports.items():
        stub = ModuleType(name)
        for attribute in attributes:
            setattr(stub, attribute, Mock(side_effect=AssertionError(
                'Engine dependency must not run in UI tests')))
        stubs[name] = stub

    spec = importlib.util.spec_from_file_location(
        'nova_ui_test_live_demo', ROOT / 'neuro-attention/src/live_demo.py')
    module = importlib.util.module_from_spec(spec)
    with ExitStack() as stack:
        stack.enter_context(patch.dict(sys.modules, stubs))
        for target in ('threading.Thread.start', 'http.server.ThreadingHTTPServer',
                       'webbrowser.open', 'socket.socket.connect', 'socket.socket.bind'):
            stack.enter_context(patch(target, side_effect=AssertionError(
                'UI tests must not start threads, servers, browsers or networking')))
        spec.loader.exec_module(module)
    return module


class UIRegressionTests(unittest.TestCase):
    def parse_ui(self):
        parser = UIParser()
        parser.feed(UI.read_text(encoding='utf-8'))
        parser.close()
        return parser

    def test_ui_000_t01_html_exists_and_is_readable(self):
        self.assertTrue(UI.is_file())
        self.assertTrue(UI.read_text(encoding='utf-8').strip())

    def test_ui_000_t02_required_dom_ids(self):
        ids = self.parse_ui().ids
        for element_id in ('banner', 'eeg', 'cardA', 'cardB', 'fillA', 'fillB',
                           'dbA', 'dbB', 'statusA', 'statusB', 'needle', 'footer'):
            with self.subTest(element_id=element_id):
                self.assertIn(element_id, ids)

    def test_ui_000_t03_state_endpoint_request(self):
        script = '\n'.join(self.parse_ui().scripts)
        self.assertRegex(script, r'''\bfetch\s*\(\s*['"]/state['"]''')

    def test_ui_000_t04_frontend_state_fields(self):
        script = '\n'.join(self.parse_ui().scripts)
        for field in STATE_FIELDS:
            with self.subTest(field=field):
                self.assertRegex(script, r'\bs\s*\.\s*' + re.escape(field) + r'\b')

    def test_ui_000_t05_backend_state_fields(self):
        module = load_live_demo()
        self.assertIsInstance(module.STATE, dict)
        for field in STATE_FIELDS:
            with self.subTest(field=field):
                self.assertIn(field, module.STATE)

    def test_ui_000_t06_set_updates_and_restores_state(self):
        module = load_live_demo()
        state = module.STATE
        original = deepcopy(state)
        try:
            module._set()
            self.assertEqual(state, original)  # Empty update is a no-op.
            changes = {'t': 1.25, 'gain_a_db': -6.0, 'mode': 'UI regression test'}
            module._set(**changes)
            self.assertIs(module.STATE, state)
            self.assertEqual(state, {**original, **changes})
            module._set(t=0.0, mode='')  # Falsy values must overwrite old values.
            self.assertEqual(state, {**original, **changes, 't': 0.0, 'mode': ''})
        finally:
            with module.LOCK:
                state.clear()
                state.update(original)
        self.assertEqual(module.STATE, original)


if __name__ == '__main__':
    unittest.main()
