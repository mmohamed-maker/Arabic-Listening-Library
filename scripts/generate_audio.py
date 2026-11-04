"""Build all learner-facing Arabic audio and listening pages from a single manifest.

The 18 original transcripts are saved in content/lessons.json. Page links are
stable. Voice gender is assigned explicitly per narrator. No secrets required.
Audio is synthesized with an unofficial remote service; review rights and audio.
"""
import argparse
import asyncio
import html
import json
import shutil
from pathlib import Path
import edge_tts

ROOT = Path(__file__).resolve().parents[1]
VOICES = {"male": "ar-SA-HamedNeural", "female": "ar-SA-ZariyahNeural"}
COLORS = {"beginner": "#E83F7C", "intermediate": "#E58A1F", "advanced": "#176EC2"}
LEVELS = {"beginner": "المستوى المبتدئ", "intermediate": "المستوى المتوسط", "advanced": "المستوى المتقدم"}

def lesson_id(lesson):
    return f"{lesson['level']}-unit-{int(lesson['unit']):02d}"

def page_html(lesson):
    ident = lesson_id(lesson)
    title = html.escape(lesson["title"])
    english = html.escape(lesson["en"])
    color = COLORS[lesson["level"]]
    transcript = html.escape(lesson["text"])
    questions = "".join(f"<li>{html.escape(q)}</li>" for q in lesson["questions"])
    return f"""<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | Arabic Made Simple</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#eef8f6;color:#09275d;font:20px/2 Tahoma,Arial,sans-serif}}
main{{max-width:780px;margin:30px auto;background:white;border-radius:24px;padding:clamp(18px,4vw,40px);box-shadow:0 12px 35px #14315b15}}
h1{{color:{color};font-size:clamp(28px,5vw,40px)}}h2{{font-size:24px}}audio{{width:100%;margin:24px 0}}
.tag{{background:{color};color:white;padding:8px 15px;border-radius:20px;font-size:16px;display:inline-block}}
.panel{{background:#fff1c6;padding:14px;border-radius:16px}}.questions{{background:#e5f8f0;padding:18px;border-radius:16px}}
a{{color:#006f8a}}details{{background:#eef5ff;padding:18px;border-radius:15px;margin-top:25px}}
small{{font-size:14px;line-height:1.8;display:block;color:#506b77}}li{{margin-bottom:10px}}
</style></head><body><main>
<div class="tag">{LEVELS[lesson["level"]]} · الوحدة {lesson["unit"]}</div>
<h1>{title}</h1><p dir="ltr" lang="en">{english} | Arabic Made Simple</p>
<div class="panel">اِسْتَمِعْ مَرَّتَيْنِ، ثُمَّ أَجِبْ عَنِ الأَسْئِلَةِ.<div dir="ltr" lang="en">Listen twice, then answer.</div></div>
<audio controls preload="metadata" src="../audio/{ident}.mp3"></audio>
<p><a href="../audio/{ident}.mp3" download>تنزيل التسجيل الصوتي · Download MP3</a></p>
<section class="questions"><h2>أَسْئِلَةُ الاسْتِمَاعِ</h2><ol>{questions}</ol></section>
<details><summary>إظهار النص المسموع · Show transcript</summary><p>{transcript}</p></details>

<p><a href="../index.html">العودة إلى مكتبة الاستماع</a></p></main></body></html>
"""

async def render_with_retries(text, voice, out, rate, attempts=4):
    for attempt in range(1, attempts+1):
        try:
            await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(str(out))
            if out.stat().st_size <= 1000:
                raise RuntimeError("MP3 is unexpectedly small")
            return
        except Exception as exc:
            if attempt == attempts:
                raise RuntimeError(f"Could not generate {out.name} after {attempts} attempts: {exc}") from exc
            print(f"Retry {attempt} for {out.name}: {exc}", flush=True)
            await asyncio.sleep(2 * attempt)

async def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--rate", default="-15%")
    cli.add_argument("--only", default="", help="Optional lesson ID, e.g. beginner-unit-02")
    args=cli.parse_args()
    manifest=json.loads((ROOT/"content/lessons.json").read_text(encoding="utf-8"))
    lessons=manifest["lessons"]
    if len(lessons)!=18 or len({lesson_id(x) for x in lessons})!=18:
        raise ValueError("Expected 18 unique lessons")
    audio_dir=ROOT/"site/audio"
    pages_dir=ROOT/"site/listen"
    audio_dir.mkdir(parents=True,exist_ok=True)
    pages_dir.mkdir(parents=True,exist_ok=True)
    for lesson in lessons:
        ident=lesson_id(lesson)
        if lesson["level"] not in COLORS or lesson["narrator"] not in VOICES:
            raise ValueError(f"Unknown level or narrator for {ident}")
        if not lesson["text"].strip() or len(lesson["questions"])!=3:
            raise ValueError(f"Invalid script or questions for {ident}")
        (pages_dir/f"{ident}.html").write_text(page_html(lesson),encoding="utf-8")
    if not args.only:
        cards="".join(
            f'<a class="lesson" href="listen/{lesson_id(l)}.html"><span>{html.escape(l["title"])}</span><small>{html.escape(l["en"])} · {LEVELS[l["level"]]}</small></a>'
            for l in lessons)
        index=f"""<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
        <title>مكتبة الاستماع — Arabic Made Simple</title><style>body{{font:19px/1.8 Tahoma,Arial;background:#eff7f4;color:#09275d;max-width:900px;margin:auto;padding:30px}}
        h1{{font-size:35px}}.lesson{{display:block;padding:15px 23px;background:white;margin:12px 0;border-right:7px solid #0b9d97;border-radius:14px;text-decoration:none;color:#09275d}}
        small{{display:block;font-size:14px;color:#576976}}a:hover{{background:#fff2c7}}</style>
        <h1>مَكْتَبَةُ الاسْتِمَاعِ — 18 درسًا</h1><p>سلسلة العربية ببساطة: المبتدئ، المتوسط، المتقدم.</p>{cards}</html>"""
        (ROOT/"site/index.html").write_text(index,encoding="utf-8")
    selected=[x for x in lessons if not args.only or lesson_id(x)==args.only]
    if not selected:
        raise SystemExit(f"No lesson matching {args.only}")
    for i, lesson in enumerate(selected,1):
        ident=lesson_id(lesson)
        voice=VOICES[lesson["narrator"]]
        out=audio_dir/f"{ident}.mp3"
        print(f"[{i}/{len(selected)}] {ident}: {voice}",flush=True)
        await render_with_retries(lesson["text"],voice,out,args.rate)
        if ident=="beginner-unit-01":
            shutil.copyfile(out,audio_dir/"unit-01.mp3")
        await asyncio.sleep(0.9)
    # Preserve old textbook QR URLs, by redirecting older site page.
    (pages_dir/"unit-01.html").write_text('<!doctype html><html lang="ar"><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=beginner-unit-01.html"><a href="beginner-unit-01.html">الدرس الأول</a></html>',encoding="utf-8")
    print(f"Generated {len(selected)} MP3 files and {len(lessons)} listening pages.")

if __name__ == "__main__":
    asyncio.run(main())
