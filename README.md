# Arabic Listening Library

Public learner-facing listening companion for *Arabic Made Simple*. This repo contains only a sample listening lesson and publicly approved source text. The book source is kept private in `Arabic-Book-Studio`.

## Publish the listening site

1. Visit **Settings → Pages** in this public repository.
2. Set **Build and deployment → Source → GitHub Actions**.
3. Visit **Actions → Build and publish Arabic listening**.
4. Use **Run workflow** on the `main` branch.
5. Check that both jobs, **build** and **deploy**, pass.
6. Open the published listening page in a private browser window and test the audio:

https://mmohamed-maker.github.io/Arabic-Listening-Library/listen/unit-01.html

The link above is the *intended* URL. It only becomes live after successful deployment.

## Convert written Arabic to listening audio

Open `content/unit-01.txt`, select the pencil icon, edit the Arabic text, and commit your changes. The workflow automatically attempts to generate a new MP3 and deploy the updated page. You can also run it manually.

- TTS script: `scripts/generate_audio.py`
- TTS workflow: `.github/workflows/publish-listening.yml`
- Voice: `ar-SA-ZariyahNeural` via `edge-tts`
- Output: `site/audio/unit-01.mp3` in the workflow workspace, published to Pages and also provided as an artifact `unit-01-mp3`.

**Important**: `edge-tts` is an unofficial client of an external speech service. Audio generation may fail if the service changes or blocks requests. Check licenses and terms before commercial distribution. Review the Arabic pronunciation, voice, pauses and transcript by listening. Do not publish student data or private curriculum drafts to this public repo.

## Project roles

- `Arabic-Book-Studio` (private): book layout, unreleased content, QR generation.
- `Arabic-Listening-Library` (public): learner-facing listening pages and sample audio.
