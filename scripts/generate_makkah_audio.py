"""Generate the Grade 6 Makkah listening narration and learner page.
Audio is synthesized via edge-tts (unofficial service), not GitHub itself.
"""
import asyncio
import html
from pathlib import Path
import edge_tts

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "makkah-grade6.txt"
OUTPUT = ROOT / "site" / "audio" / "makkah-grade6.mp3"
PAGE = ROOT / "site" / "listen" / "makkah-grade6.html"
INDEX = ROOT / "site" / "index.html"
MARKER = "<!-- GRADE6_MAKKAH_LINK -->"

def build_page(transcript):
    escaped = html.escape(transcript).replace("\n\n", "</p><p>")
    return f"""<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>رِحْلَتِي إِلَى مَكَّةَ | مدار العربية</title>
<style>body{{margin:0;background:#edf7f5;color:#173c47;font:20px/1.9 Tahoma,Arial,sans-serif}}
main{{max-width:780px;margin:32px auto;padding:clamp(18px,5vw,38px);border-radius:22px;background:#fff;box-shadow:0 12px 30px #153d4415}}
h1{{color:#08776d;line-height:1.5}}audio{{width:100%;margin:20px 0}}.tag{{background:#d7f6ea;padding:7px 14px;border-radius:16px}}
a{{color:#075b82}}.download{{display:inline-block;margin:8px 0 20px;padding:10px 16px;background:#e8f4ff;border-radius:12px}}
details{{padding:15px;background:#f2f5ff;border-radius:12px;margin-top:18px}}
small{{display:block;color:#546a74;line-height:1.8}}</style>
</head><body><main>
<small>مدار العربية · إعداد: الأستاذ محمود محمد · IB MYP Arabic Acquisition</small>
<p><span class="tag">الصف السادس · المستوى المنخفض</span></p>
<h1>رِحْلَتِي إِلَى مَكَّةَ الْمُكَرَّمَةِ</h1>
<p>استمع إلى النص، ثم أجب عن أسئلة الاستماع التي يحددها المعلم.</p>
<audio controls preload="metadata" aria-label="تسجيل رحلة العمرة">
<source src="../audio/makkah-grade6.mp3" type="audio/mpeg">متصفحك لا يدعم تشغيل الصوت.</audio>
<p><a class="download" href="../audio/makkah-grade6.mp3" download>تنزيل التسجيل الصوتي MP3</a></p>
<details><summary>إظهار النص المشكول (للمعلم أو للمراجعة بعد التقييم)</summary>
<p>{escaped}</p></details>
<p><a href="../index.html">العودة إلى مكتبة الاستماع</a></p>
</main></body></html>"""

async def main():
    transcript = SOURCE.read_text(encoding="utf-8").strip()
    if len(transcript) < 400:
        raise ValueError("Missing or truncated Grade 6 source")
    PAGE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PAGE.write_text(build_page(transcript), encoding="utf-8")
    link = '<a class="lesson" href="listen/makkah-grade6.html"><span>رِحْلَتِي إِلَى مَكَّةَ الْمُكَرَّمَةِ</span><small>الصف السادس · المستوى المنخفض · استماع العمرة</small></a>'
    index = INDEX.read_text(encoding="utf-8")
    if 'listen/makkah-grade6.html' not in index:
        index = index.replace("</html>", link + MARKER + "</html>")
        INDEX.write_text(index, encoding="utf-8")
    for attempt in range(1, 5):
        try:
            await edge_tts.Communicate(text=transcript, voice="ar-SA-ZariyahNeural", rate="-20%").save(str(OUTPUT))
            if OUTPUT.stat().st_size < 1000:
                raise RuntimeError("Generated MP3 unexpectedly small")
            print(f"Grade 6 Makkah generated: {OUTPUT.stat().st_size} bytes")
            return
        except Exception as exc:
            if attempt == 4:
                raise RuntimeError(f"Arabic speech generation failed: {exc}") from exc
            await asyncio.sleep(attempt * 3)

if __name__ == "__main__":
    asyncio.run(main())
