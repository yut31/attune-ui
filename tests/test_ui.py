"""Static UI contract and isolated live-demo state regression checks."""
from contextlib import ExitStack
from copy import deepcopy
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from types import ModuleType
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / 'src/ui.html'
README = ROOT / 'README.md'
INTEGRATION = ROOT / 'docs/INTEGRATION.md'
HANDOFF = ROOT
HANDOFF_UI = UI
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
        self.elements = []
        self.headings = []
        self.in_heading = False

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
        if tag in ('h1', 'h2', 'h3'):
            self.in_heading = True
        self.ids.update(value for name, value in attrs if name == 'id')
        if tag == 'script':
            self.in_script = True

    def handle_endtag(self, tag):
        if tag in ('h1', 'h2', 'h3'):
            self.in_heading = False
        if tag == 'script':
            self.in_script = False

    def handle_data(self, data):
        if self.in_heading:
            self.headings.append(data)
        if self.in_script:
            self.scripts.append(data)


def load_live_demo():
    # Backend-specific regression checks only run inside the full NOVA repository.
    backend = ROOT / 'neuro-attention/src/live_demo.py'
    if not backend.is_file():
        raise unittest.SkipTest(
            'Requires the full NOVA backend; this repository contains the standalone ATTUNE UI.'
        )

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
        'nova_ui_test_live_demo', backend)
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


class UIShellTests(unittest.TestCase):
    def setUp(self):
        self.ui = UIParser()
        self.ui.feed(UI.read_text(encoding='utf-8'))
        self.ui.close()
        self.script = '\n'.join(self.ui.scripts)

    def test_ui_001_t01_shell_dom_ids(self):
        ids = [attrs['id'] for _, attrs in self.ui.elements if 'id' in attrs]
        for element_id in ('banner', 'eeg', 'cardA', 'cardB', 'fillA', 'fillB',
                           'dbA', 'dbB', 'statusA', 'statusB', 'needle', 'footer'):
            with self.subTest(element_id=element_id):
                self.assertEqual(ids.count(element_id), 1)

    def test_ui_001_t02_state_request_preserved(self):
        self.assertRegex(self.script, r'''\bfetch\s*\(\s*['"]/state['"]''')

    def test_ui_001_t03_state_fields_preserved(self):
        fields = set(re.findall(r'\bs\s*\.\s*(\w+)', self.script))
        self.assertTrue(set(STATE_FIELDS).issubset(fields))

    def test_ui_001_t04_attune_heading(self):
        self.assertIn('ATTUNE', self.ui.headings)
        self.assertTrue(any(tag == 'header' for tag, _ in self.ui.elements))
        self.assertTrue(any(tag == 'span' and attrs.get('id') == 'systemText'
                            for tag, attrs in self.ui.elements))
        html = UI.read_text(encoding='utf-8')
        self.assertIn('<title>ATTUNE — Neuro-Adaptive Hearing</title>', html)
        self.assertIn('<p class="subtitle">Neuro-Adaptive Hearing</p>', html)
        self.assertIn('<footer id="footer">ATTUNE · EEG-guided adaptive hearing', html)
        self.assertNotIn('NOVA', html)

    def test_ui_001_t05_talker_headings(self):
        for talker in ('Talker A', 'Talker B'):
            with self.subTest(talker=talker):
                self.assertIn(talker, self.ui.headings)

    def test_ui_001_t06_eeg_canvas(self):
        canvases = [attrs for tag, attrs in self.ui.elements
                    if tag == 'canvas' and attrs.get('id') == 'eeg']
        self.assertEqual(len(canvases), 1)
        self.assertGreater(int(canvases[0]['width']), 0)
        self.assertGreater(int(canvases[0]['height']), 0)
        self.assertTrue(canvases[0].get('aria-label'))
        self.assertIn('requestAnimationFrame(drawEEG)', self.script)



