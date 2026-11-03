#!/usr/bin/env python3
"""Generate manifest.json: everything the in-extension setup assistant
downloads (URLs, sizes, SHA-256) for each supported Python tag.

PyPI digests come from the PyPI JSON API; our own wheels from the GitHub
release assets (their SHA-256 is computed from the local dist/ copy); the
speech models from the constants pinned in voice_hold_engine.models.
Run from a checkout with ../voice-hold and ../command-hold beside it."""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DEV = HERE.parent
TAGS = ['cp312', 'cp313', 'cp314']
PYPI = {
    'sherpa-onnx': '2.0.1',
    'sherpa-onnx-core': '2.0.1',
    'numpy': '2.5.4',
    'dbus-fast': '5.2.0',
}
VOICE_VERSION = '0.2.0'
COMMAND_VERSION = '0.1.0'
OLLAMA_TAG = 'v0.40.14'


def pypi(name, version):
    with urllib.request.urlopen(f'https://pypi.org/pypi/{name}/{version}/json', timeout=30) as f:
        return json.load(f)['urls']


def pick(urls, tag):
    """The manylinux x86_64 wheel for a CPython tag, or the pure one."""
    for u in urls:
        n = u['filename']
        if n.endswith('.whl') and ('manylinux' in n and 'x86_64' in n) and f'-{tag}-{tag}-' in n:
            return u
    for u in urls:
        n = u['filename']
        if n.endswith('py3-none-any.whl') or (n.endswith('.whl') and 'py3-none-manylinux' in n and 'x86_64' in n):
            return u
    raise SystemExit(f'no wheel for {tag} in {[u["filename"] for u in urls]}')


def entry(u):
    return {'name': u['filename'], 'url': u['url'], 'size': u['size'], 'sha256': u['digests']['sha256']}


def local_wheel(path, url):
    data = path.read_bytes()
    return {'name': path.name, 'url': url, 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    sys.path.insert(0, str(DEV / 'voice-hold' / 'engine' / 'src'))
    from voice_hold_engine import models as vm
    urls = {n: pypi(n, v) for n, v in PYPI.items()}
    voice_whl = next((DEV / 'voice-hold' / 'engine' / 'dist').glob('voice_hold_engine-*-py3-none-any.whl'))
    cmd_whl = next((DEV / 'command-hold' / 'engine' / 'dist').glob('command_hold_engine-*-py3-none-any.whl'))
    voice_url = f'https://github.com/d101c/voice-hold/releases/download/v{VOICE_VERSION[:-2]}/{voice_whl.name}'
    cmd_url = f'https://github.com/d101c/command-hold/releases/download/v{COMMAND_VERSION[:-2]}/{cmd_whl.name}'

    wheels = {}
    for tag in TAGS:
        wheels[tag] = {
            'voice': [local_wheel(voice_whl, voice_url)] + [entry(pick(urls[n], tag)) for n in ('sherpa-onnx', 'sherpa-onnx-core', 'numpy', 'dbus-fast')],
            'command': [local_wheel(cmd_whl, cmd_url), entry(pick(urls['dbus-fast'], tag))],
        }
    models = [
        {'name': vm.ASR_ARCHIVE, 'url': vm.RELEASES + vm.ASR_ARCHIVE, 'size': vm.ASR_ARCHIVE_SIZE,
         'sha256': vm.ASR_ARCHIVE_SHA256, 'extract': True, 'dir': vm.ASR_NAME},
        {'name': vm.VAD_FILE, 'url': vm.RELEASES + vm.VAD_FILE, 'size': vm.VAD_SIZE,
         'sha256': vm.VAD_SHA256, 'extract': False},
    ]

    with urllib.request.urlopen(f'https://api.github.com/repos/ollama/ollama/releases/tags/{OLLAMA_TAG}', timeout=30) as f:
        rel = json.load(f)
    oll = next(a for a in rel['assets'] if a['name'] == 'ollama-linux-amd64.tar.zst')
    manifest = {
        'schema': 1,
        'generated': __import__('time').strftime('%Y-%m-%d'),
        'python': {'tags': TAGS, 'min': '3.12'},
        'wheels': wheels,
        'voice': {'version': VOICE_VERSION, 'module': 'voice_hold_engine', 'bus_name': 'org.griffit.VoiceHold', 'models': models},
        'command': {'version': COMMAND_VERSION, 'module': 'command_hold_engine', 'bus_name': 'org.griffit.CommandHold'},
        'llm': {'ollama': {'name': oll['name'], 'url': oll['browser_download_url'], 'size': oll['size'],
                           'sha256': oll.get('digest', '').replace('sha256:', ''), 'version': OLLAMA_TAG},
                'model': 'qwen3:1.7b', 'model_size': 1400000000},
    }
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=1) + '\n')
    total = sum(e['size'] for e in wheels['cp314']['voice']) + sum(m['size'] for m in models)
    print(f'manifest.json written; voice install for cp314 = {total / 1e6:.0f} MB')


if __name__ == '__main__':
    main()
