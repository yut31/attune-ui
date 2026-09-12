"""Deterministic Python illustration; not connected to participant measurements."""
import math
from backend.app.providers import MockPredictionProvider
from backend.app.prepared_input import PreparedInput


def results(index, provider=None):
    if type(index) is not int or index < 0:
        raise ValueError('index must be a nonnegative integer')
    t = index * .25
    a = int(t // 4) % 2 == 0
    yield 'attention', t, 'mock-aad', dict(attended='A' if a else 'B',
                                        correlation_a=.42 if a else .19,
                                        correlation_b=.19 if a else .42, simulated=True)
    yield 'vigilance', t, 'mock-vigilance', dict(score=.5-.4*math.cos(t/4), simulated=True)
    yield 'signal_quality', t, 'mock-quality', dict(quality=None, artifact=None, simulated=True)
    yield 'sync', t, 'mock-sync', dict(status='unknown', offset_ms=None, drift_warning=False,
                                     timeline='session_seconds', fixed_latency_ms=None, simulated=True)
    yield 'eeg_display', t, 'mock-display', dict(sample_rate=32, channels=['illustration'],
        samples=[[math.sin(t + i / 8) for i in range(32)]], simulated=True)
    yield 'gain', t, 'mock-gain', dict(a_db=0 if a else -6, b_db=-6 if a else 0, simulated=True)
    provider = provider if provider is not None else MockPredictionProvider()
    prepared = PreparedInput(provider.provider_id, provider.task, timestamp=t,
                             window_id=f'mock-{index}', metadata={'mock': True})
    prediction = provider.predict(prepared).to_dict()
    prediction['simulated'] = True
    yield 'prediction', t, provider.provider_id, prediction


class MockProducer:
    simulated = True

    def run(self, publish, stop):
        index = 0
        provider = MockPredictionProvider()
        while not stop.is_set():
            for kind, timestamp, source, payload in results(index, provider):
                if stop.is_set():
                    return
                publish(kind, timestamp, source, payload)
            index += 1
            stop.wait(.25)