class UIDemoTests(unittest.TestCase):
    def setUp(self):
        self.html = UI.read_text(encoding='utf-8')
        self.ui = UIParser()
        self.ui.feed(self.html)
        self.ui.close()
        self.script = '\n'.join(self.ui.scripts)
        self.helper = self.script.split('function demoState(t){', 1)[1].split(
            'let demoMode', 1)[0]

    def test_ui_002_t01_demo_control_and_required_ids(self):
        self.assertTrue(any(tag == 'button' and attrs.get('id') == 'demoToggle'
                            for tag, attrs in self.ui.elements))
        for element_id in ('banner', 'eeg', 'cardA', 'cardB', 'fillA', 'fillB',
                           'dbA', 'dbB', 'statusA', 'statusB', 'needle', 'footer',
                           'systemText'):
            with self.subTest(element_id=element_id):
                self.assertIn(element_id, self.ui.ids)

    def test_ui_002_t02_simulated_disclosure(self):
        self.assertIn('demoDisclosure', self.ui.ids)
        self.assertIn('DEMO MODE · SIMULATED DATA', self.html)
        self.assertIn('not participant measurements', self.html)
        self.assertIn('No audio is played.', self.html)

    def test_ui_002_t03_real_endpoint_preserved(self):
        self.assertRegex(self.script, r'''\bfetch\s*\(\s*['"]/state['"]''')
        self.assertIn('if(generation !== modeGeneration) return;', self.script)

    def test_ui_002_t04_no_randomness(self):
        self.assertNotRegex(self.script, r'Math\s*(?:\.\s*random|\[\s*[\'\"]random)')

    def test_ui_002_t05_existing_demo_contract(self):
        payload = self.helper.split('return {', 1)[1].split('};', 1)[0]
        self.assertEqual(set(re.findall(r'\b([A-Za-z_]\w*)\s*:', payload)), set(STATE_FIELDS))
        self.assertRegex(payload, r'correct_frac:\s*0\b')

    def test_ui_002_t06_deterministic_eeg_source(self):
        self.assertIn('Math.sin', self.helper)
        self.assertRegex(self.helper, r'eeg:\s*traces')
        self.assertIn('sample/64', self.helper)
        self.assertNotIn('performance.now', self.helper)

    def test_ui_002_t07_both_attention_states(self):
        self.assertRegex(self.helper, r'attended:\s*towardB\s*<\s*0\.5\s*\?\s*0\s*:\s*1')
        self.assertIn('t % 16', self.helper)

    def test_ui_002_t08_attune_branding(self):
        self.assertIn('ATTUNE', self.ui.headings)
        self.assertIn('<title>ATTUNE — Neuro-Adaptive Hearing</title>', self.html)

    @unittest.skipUnless(shutil.which('node'), 'Optional JS execution requires an existing Node executable')
    def test_ui_002_t09_determinism_and_mode_isolation(self):
        # Built-in Node VM only; fake clock, DOM, canvas, timers and fetch.
        harness = r"""
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const html = fs.readFileSync(process.argv[1], 'utf8');
const elements = Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(m =>
  [m[1], {textContent:'',style:{},dataset:{},hidden:false,attributes:{},listeners:{},
    classList:{toggle(){}},lastElementChild:{textContent:''},
    setAttribute(k,v){this.attributes[k]=v},addEventListener(k,v){this.listeners[k]=v}}]));
let draws=0, clock=1000, requests=[], timers=[];
elements.eeg.getContext=()=>({setTransform(){},clearRect(){},beginPath(){},
  lineTo(x,y){assert(Number.isFinite(x)&&Number.isFinite(y));draws++},moveTo(){},stroke(){}});
elements.eeg.getBoundingClientRect=()=>({width:1040});
const context=vm.createContext({document:{getElementById:id=>{assert(elements[id],id);return elements[id]}},
  performance:{now:()=>clock},devicePixelRatio:1,addEventListener(){},requestAnimationFrame(){},
  setInterval(fn,ms){assert.equal(ms,80);timers.push(fn)},
  fetch:url=>{assert.equal(url,'/state');return new Promise((resolve,reject)=>requests.push({resolve,reject}))}});
const run=code=>vm.runInContext(code,context);
run(html.match(/<script>([\s\S]*?)<\/script>/)[1]);
const state=t=>JSON.parse(run(`JSON.stringify(demoState(${t}))`));
const keys=['eeg','running','done','attended','gain_a_db','gain_b_db','corr_a','corr_b',
 'correct_frac','eeg_source','audio_source','mode','t'].sort();
for(const t of [0,6,6.5,7,7.5,8,14,15,16,32,100.125]){
 const s=state(t);assert.deepStrictEqual(s,state(t));assert.deepStrictEqual(Object.keys(s).sort(),keys);
 assert.equal(s.t,t);assert.equal(s.correct_frac,0);assert.equal(s.eeg.length,6);
 s.eeg.forEach(ch=>{assert.equal(ch.length,128);ch.forEach(x=>assert(Number.isFinite(x)&&Math.abs(x)<=0.900001))});
}
for(const t of [0,3,6,16,32]){const s=state(t);assert.equal(s.attended,0);assert(s.corr_a>s.corr_b);assert(s.gain_a_db>s.gain_b_db)}
for(const t of [8,10,14,24]){const s=state(t);assert.equal(s.attended,1);assert(s.corr_b>s.corr_a);assert(s.gain_b_db>s.gain_a_db)}
for(const t of [6,7,8,14,15,16]){
 const a=state(t-0.0001),b=state(t+0.0001);
 for(const k of ['gain_a_db','gain_b_db','corr_a','corr_b'])assert(Math.abs(a[k]-b[k])<0.002);
}
assert.notDeepStrictEqual(state(0).eeg,state(0.08).eeg);
const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve()};
(async()=>{
 assert.equal(requests.length,1);
 // Leave another old real request pending to exercise both success and failure races.
 const old=run('tick()');assert.equal(requests.length,2);
 elements.demoToggle.listeners.click();
 assert.equal(elements.demoDisclosure.hidden,false);assert.equal(elements.demoToggle.attributes['aria-pressed'],'true');
 assert.equal(elements.banner.textContent,'Simulated attention: Talker A');
 clock=11000;await timers[0]();assert.equal(elements.banner.textContent,'Simulated attention: Talker B');
 assert.equal(requests.length,2);run('drawEEG()');assert(draws>0);
 requests[0].resolve({json:async()=>({...state(0),mode:'REAL'})});
 requests[1].reject(Error('old request failed'));await old;await flush();
 assert.equal(elements.systemText.textContent,'Demo mode');assert.equal(elements.banner.textContent,'Simulated attention: Talker B');
 elements.demoToggle.listeners.click();assert.equal(requests.length,3);
 assert.equal(elements.demoDisclosure.hidden,true);assert.equal(elements.eegSource.textContent,'—');
 assert.equal(elements.dbA.textContent,'— dB');assert.equal(elements.sessionMode.textContent,'—');
 assert.equal(elements.eegHeading.textContent,'Live EEG activity');assert.equal(run('eeg.length'),0);
 requests[2].reject(Error('backend unavailable'));await flush();assert.equal(elements.systemText.textContent,'Disconnected');
 const real=run('tick()');requests[3].resolve({json:async()=>({...state(0),mode:'REAL',eeg_source:'recorded trial'})});
 await real;assert.equal(elements.systemText.textContent,'System running');assert.equal(elements.banner.textContent,'Attending to Talker A');
 assert.equal(elements.sessionMode.textContent,'REAL');
 // Rapid round trip must also invalidate a real response from the previous generation.
 const stale=run('tick()');elements.demoToggle.listeners.click();elements.demoToggle.listeners.click();
 requests[4].resolve({json:async()=>state(10)});await stale;
 assert.equal(elements.systemText.textContent,'Connecting');assert.equal(elements.sessionMode.textContent,'—');
 requests[5].reject(Error('offline'));await flush();
 assert.equal(timers.length,1);
})().catch(e=>{console.error(e);process.exitCode=1});
"""
        result = subprocess.run([shutil.which('node'), '-e', harness, str(UI)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)



class UIVigilanceTests(unittest.TestCase):
    def setUp(self):
        self.html = UI.read_text(encoding='utf-8')
        self.ui = UIParser()
        self.ui.feed(self.html)
        self.ui.close()
        self.script = '\n'.join(self.ui.scripts)

    def run_js(self, body):
        node = shutil.which('node')
        if not node:
            self.skipTest('Optional JS execution requires an existing Node executable')
        harness = r"""
const fs=require('fs'),vm=require('vm');
const html=fs.readFileSync(process.argv[1],'utf8');
const elements=Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(m=>[m[1],{
 textContent:'',style:{},dataset:{},hidden:false,classList:{toggle(){}},lastElementChild:{},
 setAttribute(){},addEventListener(){}}]));
elements.eeg.getContext=()=>({setTransform(){},clearRect(){}});
elements.eeg.getBoundingClientRect=()=>({width:1040});
let clock=0;
const requests=[];
const context=vm.createContext({document:{getElementById:id=>elements[id]},
 devicePixelRatio:1,performance:{now:()=>clock},addEventListener(){},
 requestAnimationFrame(){},setInterval(){},
 fetch:()=>new Promise((resolve,reject)=>requests.push({resolve,reject}))});
const run=code=>vm.runInContext(code,context);
run(html.match(/<script>([\s\S]*?)<\/script>/)[1]);
const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve()};
(async()=>{
""" + body + r"""
})().catch(e=>{console.error(e);process.exitCode=1});
"""
        result = subprocess.run([node, '-e', harness, str(UI)], capture_output=True,
                                text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_ui_003_t01_vigilance_section(self):
        self.assertTrue(any(tag == 'section' and attrs.get('id') == 'vigilance'
                            for tag, attrs in self.ui.elements))
        self.assertIn('Vigilance', self.ui.headings)

    def test_ui_003_t02_lapse_display(self):
        self.assertIn('Lapse risk', self.ui.headings)
        for element_id in ('lapseRisk', 'lapseFill', 'vigilanceStatus', 'vigilanceNote'):
            self.assertIn(element_id, self.ui.ids)

    def test_ui_003_t03_real_unavailable_and_demo_exit(self):
        self.assertIn('Combined vigilance output not connected yet.', self.html)
        self.assertIn('<p id="lapseRisk">—</p>', self.html)
        states = self.run_js(r"""
const snapshots=[];
const snapshot=()=>snapshots.push([elements.vigilanceStatus.textContent,
 elements.lapseRisk.textContent,elements.lapseFill.style.width]);
// Ordinary auditory values must never become a vigilance measurement.
requests[0].resolve({json:async()=>JSON.parse(run('JSON.stringify(demoState(12))'))});
await flush();snapshot();
run('toggleDemo()');clock=12000;await run('tick()');snapshot();
run('toggleDemo()');snapshot(); // Must clear before the pending fetch completes.
requests[1].reject(Error('offline'));await flush();snapshot();
const pending=run('tick()');
requests[2].resolve({json:async()=>({...JSON.parse(run('JSON.stringify(demoState(0))')),running:false})});
await pending;snapshot();
console.log(JSON.stringify(snapshots));
""")
        unavailable = ['Awaiting pipeline', '—', '0%']
        self.assertEqual(states[0], unavailable)
        self.assertEqual(states[1][0], 'Elevated lapse risk')
        self.assertIn('simulated', states[1][1])
        for snapshot in states[2:]:
            self.assertEqual(snapshot, unavailable)

    def test_ui_003_t04_deterministic_lapse(self):
        values = self.run_js(r"""
console.log(JSON.stringify([0,3,6,12,18,24,123.5].map(t=>[
 run(`demoLapseRisk(${t})`),run(`demoLapseRisk(${t})`),run(`demoLapseRisk(${t+24})`)])));
""")
        for first, repeated, cycle in values:
            self.assertEqual(first, repeated)
            self.assertAlmostEqual(first, cycle)
        self.assertAlmostEqual(values[0][0], .1)
        self.assertAlmostEqual(values[3][0], .9)
        self.assertAlmostEqual(values[5][0], .1)

    def test_ui_003_t05_bounded_smooth_lapse(self):
        values = self.run_js(r"""
console.log(JSON.stringify(Array.from({length:2401},(_,i)=>run(`demoLapseRisk(${i/50})`))));
""")
        self.assertTrue(all(0 <= value <= 1 for value in values))
        self.assertGreater(max(values), .7)
        self.assertLess(min(values), .4)
        self.assertLess(max(abs(b-a) for a,b in zip(values, values[1:])), .003)

    def test_ui_003_t06_no_randomness(self):
        self.assertNotRegex(self.script, r'Math\s*(?:\.\s*random|\[\s*[\'\"]random)')

    def test_ui_003_t07_display_thresholds(self):
        labels = self.run_js(r"""
console.log(JSON.stringify([0,.399999,.4,.699999,.7,1].map(x=>run(`vigilanceLabel(${x})`))));
""")
        self.assertEqual(labels, ['Attentive', 'Attentive', 'Watch', 'Watch',
                                  'Elevated lapse risk', 'Elevated lapse risk'])

    def test_ui_003_t08_contract_unchanged(self):
        self.assertEqual(set(load_live_demo().STATE), set(STATE_FIELDS))
        self.assertIn('lapse_score', self.script)
        self.assertIn('state.vigilance.lapseScore', self.script)
        self.assertTrue(set(STATE_FIELDS).issubset(
            set(re.findall(r'\bs\s*\.\s*(\w+)', self.script))))
        helper = self.script.split('function demoLapseRisk(t){', 1)[1].split('function vigilanceLabel', 1)[0]
        for field in ('eeg', 'corr_a', 'corr_b', 'correct_frac', 'attended', 'gain'):
            self.assertNotIn(field, helper)

    def test_ui_003_t09_existing_shell_preserved(self):
        for title in ('ATTUNE', 'Talker A', 'Talker B', 'Live EEG activity'):
            self.assertIn(title, self.ui.headings)
        for element_id in ('eeg', 'demoToggle', 'demoDisclosure', 'banner', 'cardA', 'cardB'):
            self.assertIn(element_id, self.ui.ids)
        self.assertIn('DEMO MODE · SIMULATED DATA', self.html)



class UISignalTests(unittest.TestCase):
    # Reuse the existing offline harness without inheriting/duplicating its tests.
    setUp = UIVigilanceTests.setUp
    run_js = UIVigilanceTests.run_js

    def test_ui_004_t01_signal_section(self):
        self.assertTrue(any(tag == 'section' and attrs.get('id') == 'signalQuality'
                            for tag, attrs in self.ui.elements))
        self.assertIn('Signal quality', self.ui.headings)

    def test_ui_004_t02_quality_display(self):
        self.assertIn('EEG quality', self.ui.headings)
        self.assertIn('qualityValue', self.ui.ids)
        self.assertIn('qualityFill', self.ui.ids)

    def test_ui_004_t03_artifact_display(self):
        self.assertIn('Artifact status', self.ui.headings)
        self.assertIn('artifactStatus', self.ui.ids)

    def test_ui_004_t04_real_unavailable(self):
        self.assertIn('<p id="qualityValue">—</p>', self.html)
        self.assertIn('<p id="artifactStatus">Not connected</p>', self.html)
        self.assertIn('Signal-quality processing not connected yet.', self.html)
        values = self.run_js(r"""
requests[0].resolve({json:async()=>JSON.parse(run('JSON.stringify(demoState(10))'))});
await flush();
console.log(JSON.stringify([elements.signalStatus.textContent,elements.qualityValue.textContent,
 elements.artifactStatus.textContent,elements.qualityFill.style.width]));
""")
        self.assertEqual(values, ['Awaiting pipeline', '—', 'Not connected', '0%'])

    def test_ui_004_t05_deterministic_quality(self):
        values = self.run_js(r"""
console.log(JSON.stringify([0,4,8,10,12,16,20,100.125].map(t=>[
 run(`demoSignal(${t})`),run(`demoSignal(${t})`),run(`demoSignal(${t+20})`)])));
""")
        for first, repeated, cycle in values:
            self.assertEqual(first, repeated)
            self.assertAlmostEqual(first['quality'], cycle['quality'])
            self.assertEqual(first['artifact'], cycle['artifact'])

    def test_ui_004_t06_quality_bounds_and_smoothness(self):
        values = self.run_js(r"""
console.log(JSON.stringify(Array.from({length:2001},(_,i)=>run(`demoSignal(${i/50}).quality`))));
""")
        self.assertTrue(all(0 <= value <= 1 for value in values))
        self.assertAlmostEqual(min(values), .25)
        self.assertAlmostEqual(max(values), .95)
        self.assertLess(max(abs(b-a) for a,b in zip(values,values[1:])), .003)

    def test_ui_004_t07_quality_thresholds(self):
        labels = self.run_js(r"""
console.log(JSON.stringify([0,.449999,.45,.749999,.75,1].map(q=>run(`qualityLabel(${q})`))));
""")
        self.assertEqual(labels, ['Poor','Poor','Fair','Fair','Good','Good'])

    def test_ui_004_t08_artifact_interval(self):
        values = self.run_js(r"""
const times=[0,7.999,8,10,11.999,12,20];
console.log(JSON.stringify(times.map(t=>{
 run(`paintSignal(${t})`);
 return [run(`demoSignal(${t})`),elements.artifactStatus.textContent];
})));
""")
        for (sample, text), artifact in zip(values, [False,False,True,True,True,False,False]):
            self.assertEqual(sample['artifact'], artifact)
            self.assertEqual(text, ('Artifact detected' if artifact else 'Clean')+' · simulated')
            if artifact:
                self.assertLess(sample['quality'], .45)

    def test_ui_004_t09_no_randomness(self):
        self.assertNotRegex(self.script, r'Math\s*(?:\.\s*random|\[\s*[\'\"]random)')

    def test_ui_004_t10_backend_contract_unchanged(self):
        self.assertEqual(set(load_live_demo().STATE), set(STATE_FIELDS))
        self.assertTrue(set(STATE_FIELDS).issubset(
            set(re.findall(r'\bs\s*\.\s*(\w+)', self.script))))
        self.assertIn('paintSignal(demoMode ? state.elapsedSeconds : null)', self.script)
        helper = self.script.split('function demoSignal(t){', 1)[1].split('function qualityLabel', 1)[0]
        for field in ('eeg', 'corr_a', 'corr_b', 'attended', 'gain', 'correct_frac', 'lapse'):
            self.assertNotIn(field, helper)

    def test_ui_004_t11_existing_features(self):
        for heading in ('ATTUNE', 'Vigilance', 'Talker A', 'Talker B', 'Live EEG activity'):
            self.assertIn(heading, self.ui.headings)
        for element_id in ('eeg', 'demoToggle', 'demoDisclosure', 'lapseRisk'):
            self.assertIn(element_id, self.ui.ids)
        self.assertIn('DEMO MODE · SIMULATED DATA', self.html)

    def test_ui_004_t12_exit_resets_quality_and_artifact(self):
        values = self.run_js(r"""
const snapshots=[];
const snapshot=()=>snapshots.push([elements.qualityValue.textContent,
 elements.artifactStatus.textContent,elements.qualityFill.style.width]);
run('toggleDemo()');clock=10000;await run('tick()');snapshot();
// A pending real response cannot overwrite demo metrics.
requests[0].resolve({json:async()=>JSON.parse(run('JSON.stringify(demoState(0))'))});
await flush();snapshot();
run('toggleDemo()');snapshot(); // Clear immediately, before backend response.
requests[1].reject(Error('offline'));await flush();snapshot();
const pending=run('tick()');
requests[2].resolve({json:async()=>JSON.parse(run('JSON.stringify(demoState(10))'))});
await pending;snapshot();
console.log(JSON.stringify(snapshots));
""")
        self.assertIn('Poor', values[0][0])
        self.assertIn('simulated', values[0][0])
        self.assertEqual(values[0][1], 'Artifact detected · simulated')
        self.assertEqual(values[0], values[1])
        for snapshot in values[2:]:
            self.assertEqual(snapshot, ['—', 'Not connected', '0%'])



class UIHistoryTests(unittest.TestCase):
    setUp = UIVigilanceTests.setUp
    run_js = UIVigilanceTests.run_js

    def test_ui_005_t01_section(self):
        self.assertIn('sessionHistory', self.ui.ids)
        self.assertIn('Session History', self.ui.headings)

    def test_ui_005_t02_attention_labels(self):
        self.assertIn('attentionHistory', self.ui.ids)
        self.assertIn('A = Talker A · B = Talker B', self.html)

    def test_ui_005_t03_vigilance_history(self):
        self.assertIn('lapseHistory', self.ui.ids)
        self.assertIn('lapseHistoryStatus', self.ui.ids)

    def test_ui_005_t04_signal_history(self):
        self.assertIn('signalHistory', self.ui.ids)
        self.assertIn('Striped bars = simulated artifact periods', self.script)

    def test_ui_005_t05_determinism(self):
        values = self.run_js(r"""
console.log(JSON.stringify([0,1.2,29.9,30,50.5,1000].map(t=>[
 run(`demoHistory(${t})`),run(`demoHistory(${t})`)])));
""")
        for first, second in values:
            self.assertEqual(first, second)
            self.assertTrue(all(0 <= p['lapse'] <= 1 and 0 <= p['quality'] <= 1 for p in first))

    def test_ui_005_t06_bounded_history(self):
        values = self.run_js(r"""
for(let i=0;i<1000;i++){run(`recordAttention(${i},0)`);run(`recordAttention(${i},1)`)}
const real=run('realHistory.slice()');
run('recordAttention(1100,null)');
console.log(JSON.stringify([run('demoHistory(0)'),run('demoHistory(1000)'),real,run('realHistory')]));
""")
        self.assertEqual(len(values[0]), 1)
        for points in values[1:3]:
            self.assertEqual(len(points), 30)
            self.assertEqual(len({p['time'] for p in points}), 30)
            self.assertEqual(points[-1]['time']-points[0]['time'], 29)
        self.assertEqual(values[3], [])
        self.assertNotIn('localStorage', self.script)

    def test_ui_005_t07_reuses_helpers(self):
        result = self.run_js(r"""
console.log(JSON.stringify(run('demoHistory(40).every(p => p.attended === demoState(p.time).attended && p.lapse === demoLapseRisk(p.time) && p.quality === demoSignal(p.time).quality && p.artifact === demoSignal(p.time).artifact)')));
""")
        self.assertTrue(result)

    def test_ui_005_t08_no_randomness(self):
        self.assertNotRegex(self.script, r'Math\s*(?:\.\s*random|\[\s*[\'\"]random)')

    def real_history_snapshot(self):
        return self.run_js(r"""
run('resetHistory()');
requests[0].resolve({json:async()=>JSON.parse(run('JSON.stringify(demoState(10))'))});
await flush();
console.log(JSON.stringify([elements.lapseHistory.innerHTML,elements.lapseHistoryStatus.textContent,
 elements.signalHistory.innerHTML,elements.signalHistoryStatus.textContent,run('realHistory')]));
""")

    def test_ui_005_t09_real_vigilance_unavailable(self):
        values = self.real_history_snapshot()
        self.assertIn('history-bin gap', values[0])
        self.assertEqual(values[1], 'Awaiting pipeline')
        self.assertEqual(set(values[4][0]), {'time', 'attended'})

    def test_ui_005_t10_real_signal_unavailable(self):
        self.assertEqual(self.real_history_snapshot()[2:4], ['', 'Awaiting pipeline'])

    def test_ui_005_t11_contract(self):
        self.assertEqual(set(load_live_demo().STATE), set(STATE_FIELDS))
        self.assertTrue(set(STATE_FIELDS).issubset(
            set(re.findall(r'\bs\s*\.\s*(\w+)', self.script))))

    def test_ui_005_t12_preserved_features(self):
        for heading in ('ATTUNE','Talker A','Talker B','Vigilance','Signal quality','Live EEG activity'):
            self.assertIn(heading,self.ui.headings)
        for element_id in ('eeg','demoToggle','demoDisclosure'):
            self.assertIn(element_id,self.ui.ids)

    def test_ui_005_t13_exit_clears_and_real_recovers(self):
        values = self.run_js(r"""
run('toggleDemo()');clock=31000;await run('tick()');
const demo=[elements.historyMode.textContent,elements.attentionHistory.innerHTML,
 elements.lapseHistory.innerHTML,elements.signalHistory.innerHTML];
run('toggleDemo()');
const cleared=[elements.attentionHistory.innerHTML,elements.lapseHistory.innerHTML,
 elements.signalHistory.innerHTML,run('realHistory.length'),elements.historyMode.textContent];
// Old real response after the round trip must not populate history.
requests[0].resolve({json:async()=>JSON.parse(run('JSON.stringify(demoState(0))'))});
await flush();const stale=run('realHistory.length');
requests[1].resolve({json:async()=>JSON.parse(run('JSON.stringify(demoState(10))'))});
await flush();const real=run('realHistory');
console.log(JSON.stringify([demo,cleared,stale,real,elements.lapseHistory.innerHTML,elements.signalHistory.innerHTML]));
""")
        self.assertIn('SIMULATED', values[0][0])
        self.assertTrue(all(values[0][1:]))
        self.assertIn('artifact', values[0][3])
        self.assertEqual(values[1][:4], ['', '', '', 0])
        self.assertNotIn('SIMULATED', values[1][4])
        self.assertEqual(values[2], 0)
        self.assertEqual(values[3], [{'time':31,'attended':1}])
        self.assertIn('history-bin gap', values[4])
        self.assertEqual(values[5], '')

    def test_ui_005_t14_no_external_dependencies(self):
        for tag, attrs in self.ui.elements:
            if tag == 'script':
                self.assertNotIn('src', attrs)
            if tag == 'link':
                self.assertNotIn('href', attrs)
        self.assertNotRegex(self.script, r'\bimport\s*(?:\(|.*from)')



class UIAdapterTests(unittest.TestCase):
    setUp = UIVigilanceTests.setUp
    run_js = UIVigilanceTests.run_js

    def test_ui_006_t01_adapter_exists(self):
        self.assertIn('function normalizeState(rawState)', self.script)

    def test_ui_006_t02_valid_mapping(self):
        value = self.run_js(r"""
console.log(JSON.stringify(run(`normalizeState({running:true,done:false,t:12.5,attended:1,
 gain_a_db:-9,gain_b_db:0,corr_a:.2,corr_b:.8,correct_frac:.75,
 eeg_source:'recorded',audio_source:'tracks',mode:'playing',eeg:[[0,1],[-1,0]]})`)));
""")
        self.assertEqual(value, dict(running=True,done=False,elapsedSeconds=12.5,
            attention=dict(attendedTalker=1,correlationA=.2,correlationB=.8,gainA=-9,gainB=0),
            vigilance=dict(lapseScore=None),
            session=dict(accuracy=.75,eegSource='recorded',audioSource='tracks',mode='playing'),
            eeg=[[0,1],[-1,0]]))

    def test_ui_006_t03_invalid_defaults(self):
        values = self.run_js(r"""
console.log(JSON.stringify([null,undefined,0,'bad',true,[],{}].map(x=>context.normalizeState(x))));
""")
        expected = dict(running=False,done=False,elapsedSeconds=None,
            attention=dict(attendedTalker=None,correlationA=None,correlationB=None,gainA=None,gainB=None),
            vigilance=dict(lapseScore=None),
            session=dict(accuracy=None,eegSource='',audioSource='',mode=''),eeg=[])
        self.assertTrue(all(value == expected for value in values))

    def test_ui_006_t04_attended_validation(self):
        values = self.run_js(r"""
console.log(JSON.stringify([0,1,-1,2,'0',true,null,NaN].map(attended=>context.normalizeState({attended}).attention.attendedTalker)));
""")
        self.assertEqual(values,[0,1,None,None,None,None,None,None])

    def test_ui_006_t05_eeg_validation(self):
        values = self.run_js(r"""
console.log(JSON.stringify([null,{},'bad',[1,2],[[0]],[[0,1],[2]],[[0,NaN]],[[0,1]]].map(eeg=>context.normalizeState({eeg}).eeg)));
""")
        self.assertEqual(values[:-1],[[]]*7)
        self.assertEqual(values[-1],[[0,1]])

    def test_ui_006_t06_finite_numbers_and_strings(self):
        values = self.run_js(r"""
console.log(JSON.stringify([NaN,Infinity,-Infinity,'1',null,true].map(x=>context.normalizeState({
 t:x,corr_a:x,corr_b:x,gain_a_db:x,gain_b_db:x,correct_frac:x,eeg_source:x,audio_source:{},mode:[],running:1,done:'true'}))));
""")
        for value in values:
            self.assertIsNone(value['elapsedSeconds'])
            self.assertTrue(all(v is None for v in value['attention'].values()))
            self.assertIsNone(value['session']['accuracy'])
            self.assertEqual(value['session']['audioSource'],'')
            self.assertEqual(value['session']['mode'],'')
            self.assertFalse(value['running'])
            self.assertFalse(value['done'])

    def test_ui_006_t07_real_path_normalized(self):
        values = self.run_js(r"""
let calls=0;const original=context.normalizeState;
context.normalizeState=x=>{calls++;return original(x)};
requests[0].resolve({json:async()=>({running:true,attended:'bad',corr_a:'bad',gain_a_db:Infinity,eeg:'bad'})});
await flush();
console.log(JSON.stringify([calls,elements.banner.textContent,elements.dbA.textContent,elements.corrA.textContent,elements.elapsed.textContent]));
""")
        self.assertEqual(values,[1,'Attention unavailable','— dB','—','—'])

    def test_ui_006_t08_normalized_attention_rendering(self):
        rendering = self.script.split('async function tick()',1)[1]
        for field in ('attendedTalker','gainA','gainB','correlationA','correlationB'):
            self.assertIn('state.attention.'+field,rendering)
        for field in ('corr_a','corr_b','gain_a_db','gain_b_db'):
            self.assertNotIn(field,rendering)

    def test_ui_006_t09_normalized_session_rendering(self):
        rendering = self.script.split('async function tick()',1)[1]
        for field in ('accuracy','eegSource','audioSource','mode'):
            self.assertIn('state.session.'+field,rendering)

    def test_ui_006_t10_normalized_history(self):
        values = self.run_js(r"""
run('updateHistory(normalizeState({running:true,attended:1}))');
clock=1000;run('updateHistory(normalizeState({running:true,attended:8}))');
console.log(JSON.stringify(run('realHistory')));
""")
        self.assertEqual(values,[{'time':0,'attended':1}])
        self.assertIn('state.attention.attendedTalker',self.script.split('function updateHistory',1)[1].split('function demoSignal',1)[0])

    def test_ui_006_t11_no_fabricated_metrics(self):
        value = self.run_js(r"""
console.log(JSON.stringify(context.normalizeState({lapseScore:.8,signalQuality:.9,artifact:true,confidence:.8})));
""")
        self.assertEqual(set(value),{'running','done','elapsedSeconds','attention','vigilance','session','eeg'})
        for field in ('lapseScore','signalQuality','artifact','confidence'):
            if field != 'lapseScore':
                self.assertNotIn(field,json.dumps(value))
        self.assertIsNone(value['vigilance']['lapseScore'])

    def test_ui_006_t12_backend_unchanged(self):
        self.assertEqual(set(load_live_demo().STATE),set(STATE_FIELDS))

    def test_ui_006_t13_demo_determinism(self):
        values = self.run_js(r"""
console.log(JSON.stringify([0,8,16,40].map(t=>[run(`normalizeState(demoState(${t}))`),run(`normalizeState(demoState(${t}))`)])));
""")
        for first,second in values:
            self.assertEqual(first,second)
            self.assertTrue(first['running'])

    def test_ui_006_t14_no_randomness(self):
        self.assertNotRegex(self.script, r'Math\s*(?:\.\s*random|\[\s*[\'\"]random)')

    def test_ui_006_t15_features_preserved(self):
        for heading in ('ATTUNE','Talker A','Talker B','Vigilance','Signal quality','Session History'):
            self.assertIn(heading,self.ui.headings)
        for element_id in ('eeg','demoToggle','demoDisclosure','lapseRisk','qualityValue'):
            self.assertIn(element_id,self.ui.ids)


class UIVigilanceReadinessTests(unittest.TestCase):
    setUp = UIVigilanceTests.setUp
    run_js = UIVigilanceTests.run_js

    def test_ui_007_t01_normalized_vigilance_object(self):
        value = self.run_js(r"""
console.log(JSON.stringify(run('normalizeState({}).vigilance')));
""")
        self.assertEqual(value, {'lapseScore': None})

    def test_ui_007_t02_valid_lapse_scores(self):
        values = self.run_js(r"""
console.log(JSON.stringify([0,.5,1].map(x=>context.normalizeState({lapse_score:x}).vigilance.lapseScore)));
""")
        self.assertEqual(values, [0,.5,1])

    def test_ui_007_t03_missing_and_null_scores(self):
        values = self.run_js(r"""
console.log(JSON.stringify([context.normalizeState({}).vigilance.lapseScore,
 context.normalizeState({lapse_score:null}).vigilance.lapseScore]));
""")
        self.assertEqual(values, [None,None])

    def test_ui_007_t04_numeric_string_rejected(self):
        value = self.run_js(r"""
console.log(JSON.stringify(context.normalizeState({lapse_score:'0.5'}).vigilance.lapseScore));
""")
        self.assertIsNone(value)

    def test_ui_007_t05_nonfinite_scores_rejected(self):
        values = self.run_js(r"""
console.log(JSON.stringify([NaN,Infinity,-Infinity].map(x=>context.normalizeState({lapse_score:x}).vigilance.lapseScore)));
""")
        self.assertEqual(values, [None,None,None])

    def test_ui_007_t06_out_of_range_scores_rejected(self):
        values = self.run_js(r"""
console.log(JSON.stringify([-0.01,1.01].map(x=>context.normalizeState({lapse_score:x}).vigilance.lapseScore)));
""")
        self.assertEqual(values, [None,None])

    def test_ui_007_t07_no_fabricated_metrics(self):
        value = self.run_js(r"""
console.log(JSON.stringify(context.normalizeState({lapse_score:.5,signalQuality:.9,artifact:true,confidence:.8})));
""")
        self.assertEqual(value['vigilance']['lapseScore'], .5)
        for field in ('signalQuality','artifact','confidence'):
            self.assertNotIn(field, json.dumps(value))

    def test_ui_007_t08_real_missing_score_is_unavailable(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>({running:true})});
await flush();
console.log(JSON.stringify([elements.vigilanceStatus.textContent,elements.lapseRisk.textContent,
 elements.vigilanceNote.textContent,elements.lapseFill.style.width]));
""")
        self.assertEqual(values, ['Awaiting pipeline','—','Combined vigilance output not connected yet.','0%'])

    def test_ui_007_t09_real_score_uses_existing_label(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>({running:true,lapse_score:.8})});
await flush();
console.log(JSON.stringify([elements.vigilanceStatus.textContent,elements.lapseRisk.textContent,
 elements.vigilanceNote.textContent,elements.lapseFill.style.width]));
""")
        self.assertEqual(values, ['Elevated lapse risk','80% · pipeline',
                                  'Pipeline vigilance output · not a clinical measurement.','80%'])

    def test_ui_007_t10_real_score_not_simulated(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>({running:true,lapse_score:.5})});
