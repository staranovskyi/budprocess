"""Нерозривні пробіли в тілі статей довідника: 60 %, 5 000 грн, 12 мм, № 3, 1 000 000.

Запуск після правок content/*.html:  py tools/nbsp.py   (далі py tools/build_dovidnyk.py)
Блок метаданих (до першого порожнього рядка) не чіпає.
"""
import pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent / "content"
for p in sorted(root.glob("*.html")):
    t = p.read_text(encoding="utf-8")
    head, body = t.split("\n\n", 1)
    b = body
    b = re.sub(r"(\d) %", r"\1&nbsp;%", b)
    b = re.sub(r"(\d) (\d{3})(?!\d)", r"\1&nbsp;\2", b)
    b = re.sub(r"(\d)&nbsp;(\d{3}) (\d{3})(?!\d)", r"\1&nbsp;\2&nbsp;\3", b)
    b = re.sub(r"(\d) грн", r"\1&nbsp;грн", b)
    b = re.sub(r"(\d) мм", r"\1&nbsp;мм", b)
    b = re.sub(r"№ (\d)", r"№&nbsp;\1", b)
    if b != body:
        p.write_text(head + "\n\n" + b, encoding="utf-8", newline="\n")
    print(p.name, "nbsp:", b.count("&nbsp;"))
