"""Generate 50 MSA narration clips for the Grade 8 Alif Fariqah game.

Uses the existing repository's edge-tts dependency. Audio is a draft pending
teacher listening review; no synthesis engine guarantees correct Arabic.
"""
import argparse
import asyncio
import re
from pathlib import Path
import edge_tts

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content/alif-fariqah-grade8.txt"
OUT = ROOT / "site/audio/alif-fariqah-grade8"

def read_lines():
    records = {}
    for raw in SOURCE.read_text(encoding="utf-8-sig").splitlines():
        if not raw.strip():
            continue
        match = re.fullmatch(r"(\d{2})\|(.*)", raw)
        if not match:
            raise ValueError("Malformed line: " + raw[:60])
        number, sentence = match.groups()
        if number in records or not sentence.strip():
            raise ValueError("Duplicate or blank line: " + number)
        records[number] = sentence.strip()
    if set(records) != {f"{n:02d}" for n in range(1, 51)}:
        raise ValueError("Expected exactly IDs 01 through 50")
    if any("فَرَاغٌ" in value for value in records.values()):
        raise ValueError("Narration contains an unfilled blank")
    return records

async def synthesize(sentence, path, voice, rate):
    for attempt in range(1, 5):
        try:
            await edge_tts.Communicate(text=sentence, voice=voice, rate=rate).save(str(path))
            if path.stat().st_size <= 1000:
                raise RuntimeError("Generated audio too small")
            return
        except Exception:
            path.unlink(missing_ok=True)
            if attempt == 4:
                raise
            await asyncio.sleep(attempt * 3)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice", choices=["ar-SA-HamedNeural", "ar-SA-ZariyahNeural"], default="ar-SA-HamedNeural")
    parser.add_argument("--rate", default="-10%")
    parser.add_argument("--only", type=int, choices=range(1, 51))
    args = parser.parse_args()
    records = read_lines()
    OUT.mkdir(parents=True, exist_ok=True)
    wanted = [f"{args.only:02d}"] if args.only else list(records)
    for index, num in enumerate(wanted, 1):
        target = OUT / f"q{num}.mp3"
        await synthesize(records[num], target, args.voice, args.rate)
        print(f"[{index}/{len(wanted)}] {target.name}: {target.stat().st_size} bytes", flush=True)
        await asyncio.sleep(0.7)
    if not args.only:
        assert len(list(OUT.glob("q[0-5][0-9].mp3"))) == 50
    print("Synthetic audio ready for HUMAN pronunciation review.")

if __name__ == "__main__":
    asyncio.run(main())