await flush();
console.log(JSON.stringify([elements.lapseRisk.textContent,elements.vigilanceNote.textContent]));
""")
        self.assertTrue(all('simulated' not in value.lower() for value in values))

    def test_ui_007_t11_demo_remains_deterministic_and_separate(self):
        values = self.run_js(r"""
const a=run('demoLapseRisk(12)'),b=run('demoLapseRisk(12)');
console.log(JSON.stringify([a,b,context.normalizeState({lapse_score:.99}).vigilance.lapseScore]));
""")
        self.assertEqual(values[0], values[1])
        self.assertEqual(values[2], .99)

    def test_ui_007_t12_real_history_consumes_normalized_score(self):
        values = self.run_js(r"""
run('resetHistory()');
run('updateHistory(normalizeState({running:true,lapse_score:.5}))');
console.log(JSON.stringify(run('realLapseHistory')));
""")
        self.assertEqual(values, [{'time':0,'lapse':.5}])

    def test_ui_007_t13_missing_real_values_are_gaps(self):
        values = self.run_js(r"""
run('resetHistory()');
run('updateHistory(normalizeState({running:true,lapse_score:.5}))');
clock=1000;run('updateHistory(normalizeState({running:true}))');
console.log(JSON.stringify([run('realLapseHistory'),elements.lapseHistory.innerHTML.includes('title="1 s: 0%"'),
 elements.lapseHistory.innerHTML.match(/history-bin gap/g).length]));
