# hold-setup

The installation assistant of the
[Voice Hold](https://github.com/d101c/voice-hold) GNOME Shell extension.

`manifest.json` lists everything the extension's *Installation* page may
download for a user: the engine's pure-Python wheel (from the GitHub
release), its dependencies (from PyPI, per CPython tag) and the speech
models (from the sherpa-onnx `asr-models` release), each with its size and
SHA-256. The page downloads with libsoup, checks the hashes, unpacks with
libgnome-autoar into `~/.local/share/hold/` and
`~/.local/share/voice-hold/models/`, and writes the D-Bus service file so
the engine runs with the system Python. No subprocess, no pipx, no sudo.

`extension/setup.js` and `extension/setupPage.js` are the source of truth;
the extension carries a copy (extensions.gnome.org bundles must be
self-contained).

Regenerate the manifest after a release: `python3 tools/make-manifest.py`.

## Roadmap and issues

Bugs, ideas, planned work and things still to test are tracked in the
[GitHub issues](https://github.com/d101c/hold-setup/issues); what is planned for
the next version is grouped in a milestone.

- **Report a bug:** open an issue with your distribution, GNOME Shell version,
  what you did, what you expected and what happened, plus any error shown by
  `journalctl -b /usr/bin/gnome-shell`. Problems with the extension itself
  go to [Voice Hold](https://github.com/d101c/voice-hold/issues).
- **Suggest an idea:** open an issue that describes what you want to do.
