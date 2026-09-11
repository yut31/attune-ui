"""Prepare a reproducible 27-person pilot using HTTP ranges of uncompressed MAT data.

Only EEG preceding lane-departure events is used. Reaction times supply targets;
vehicle position is excluded. Source event tables come from the NEMAR conversion.
"""
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
from pathlib import Path
import struct
import time
from urllib.request import Request, urlopen

import numpy as np
from scipy.signal import butter, sosfiltfilt, resample_poly

ROOT = Path(__file__).resolve().parents[2] / 'datasets/driving-attention'
META = ROOT / 'metadata'
CHANNELS = ['FP1','FP2','F7','F3','FZ','F4','F8','FT7','FC3','FCZ','FC4','FT8',
            'T3','C3','CZ','C4','T4','TP7','CP3','CPZ','CP4','TP8','A1','T5',
            'P3','PZ','P4','T6','A2','O1','OZ','O2']
EEG_INDICES = [i for i, name in enumerate(CHANNELS) if name not in ('A1','A2')]
CHANNELS = [CHANNELS[i] for i in EEG_INDICES]
TYPES = {1:'i1',2:'u1',3:'<i2',4:'<u2',5:'<i4',6:'<u4',7:'<f4',9:'<f8'}
SEED = 42
WINDOWS_PER_PERSON = 40


