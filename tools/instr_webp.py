"""img/instr/*.png → *.webp (ширина 1600, якість 82); png після конвертації видаляються (їх відтворює tools/shoot_instr.py)."""
import pathlib
from PIL import Image

d = pathlib.Path(__file__).resolve().parent.parent / "img" / "instr"
for p in sorted(d.glob("*.png")):
    im = Image.open(p).convert("RGB")
    if im.width > 1600:
        im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    out = p.with_suffix(".webp")
    im.save(out, "WEBP", quality=82, method=6)
    p.unlink()
    print(out.name, im.size, out.stat().st_size)
