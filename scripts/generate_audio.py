"""Create a learner-facing Arabic MP3 using a voice that matches the narrator.

Narrator gender is explicitly supplied per lesson, never inferred from the text.
This unofficial edge-tts client requires an external service; review audio and terms.
"""
import argparse
import asyncio
from pathlib import Path
import edge_tts

ROOT = Path(__file__).resolve().parents[1]
VOICE_FOR_NARRATOR = {
    "male": "ar-SA-HamedNeural",
    "female": "ar-SA-ZariyahNeural",
}

async def main():
    parser = argparse.ArgumentParser(description="Generate Arabic listening audio")
    parser.add_argument("--source", default="content/unit-01.txt")
    parser.add_argument("--output", default="site/audio/unit-01.mp3")
    parser.add_argument("--narrator", choices=VOICE_FOR_NARRATOR, default="male",
                        help="The speaker in the story: male or female.")
    parser.add_argument("--voice", default=None,
                        help="Optional explicit voice override; check its availability.")
    parser.add_argument("--rate", default="-15%")
    args = parser.parse_args()

    source = (ROOT / args.source).resolve()
    output = (ROOT / args.output).resolve()
    if not source.is_relative_to(ROOT) or not source.is_file():
        raise SystemExit("Source must be an existing file within the repository.")
    if not output.is_relative_to(ROOT):
        raise SystemExit("Output must remain within the repository.")
    text = source.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit("Listening text cannot be empty.")
    output.parent.mkdir(parents=True, exist_ok=True)
    voice = args.voice or VOICE_FOR_NARRATOR[args.narrator]
    print(f"Narrator: {args.narrator}; voice: {voice}; speaking rate: {args.rate}")
    await edge_tts.Communicate(text=text, voice=voice, rate=args.rate).save(str(output))
    if output.stat().st_size < 1000:
        raise SystemExit("Audio output unexpectedly small.")
    print(f"Created {output.relative_to(ROOT)} ({output.stat().st_size} bytes)")

if __name__ == "__main__":
    asyncio.run(main())