class RemoteMAT:
    def __init__(self, entry):
        self.entry = entry
        self.cache = {}
        self.chunk_dir = ROOT / 'chunks' / entry['name']
        self.chunk_dir.mkdir(parents=True, exist_ok=True)
        self.partial = ROOT / 'raw' / (entry['name'] + '.part')

    def fetch(self, start, count):
        if self.partial.exists() and self.partial.stat().st_size >= start+count:
            with self.partial.open('rb') as handle:
                handle.seek(start)
                return handle.read(count)
        cached = self.chunk_dir / f"{start}-{count}.bin"
        if cached.exists() and cached.stat().st_size == count:
            return cached.read_bytes()
        end = start + count - 1
        error = None
        for attempt in range(4):
            try:
                request = Request(self.entry['download_url'], headers={'Range':f'bytes={start}-{end}'})
                with urlopen(request, timeout=45) as response:
                    if response.status != 206:
                        raise ValueError('Server must honor byte ranges')
                    expected = f'bytes {start}-{end}/{self.entry["size"]}'
                    if response.headers.get('Content-Range') != expected:
                        raise ValueError(f'Unexpected range: {response.headers.get("Content-Range")}')
                    result = response.read(count+1)
                if len(result) != count:
                    raise ValueError('Incomplete range response')
                cached.write_bytes(result)
                return result
            except Exception as exc:
                error = exc
                print(f"Retry {self.entry["name"]}: {type(exc).__name__}: {exc}",flush=True)
                time.sleep(attempt+1)
        raise RuntimeError(f'Range failed for {self.entry["name"]} at {start}: {error}')

    def read(self, start, count):
        # Small reads are metadata; cache 64 KiB pages and never read the full EEG matrix.
        page = start // 65536 * 65536
        if start+count <= page+65536:
            if page not in self.cache:
                self.cache[page] = self.fetch(page, min(65536, self.entry['size']-page))
            return self.cache[page][start-page:start-page+count]
        return self.fetch(start,count)

    def tag(self, offset):
        word, second = struct.unpack('<II',self.read(offset,8))
        if word >> 16:
            return word & 65535, word >> 16, offset+4, offset+8
        return word, second, offset+8, offset+8+((second+7)//8)*8

    def matrix(self, offset):
        kind,size,pos,nxt = self.tag(offset)
        if kind != 14:
            raise ValueError('Expected uncompressed MATLAB miMATRIX')
        _,_,_,pos=self.tag(pos) # flags
        _,size,data,pos=self.tag(pos)
        dims=struct.unpack('<'+'i'*(size//4),self.read(data,size))
        _,_,_,pos=self.tag(pos) # name
        return dims,pos,nxt

    def fields(self):
        if self.read(126,2)!=b'IM':
            raise ValueError('Only little-endian MAT v5 is supported')
        dims,pos,_=self.matrix(128)
        if dims!=(1,1):raise ValueError('Expected scalar EEG struct')
        _,size,data,pos=self.tag(pos)
        width=struct.unpack('<i',self.read(data,size))[0]
        _,size,data,pos=self.tag(pos)
        names=self.read(data,size)
        fields={}
        for i in range(0,len(names),width):
            name=names[i:i+width].split(b'\x00')[0].decode()
            dims,contents,nxt=self.matrix(pos)
            kind,size,data,_=self.tag(contents)
            fields[name]={'dims':dims,'type':kind,'data':data,'bytes':size}
            pos=nxt
            if name=='data':break
        return fields

    def scalar(self, field):
        return np.frombuffer(self.read(field['data'],field['bytes']),dtype=TYPES[field['type']]).item()


def labeled_events(path):
    with path.open() as handle:
        rows=list(csv.DictReader(handle, delimiter='\t'))
    trials=[];pending=None
    for row in rows:
        value=int(row['value']);t=float(row['onset'])
        if value in (251,252):pending=t
        elif value==253 and pending is not None:
            if t>pending:trials.append((pending,t-pending))
            pending=None
        elif value==254:pending=None
    if len(trials)<20:raise ValueError('Insufficient reaction-time trials')
    trials=np.asarray(trials)
    labels=np.zeros(len(trials),dtype=np.int64)
    labels[np.argsort(trials[:,1],kind='stable')[-(len(trials)//10):]]=1
    return trials,labels


def prepare(entry):
    subject=entry['name'].split('_')[0]
    out=ROOT/'prepared'/f'{subject}.npz'
    if out.exists():
        with np.load(out,allow_pickle=False) as cache:
            if cache['channels'].tolist()!=CHANNELS:
                raise ValueError(f'Cached channel contract differs for {subject}')
        print('Prepared cache:',subject,flush=True);return
    source = RemoteMAT(entry)
    fields=source.fields()
    rate=float(source.scalar(fields['srate']));nchan=int(source.scalar(fields['nbchan']))
    data=fields['data'];dtype=np.dtype(TYPES[data['type']]);dims=data['dims']
    if nchan!=33 or dims[0]!=33 or rate!=500:
        raise ValueError(f'Unexpected input layout: {nchan}, {dims}, {rate}')
    if data['bytes'] != np.prod(dims)*dtype.itemsize:
        raise ValueError('EEG matrix size is inconsistent')
    trials,labels=labeled_events(META/f'{subject}_events.tsv')
    # Uniform fixed-seed sampling of trials BEFORE examining the EEG or labels.
    rng=np.random.default_rng(SEED+int(subject[1:]))
    eligible=np.where(trials[:,0]>=6.1)[0]
    selected=np.sort(rng.choice(eligible,min(WINDOWS_PER_PERSON,len(eligible)),replace=False))
    sos=butter(4,[0.5,45],btype='bandpass',fs=rate,output='sos')
    windows=[];targets=[];rts=[];onsets=[];checksums=[];rejected=[]
    print(f"{subject}: layout verified; preparing {len(selected)} windows",flush=True)
    for position, ix in enumerate(selected,1):
        onset,rt=trials[ix]
        # Six seconds of pre-stimulus context ending 100 ms before the event.
        # No post-stimulus or response samples enter the preprocessing window.
        stop=int(round((onset-.1)*rate));start=stop-int(6*rate)
        count=(stop-start)*nchan*dtype.itemsize
        payload=source.fetch(data['data']+start*nchan*dtype.itemsize,count)
        eeg=np.frombuffer(payload,dtype=dtype).reshape((-1,nchan)).T[EEG_INDICES].astype(np.float64)
        if not np.isfinite(eeg).all():
            rejected.append({'trial':int(ix),'reason':'nonfinite'});continue
        filtered=sosfiltfilt(sos,eeg,axis=1)
        window=resample_poly(filtered,128,500,axis=1)[:,-256:].astype(np.float32)
        if np.max(np.ptp(window,axis=1))>500 or np.any(np.std(window,axis=1)<1e-6):
            rejected.append({'trial':int(ix),'reason':'artifact_or_flat'});continue
        windows.append(window);targets.append(labels[ix]);rts.append(rt);onsets.append(onset)
        checksums.append(hashlib.sha256(payload).hexdigest())
        if position % 10 == 0:print(f"{subject}: {position}/{len(selected)} windows",flush=True)
    if not windows:raise ValueError(f'No usable EEG for {subject}')
    out.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out,data=np.stack(windows),labels=np.array(targets),rt=np.array(rts),onset=np.array(onsets),channels=CHANNELS)
    (out.with_suffix('.json')).write_text(json.dumps({'subject':subject,'file':entry['name'],
        'source_md5':entry['computed_md5'],'selected_trial_indices':selected.tolist(),
        'accepted_payload_sha256':checksums,'rejected':rejected,'total_reaction_trials':len(trials),
        'accepted':len(windows),'positives':int(sum(targets)),
        'data_offset':data['data'],'dtype':dtype.str,'source_rate':rate},indent=2))
    print(f'{subject}: prepared {len(windows)} windows, {sum(targets)} slow responses',flush=True)


if __name__=='__main__':
    entries=json.loads((ROOT/'manifest.json').read_text())['files']
    with ThreadPoolExecutor(max_workers=12) as pool:list(pool.map(prepare,entries))
    print('Pilot preprocessing complete.',flush=True)
