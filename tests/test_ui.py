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
        self.assertNotIn('lapse_score', self.script)
        self.assertIn('paintVigilance(demoMode ? s.t : null)', self.script)
        self.assertEqual(set(re.findall(r'\bs\s*\.\s*(\w+)', self.script)), set(STATE_FIELDS))
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
        self.assertEqual(set(re.findall(r'\bs\s*\.\s*(\w+)', self.script)), set(STATE_FIELDS))
        self.assertIn('paintSignal(demoMode ? s.t : null)', self.script)
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


if __name__ == '__main__':
    unittest.main()