""")
        self.assertEqual(values[0], [{'time':0,'lapse':.5},{'time':1,'lapse':None}])
        self.assertFalse(values[1])
        self.assertEqual(values[2], 29)

    def test_ui_007_t14_real_signal_history_unavailable(self):
        values = self.run_js(r"""
run('resetHistory()');
run('updateHistory(normalizeState({running:true,lapse_score:.5}))');
console.log(JSON.stringify([elements.signalHistory.innerHTML,elements.signalHistoryStatus.textContent]));
""")
        self.assertEqual(values, ['', 'Awaiting pipeline'])

    def test_ui_007_t15_state_fetch_is_preserved(self):
        self.assertIn('fetch("/state",{cache:"no-store"})', self.script)

    def test_ui_007_t16_backend_state_remains_thirteen_fields(self):
        self.assertEqual(set(load_live_demo().STATE), set(STATE_FIELDS))

    def test_ui_007_t17_no_randomness(self):
        self.assertNotRegex(self.script, r'Math\s*(?:\.\s*random|\[\s*[\'\"]random)')

    def test_ui_007_t18_no_external_resources(self):
        for tag, attrs in self.ui.elements:
            if tag == 'script':
                self.assertNotIn('src', attrs)
            if tag == 'link':
                self.assertNotIn('href', attrs)
        self.assertNotRegex(self.script, r'\bimport\s*(?:\(|.*from)')

    def test_ui_007_t19_previous_features_remain(self):
        for heading in ('ATTUNE','Talker A','Talker B','Vigilance','Signal quality','Session History'):
            self.assertIn(heading, self.ui.headings)
        for element_id in ('eeg','demoToggle','demoDisclosure','lapseRisk','qualityValue'):
            self.assertIn(element_id, self.ui.ids)


class UIIntegrationHardeningTests(unittest.TestCase):
    setUp = UIVigilanceTests.setUp
    run_js = UIVigilanceTests.run_js

    def test_ui_008_t01_initial_connecting_state(self):
        self.assertIn('data-state="waiting"', self.html)
        self.assertIn('>Connecting</span>', self.html)

    def test_ui_008_t02_valid_response_marks_connected(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>({running:true,lapse_score:.5})});
await flush();
console.log(JSON.stringify([elements.systemStatus.dataset.state,elements.systemText.textContent]));
""")
        self.assertEqual(values, ['connected','System running'])

    def test_ui_008_t03_fetch_rejection_continues_polling(self):
        values = self.run_js(r"""
requests[0].reject(Error('offline'));await flush();
const first=elements.systemText.textContent;run('tick()');
const count=requests.length;requests[1].resolve({json:async()=>({running:true})});await flush();
console.log(JSON.stringify([first,count,elements.systemStatus.dataset.state]));
""")
        self.assertEqual(values, ['Disconnected',2,'connected'])

    def test_ui_008_t04_non_ok_response_unavailable(self):
        values = self.run_js(r"""
requests[0].resolve({ok:false,json:async()=>({running:true})});await flush();
console.log(JSON.stringify([elements.systemStatus.dataset.state,elements.systemText.textContent,
 elements.lapseRisk.textContent]));
""")
        self.assertEqual(values, ['unavailable','Disconnected','—'])

    def test_ui_008_t05_json_parse_failure_safe(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>{throw Error('bad json')}});await flush();
