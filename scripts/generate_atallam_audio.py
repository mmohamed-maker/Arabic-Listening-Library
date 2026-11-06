"""Generate the 32 learner recordings from the Atallam textbook manifest.
A separate GitHub Pages library contains public learner-facing material only.
Listening assessment scripts are not included until approved; no fictitious audio.
edge-tts uses an unofficial external service: check availability and licensing.
"""
import asyncio
import json
import shutil
from pathlib import Path
import edge_tts

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'content'/'atallam_lessons.json'
DEST=ROOT/'site'/'atallam'
VOICE={'male':'ar-SA-HamedNeural','female':'ar-SA-ZariyahNeural'}

async def synth(item,sem):
    async with sem:
        path=DEST/'audio'/f"{item['id']}.mp3"
        if path.exists() and path.stat().st_size>1000:
            print('Skipping existing',item['id'],flush=True);return
        msg=item['text'].strip()
        if not msg:raise ValueError(f"Empty audio transcript for {item['id']}")
        for attempt in range(1,5):
            try:
                await edge_tts.Communicate(text=msg,voice=VOICE[item['voice']],rate='-12%').save(str(path))
                if path.stat().st_size<1000:raise RuntimeError('Audio too small')
                print(f"[{item['id']}] {path.stat().st_size} bytes",flush=True)
                return
            except Exception as exc:
                if attempt==4:raise RuntimeError(f"TTS failed for {item['id']}: {exc}") from exc
                await asyncio.sleep(attempt*3)

async def main():
    data=json.loads(SRC.read_text(encoding='utf-8'))
    valid=[x for x in data['lessons'] if x['kind']!='listening']
    assert len(data['lessons'])==40,len(data['lessons'])
    assert len(valid)==32,len(valid)
    assert len({x['id'] for x in valid})==32
    assert all(x['text'].strip() and x.get('voice') in VOICE for x in valid)
    (DEST/'audio').mkdir(parents=True,exist_ok=True)
    (DEST/'lessons.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    if not (DEST/'index.html').exists():raise FileNotFoundError(DEST/'index.html')
    sem=asyncio.Semaphore(4)
    await asyncio.gather(*(synth(x,sem) for x in valid))
    assert len(list((DEST/'audio').glob('*.mp3')))==32
    assert all((DEST/'audio'/f"{x['id']}.mp3").stat().st_size>1000 for x in valid)
    print('SUCCESS: 32 audio files + manifest + player ready',flush=True)

if __name__=='__main__':asyncio.run(main())
