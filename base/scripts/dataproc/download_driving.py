"""Download and verify the predeclared public driving-EEG subject cohort."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2] / 'datasets/driving-attention'


def verified(path, entry):
    if not path.exists() or path.stat().st_size != entry['size']:
        return False
    digest = hashlib.md5()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest() == entry['computed_md5']


def download(entry):
    path = ROOT / 'raw' / entry['name']
    if verified(path, entry):
        print('Verified existing:', entry['name'], flush=True)
        return
    url = entry['download_url']
    if not url.startswith('https://ndownloader.figshare.com/files/'):
        raise ValueError('Unexpected download host')
    partial = path.with_suffix('.set.part')
    print('Downloading:', entry['name'], flush=True)
    subprocess.run(['curl', '-sS', '-L', '--fail', '--retry', '2', '--connect-timeout', '15',
                    '--max-time', '900', url, '-o', str(partial)], check=True)
    if not verified(partial, entry):
        raise ValueError(f'Checksum/size mismatch: {entry["name"]}')
    partial.replace(path)
    print('Verified:', entry['name'], flush=True)


if __name__ == '__main__':
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(download, manifest['files']))
    print('All public EEG downloads verified.', flush=True)