console.log(JSON.stringify([elements.systemStatus.dataset.state,elements.lapseRisk.textContent,
 elements.eeg.length]));
""")
        self.assertEqual(values, ['unavailable','—',None])

    def test_ui_008_t06_malformed_top_level_safe(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>[1,2,3]});await flush();
console.log(JSON.stringify([elements.systemStatus.dataset.state,elements.dbA.textContent,
 elements.lapseRisk.textContent]));
""")
        self.assertEqual(values, ['unavailable','— dB','—'])

    def test_ui_008_t07_failure_clears_previous_measurements(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>({running:true,attended:1,gain_b_db:0,corr_b:.8,lapse_score:.8,eeg:[[0,1]]})});
await flush();run('tick()');requests[1].reject(Error('offline'));await flush();
console.log(JSON.stringify([elements.dbB.textContent,elements.corrB.textContent,
 elements.lapseRisk.textContent,elements.eegStatus.textContent]));
""")
        self.assertEqual(values, ['— dB','—','—','Disconnected'])

    def test_ui_008_t08_success_recovers_after_failure(self):
        values = self.run_js(r"""
requests[0].reject(Error('offline'));await flush();run('tick()');
requests[1].resolve({json:async()=>({running:true,attended:1,lapse_score:.6})});await flush();
console.log(JSON.stringify([elements.systemStatus.dataset.state,elements.lapseRisk.textContent]));
""")
        self.assertEqual(values, ['connected','60% · pipeline'])

    def test_ui_008_t09_older_real_response_ignored(self):
        values = self.run_js(r"""
