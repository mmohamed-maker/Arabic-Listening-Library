"""Convert an Arabic UTF-8 script to MP3 for GitHub Pages.
Requires internet connection to an external voice synthesis endpoint.
"""
import argparse
import asyncio
from pathlib import Path
import edge_tts

ROOT = Path(__file__).resolve().parents[1]

async def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--source", default="content/unit-01.txt")
    cli.add_argument("--output", default="site/audio/unit-01.mp3")
    cli.add_argument("--voice", default="ar-SA-ZariyahNeural")
    cli.add_argument("--rate", default="-15%")
    args = cli.parse_args()
    src = (ROOT / args.source).resolve()
    dest = (ROOT / args.output).resolve()
    if not src.is_relative_to(ROOT) or not src.is_file():
        raise SystemExit("Missing script or source outside repository.")
    if not dest.is_relative_to(ROOT):
        raise SystemExit("Audio output must be within repository.")
    speech = src.read_text(encoding="utf-8").strip()
    if not speech:
        raise SystemExit("Listening script is empty.")
    dest.parent.mkdir(parents=True, exist_ok=True)
    await edge_tts.Communicate(speech, voice=args.voice, rate=args.rate).save(str(dest))
    if dest.stat().st_size < 1000:
        raise SystemExit("MP3 output is unexpectedly small.")
    print(f"Created {dest.relative_to(ROOT)}: {dest.stat().st_size} bytes")

if __name__ == "__main__":
    asyncio.run(main())
