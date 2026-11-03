# hold-setup

The installation assistant shared by the Hold family of GNOME Shell
extensions ([Accent Hold](https://github.com/d101c/accent-hold),
[Voice Hold](https://github.com/d101c/voice-hold),
[Command Hold](https://github.com/d101c/command-hold)).

`manifest.json` lists everything an extension's *Installation* page may
download for a user: the engines' pure-Python wheels (from the GitHub
releases), their dependencies (from PyPI, per CPython tag), the speech
models (from the sherpa-onnx `asr-models` release) and the Ollama bundle,
each with its size and SHA-256. The page downloads with libsoup, checks the
hashes, unpacks with libgnome-autoar into `~/.local/share/hold/` and
`~/.local/share/voice-hold/models/`, and writes the D-Bus service files so
the engines run with the system Python. No subprocess, no pipx, no sudo.

`extension/setup.js` and `extension/setupPage.js` are the source of truth;
each extension carries a copy (extensions.gnome.org bundles must be
self-contained).

Regenerate the manifest after a release: `python3 tools/make-manifest.py`.