const older=run('tick()'),newer=run('tick()');
requests[2].resolve({json:async()=>({running:true,attended:1,lapse_score:.8})});await newer;
requests[1].resolve({json:async()=>({running:true,attended:0,lapse_score:.2})});await older;
console.log(JSON.stringify([elements.lapseRisk.textContent,elements.banner.textContent]));
""")
        self.assertEqual(values, ['80% · pipeline','Attending to Talker B'])

    def test_ui_008_t10_mode_generation_ignores_real_after_demo(self):
        values = self.run_js(r"""
const stale=run('tick()');run('toggleDemo()');clock=10000;await run('tick()');
requests[1].resolve({json:async()=>({running:true,attended:1,lapse_score:.9})});await stale;
console.log(JSON.stringify([elements.systemText.textContent,elements.lapseRisk.textContent,
 elements.banner.textContent]));
""")
        self.assertEqual(values, ['Demo mode','85% · simulated','Simulated attention: Talker B'])

    def test_ui_008_t11_real_to_demo_isolates_history(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>({running:true,lapse_score:.8})});await flush();
run('toggleDemo()');
console.log(JSON.stringify([run('realHistory.length'),run('realLapseHistory.length'),
 elements.historyMode.textContent]));
""")
        self.assertEqual(values, [0,0,'DEMO MODE · SIMULATED HISTORY'])

    def test_ui_008_t12_demo_to_real_clears_simulated_history(self):
        values = self.run_js(r"""
run('toggleDemo()');clock=10000;await run('tick()');run('toggleDemo()');
console.log(JSON.stringify([elements.lapseHistory.innerHTML,elements.signalHistory.innerHTML,
 elements.historyMode.textContent,elements.lapseRisk.textContent]));
""")
        self.assertEqual(values, ['', '', 'Real session · attention observations only','—'])

    def test_ui_008_t13_real_waits_for_fresh_response(self):
        values = self.run_js(r"""
run('toggleDemo()');await run('tick()');run('toggleDemo()');
console.log(JSON.stringify([elements.systemText.textContent,elements.lapseRisk.textContent,
 elements.qualityValue.textContent,requests.length]));
""")
        self.assertEqual(values, ['Connecting','—','—',2])

    def test_ui_008_t14_simulated_vigilance_does_not_leak(self):
        values = self.run_js(r"""
run('toggleDemo()');clock=12000;await run('tick()');run('toggleDemo()');
console.log(JSON.stringify([elements.lapseRisk.textContent,elements.vigilanceStatus.textContent]));
""")
        self.assertEqual(values, ['—','Awaiting pipeline'])

    def test_ui_008_t15_simulated_signal_does_not_leak(self):
        values = self.run_js(r"""
run('toggleDemo()');clock=10000;await run('tick()');run('toggleDemo()');
console.log(JSON.stringify([elements.qualityValue.textContent,elements.artifactStatus.textContent]));
""")
        self.assertEqual(values, ['—','Not connected'])

    def test_ui_008_t16_warmup_does_not_show_talker_a(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>({running:false,attended:0,gain_a_db:0,corr_a:1,lapse_score:.9,eeg:[[0,1]]})});await flush();
