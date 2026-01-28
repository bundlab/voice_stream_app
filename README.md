# voice_stream_app

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- Add this once you have CI working: [![CI](https://github.com/bundlab/voice_stream_app/actions/workflows/ci.yml/badge.svg)](https://github.com/bundlab/voice_stream_app/actions) -->

A lightweight Python demo that **prints lines of text to console** and **speaks them locally** using [pyttsx3](https://github.com/nateshmbhat/pyttsx3) — a pure-Python offline text-to-speech library.

Perfect as a starting point for voice experiments, audio feedback tools, or real-time voice processing prototypes.

## Features

- **Robust, thread-safe TTS** — pyttsx3 engine initialized inside a dedicated thread (avoids common import-time & multi-threading issues)
- **CLI-friendly** — full argparse support for customization
- **Continuous / one-shot modes** — loop forever or run once
- **Save to audio file** — synthesize text to WAV/MP3 without speaking
- **Graceful shutdown** — handles Ctrl+C, SIGTERM, etc. cleanly
- **Basic unit tests** + GitHub Actions CI setup
- **Modular design** — easy to extend with live microphone input + speech-to-text (coming soon!)

## Installation

```bash
# Recommended: use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install pyttsx3 pytest flake8
# or if you use poetry/uv/pipenv → add to your project