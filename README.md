# voice_stream_app

A small demo that prints lines of text and speaks them locally using pyttsx3.

Features added in this commit:
- Robust, thread-safe TTS worker that initializes pyttsx3 inside its thread
- CLI with options for rate, volume, continuous mode, and saving to a file
- Graceful shutdown handling (signals & KeyboardInterrupt)
- Basic unit test for non-TTS behavior and GitHub Actions CI

Usage

Run the demo (prints and speaks lines):

```bash
python app.py