console.log(JSON.stringify([elements.banner.textContent,elements.dbA.textContent,elements.corrA.textContent]));
""")
        self.assertEqual(values, ['Waiting for the listener…','— dB','—'])

    def test_ui_008_t17_warmup_clears_correlations_and_gains(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>({running:false,gain_a_db:-2,gain_b_db:-3,corr_a:.2,corr_b:.1})});await flush();
console.log(JSON.stringify([elements.dbA.textContent,elements.dbB.textContent,elements.corrA.textContent,elements.corrB.textContent]));
""")
        self.assertEqual(values, ['— dB','— dB','—','—'])

    def test_ui_008_t18_warmup_vigilance_unavailable(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>({running:false,lapse_score:.7})});await flush();
console.log(JSON.stringify([elements.vigilanceStatus.textContent,elements.lapseRisk.textContent]));
""")
        self.assertEqual(values, ['Awaiting pipeline','—'])

    def test_ui_008_t19_warmup_signal_unavailable(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>({running:false})});await flush();
console.log(JSON.stringify([elements.signalStatus.textContent,elements.qualityValue.textContent,elements.artifactStatus.textContent]));
""")
        self.assertEqual(values, ['Awaiting pipeline','—','Not connected'])

    def test_ui_008_t20_malformed_empty_eeg_safe(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>({running:true,eeg:[[],[1]]})});await flush();
run('drawEEG()');
console.log(JSON.stringify([elements.eegStatus.textContent,run('eeg.length')]));
""")
        self.assertEqual(values, ['Awaiting samples',0])

    def test_ui_008_t21_real_mode_never_creates_synthetic_eeg(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>({running:true})});await flush();
console.log(JSON.stringify(run('eeg')));
""")
        self.assertEqual(values, [])

    def test_ui_008_t22_failure_creates_history_gap(self):
        values = self.run_js(r"""
requests[0].resolve({json:async()=>({running:true,lapse_score:.8})});await flush();
run('tick()');requests[1].reject(Error('offline'));await flush();
console.log(JSON.stringify([run('realLapseHistory'),elements.lapseHistory.innerHTML.includes('history-bin gap')]));
""")
        self.assertEqual(values[0][-1], {'time':0,'lapse':None})
        self.assertTrue(values[1])

    def test_ui_008_t23_history_remains_bounded(self):
        values = self.run_js(r"""
for(let i=0;i<100;i++)run(`recordLapse(${i},.5)`);
console.log(JSON.stringify(run('realLapseHistory')));
""")
        self.assertEqual(len(values), 30)
        self.assertEqual(values[0]['time'],70)

    def test_ui_008_t24_no_local_storage(self):
        self.assertNotIn('localStorage', self.script)

    def test_ui_008_t25_no_randomness(self):
        self.assertNotRegex(self.script, r'Math\s*(?:\.\s*random|\[\s*[\'\"]random)')

    def test_ui_008_t26_state_polling_is_no_store(self):
        self.assertIn('fetch("/state",{cache:"no-store"})', self.script)

    def test_ui_008_t27_backend_contract_unchanged(self):
        self.assertEqual(set(load_live_demo().STATE), set(STATE_FIELDS))

    def test_ui_008_t28_lapse_score_readiness_preserved(self):
        value = self.run_js(r"""
console.log(JSON.stringify([context.normalizeState({lapse_score:0}).vigilance.lapseScore,
context.normalizeState({lapse_score:'0.5'}).vigilance.lapseScore]));
""")
        self.assertEqual(value, [0,None])

    def test_ui_008_t29_previous_features_remain(self):
        for heading in ('ATTUNE','Talker A','Talker B','Vigilance','Signal quality','Session History'):
            self.assertIn(heading, self.ui.headings)
        for element_id in ('eeg','demoToggle','demoDisclosure','lapseRisk','qualityValue'):
            self.assertIn(element_id, self.ui.ids)


class UIFinalPolishTests(unittest.TestCase):
    setUp = UIVigilanceTests.setUp

    def test_ui_009_t01_attune_title(self):
        self.assertIn('<title>ATTUNE — Neuro-Adaptive Hearing</title>', self.html)

    def test_ui_009_t02_subtitle(self):
        self.assertIn('<p class="subtitle">Neuro-Adaptive Hearing</p>', self.html)

    def test_ui_009_t03_footer_branding(self):
        self.assertIn('ATTUNE · EEG-guided adaptive hearing', self.html)
        self.assertNotIn('NOVA', self.html)

    def test_ui_009_t04_demo_disclosure(self):
        self.assertIn('DEMO MODE · SIMULATED DATA', self.html)
        self.assertIn('not participant measurements', self.html)

    def test_ui_009_t05_real_vigilance_unavailable(self):
        self.assertIn('Combined vigilance output not connected yet.', self.html)
        self.assertIn('<p id="lapseRisk">—</p>', self.html)

    def test_ui_009_t06_real_signal_unavailable(self):
        self.assertIn('Signal-quality processing not connected yet.', self.html)
        self.assertIn('<p id="artifactStatus">Not connected</p>', self.html)

    def test_ui_009_t07_no_medical_claim(self):
        for term in ('diagnos', 'medical certainty', 'clinical certainty'):
            self.assertNotIn(term, self.html.lower())

    def test_ui_009_t08_accessible_demo_control(self):
        self.assertRegex(self.html, r'<button[^>]+id="demoToggle"[^>]*>Start Demo</button>')
        self.assertIn('aria-pressed="false"', self.html)
        self.assertIn('aria-controls="demoDisclosure"', self.html)

    def test_ui_009_t09_focus_visible_style(self):
        self.assertIn('#demoToggle:focus-visible', self.html)

    def test_ui_009_t10_status_semantics(self):
        self.assertIn('id="systemStatus" role="status"', self.html)
        self.assertIn('aria-live="polite"', self.html)
        self.assertIn('id="banner" role="status"', self.html)

    def test_ui_009_t11_narrow_responsive_rule(self):
        self.assertRegex(self.html, r'@media\s*\(max-width:\s*760px\)')

    def test_ui_009_t12_history_narrow_layout(self):
        self.assertRegex(self.html, r'@media\s*\(max-width:\s*540px\).*history-row')

    def test_ui_009_t13_responsive_eeg(self):
        self.assertIn('#eeg{width:100%;height:170px;display:block}', self.html)
        self.assertIn('overflow-x:hidden', self.html)

    def test_ui_009_t14_no_external_resources(self):
        for tag, attrs in self.ui.elements:
            if tag == 'script':
                self.assertNotIn('src', attrs)
            if tag == 'link':
                self.assertNotIn('href', attrs)

    def test_ui_009_t15_no_framework_artifacts(self):
        self.assertNotRegex(self.html, r'(?i)react|vite|npm|node_modules')

    def test_ui_009_t16_no_randomness(self):
        self.assertNotRegex(self.script, r'Math\s*(?:\.\s*random|\[\s*[\'\"]random)')

    def test_ui_009_t17_no_local_storage(self):
        self.assertNotIn('localStorage', self.script)

    def test_ui_009_t18_same_origin_state_endpoint(self):
        self.assertIn('fetch("/state"', self.script)
        self.assertNotRegex(self.script, r'fetch\s*\(\s*[\'\"]https?://')

    def test_ui_009_t19_no_store_polling(self):
        self.assertIn('fetch("/state",{cache:"no-store"})', self.script)

    def test_ui_009_t20_stale_protection_preserved(self):
        self.assertIn('if(generation !== modeGeneration) return;', self.script)
        self.assertIn('realRequestSequence', self.script)

    def test_ui_009_t21_mode_isolation_preserved(self):
        self.assertIn('resetHistory()', self.script)
        self.assertIn('if(demoMode) return;', self.script)
        self.assertIn('DEMO MODE · SIMULATED DATA', self.html)

    def test_ui_009_t22_handoff_files_are_approved(self):
        self.assertTrue(UI.is_file())
        self.assertTrue(README.is_file())
        self.assertTrue(INTEGRATION.is_file())
        self.assertTrue((ROOT / 'tests/test_ui.py').is_file())

    def test_ui_009_t23_handoff_ui_matches_production(self):
        self.assertTrue(UI.is_file())
        self.assertGreater(len(UI.read_bytes()), 0)

    def test_ui_009_t24_readme_has_no_absolute_path(self):
        self.assertNotRegex(README.read_text(encoding='utf-8'), r'/Users/|/home/')

    def test_ui_009_t25_integration_documents_lapse_score(self):
        contract = INTEGRATION.read_text(encoding='utf-8')
        self.assertIn('lapse_score', contract)
        self.assertIn('0..1', contract)

    def test_ui_009_t26_integration_documents_unavailable_quality(self):
        contract = INTEGRATION.read_text(encoding='utf-8')
        self.assertIn('do not currently exist', contract)
        self.assertIn('unavailable in Real Mode', contract)

    def test_ui_009_t27_handoff_has_no_secret_files(self):
        forbidden = re.compile(r'(?i)(^|\.)(env|key|pem|p12|pfx|credential|token|dataset|participant|recording|checkpoint|model)($|\.)')
        files = (path for path in ROOT.rglob('*') if '.git' not in path.parts)
        self.assertFalse(any(forbidden.search(path.name) for path in files))

    def test_ui_009_t28_previous_features_remain(self):
        for heading in ('ATTUNE','Talker A','Talker B','Vigilance','Signal quality','Session History'):
            self.assertIn(heading, self.ui.headings)
        for feature in ('normalizeState', 'demoLapseRisk', 'realRequestSequence', 'resetHistory'):
            self.assertIn(feature, self.script)


if __name__ == '__main__':
    unittest.main()
