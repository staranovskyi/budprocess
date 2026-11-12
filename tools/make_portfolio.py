# -*- coding: utf-8 -*-
"""Портфоліо лендингу БЕЗ окремих об'єктів: сторінка portfolio.html і блок «Досвід» на analiz-tsin.html — лише зведені цифри.
Оболонка сторінки (head, шапка, футер, скрипти) береться з analiz-tsin.html.
Запуск: python tools/make_portfolio.py <тека лендингу>.

Рішення власника 2026-11-12: жодних карток об'єктів (ні назв, ні адрес, ні цифр окремого об'єкта) — «щоб ніхто не зміг
зорієнтуватись, який це конкретно об'єкт». Показуємо лише підсумки по всіх об'єктах, напрями, види робіт, розмір і перелік
областей (без кількості об'єктів в області, у порядку за кількістю жителів). Новий об'єкт = оновити числа нижче."""
import html
import io
import re
import sys

LAND = sys.argv[1]
SRC = LAND + r"\analiz-tsin.html"
src = io.open(SRC, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in src else "\n"
src = src.replace("\r\n", "\n")
e = html.escape

# ---- дані: підсумки за відомостями ресурсів власника (кожен об'єкт один раз)
# 2026-11-12: +харчоблок ліцею (ПВР іншого формату, пораховано окремо: 155 позицій, 7 ціноутворюючих, 1,5 млн) і основні
# роботи по лікарні (834 / 44 / 15,2 млн) — лікарня вже була в переліку з «додатковими роботами», тому це той самий об'єкт:
# додались лише його позиції й сума, кількість об'єктів зросла на один.
OBJECTS, REGIONS_N, TOWNS = 38, 10, 27
POSITIONS, PRICING, MATERIALS = "10 705", "503", "406,5 млн грн"
SECT = [("Енергетика", 10, "сонячні й фотоелектричні станції, електропостачання, освітлення"),
        ("Освіта", 9, "ліцеї, школи, дитячі садки, заклади вищої освіти"),
        ("Житло і громадські будівлі", 6, "житлові будинки, адміністративні будівлі, будинки культури"),
        ("Укриття", 4, "укриття в закладах освіти й адміністративних будівлях"),
        ("Тепло, вода, газ", 4, "котельні, мережі водопостачання, газопостачання"),
        ("Медицина", 3, "лікарні, амбулаторії"),
        ("Дороги і мости", 2, "мости на автомобільних дорогах")]
WORK = [("Капітальний ремонт", 21), ("Реконструкція", 12), ("Нове будівництво", 4), ("Встановлення обладнання", 1)]
SIZE = [("до 1 млн грн", 17), ("1–10 млн грн", 12), ("понад 10 млн грн", 9)]
# області — лише перелік, у порядку за кількістю жителів (Держстат, на 01.01.2022; Київська — без міста Києва)
REG = ["Дніпропетровська", "Львівська", "Одеська", "Київська", "Полтавська", "Черкаська", "Сумська", "Тернопільська", "Херсонська", "Чернівецька"]
assert sum(n for _, n, _ in SECT) == sum(n for _, n in WORK) == sum(n for _, n in SIZE) == OBJECTS and len(REG) == REGIONS_N


def tile(a, b):
    return f'<div class="obj-num"><b>{e(a)}</b><span>{e(b)}</span></div>'


# ---- сторінка послуги: стилі блоку і сам блок «Досвід» (цифри, напрями плашками, кнопка на портфоліо)
CSS_BLOCK = '''/* досвід у цифрах: підсумки й напрями без окремих об'єктів (рішення власника 2026-11-12); докладніше — /portfolio.
   Блок і ці стилі пише tools/make_portfolio.py — вручну не правити */
.obj-lead{font-size:16.5px;color:var(--muted);max-width:700px;margin:-16px 0 24px}
.obj-nums{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin-bottom:16px}
.obj-num{background:var(--ink);color:#fff;border-radius:var(--r);padding:20px 22px}
.obj-num b{display:block;font-family:"IBM Plex Mono",monospace;font-size:clamp(22px,2.1vw,26px);font-weight:600;line-height:1.15;color:var(--amber);white-space:nowrap}
.obj-num span{display:block;font-size:13.5px;opacity:.82;margin-top:4px;line-height:1.35}
.pf-chips{display:flex;flex-wrap:wrap;gap:8px}
.pf-chips span{font-size:14px;padding:7px 13px;border-radius:999px;background:var(--card);border:1px solid var(--line)}
.pf-chips span b{font-family:"IBM Plex Mono",monospace;font-weight:600;margin-left:6px;color:var(--amber-dark)}
.obj-more{margin-top:18px}
@media(max-width:1000px){.obj-nums{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:640px){.obj-num{padding:16px 16px}.obj-num b{font-size:22px;white-space:normal}}
'''
a = src.index("/* ", src.index(".client span{"))
b = src.index("@media(max-width:820px){.svc{")
src = src[:a] + CSS_BLOCK + src[b:]

BLOCK = f'''<section id="objects">
<div class="wrap">
<div class="sec-label">Досвід</div>
<h2>{OBJECTS} об'єктів з нашим аналізом цін</h2>
<p class="obj-lead">З нашим аналізом цін проєкти проходять експертизу і тендери, один з них пройшов відбір у державній системі DREAM.</p>
<div class="obj-nums">
{tile(str(OBJECTS), f"об'єктів у {REGIONS_N} областях")}
{tile(POSITIONS, "позицій матеріалів")}
{tile(PRICING, "ціноутворюючі позиції")}
{tile(MATERIALS, "вартість матеріалів у відомостях")}
</div>
<div class="pf-chips">{"".join(f"<span>{e(t)}<b>{n}</b></span>" for t, n, _ in SECT)}</div>
<div class="obj-more"><a class="btn btn-line" href="/portfolio">Докладніше в портфоліо</a></div>
</div>
</section>
'''
a = src.index('<section id="objects">')
b = src.index("</section>\n", a) + len("</section>\n")
src = src[:a] + BLOCK + src[b:]
io.open(SRC, "w", encoding="utf-8", newline="").write(src.replace("\n", NL))

# ---- сторінка портфоліо
TITLE = "Портфоліо: досвід аналізу цін для ЄДЕССБ у цифрах | BudProcess"
DESC = (f"{OBJECTS} об'єктів у {REGIONS_N} областях, для яких ми підготували аналіз цін на матеріальні ресурси: освіта, медицина, "
        "укриття, енергетика, дороги і мости. З нашим аналізом цін проєкти проходять експертизу і тендери.")
OG = "BudProcess — досвід аналізу цін у цифрах"
URL = "https://budprocess.com/portfolio"
ea = lambda s: html.escape(s, quote=True)

head, rest = src.split("<main>", 1)
tail = rest.split("</main>", 1)[1]
head = re.sub(r"<title>.*?</title>", f"<title>{e(TITLE)}</title>", head, count=1, flags=re.S)
head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{ea(DESC)}">', head, count=1)
head = re.sub(r'<meta name="keywords" content="[^"]*">\n', "", head, count=1)
head = head.replace('href="https://budprocess.com/analiz-tsin">', f'href="{URL}">', 1)
# сторінка відкрита для індексації (власник 2026-11-12, після того як з неї прибрали об'єкти): «index, follow» лишається
# зі сторінки послуги, адреса є в sitemap.xml. Поки на сторінці були картки об'єктів, вона була закрита (noindex).
assert head.count('<meta name="robots" content="index, follow">') == 1
head = re.sub(r'(<meta property="og:url" content=")[^"]*', r"\g<1>" + URL, head, count=1)
for prop in ('property="og:title"', 'name="twitter:title"'):
    head = re.sub(r"(<meta " + prop + r' content=")[^"]*', lambda m: m.group(1) + ea(OG), head, count=1)
for prop in ('property="og:description"', 'name="twitter:description"'):
    head = re.sub(r"(<meta " + prop + r' content=")[^"]*', lambda m: m.group(1) + ea(DESC), head, count=1)
ld = ('<script type="application/ld+json">\n{\n"@context": "https://schema.org",\n"@type": "WebPage",\n'
      f'"name": "Досвід аналізу цін BudProcess у цифрах",\n"url": "{URL}",\n"description": "{DESC}",\n'
      '"isPartOf": { "@type": "WebSite", "name": "BudProcess", "url": "https://budprocess.com/" }\n}\n</script>')
head, n = re.subn(r'<script type="application/ld\+json">.*?</script>', lambda m: ld, head, count=1, flags=re.S)
assert n == 1
assert '<a href="/analiz-tsin" aria-current="page">' in head
head = head.replace('<a href="/analiz-tsin" aria-current="page">', '<a href="/analiz-tsin">', 1)
assert head.count('<a href="/portfolio">Портфоліо</a>') == 1      # пункт верхнього меню (футер — у tail)
head = head.replace('<a href="/portfolio">Портфоліо</a>', '<a href="/portfolio" aria-current="page">Портфоліо</a>', 1)
tail = tail.replace('<a class="btn btn-line" href="#contact">Під ключ</a>', '<a class="btn btn-line" href="/analiz-tsin#contact">Під ключ</a>', 1)

# свої стилі сторінки. Вертикальний ритм (крок 8 px): текст → цифри 24, цифри → перший розділ 56, розділ → розділ 56,
# заголовок розділу → картки 24, картки між собою 16, останній розділ → завершальний блок 56, блок → футер 64
CSS_PAGE = '''.hero{padding-bottom:0}.hero .pitch{margin-bottom:0}
#numbers{padding:24px 0 28px}
main section.pf{padding:28px 0}
.pf-nums{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.pf-nums .obj-num b{font-size:clamp(24px,3vw,32px)}
.pf-h{margin-bottom:24px}.pf-h h2{margin:0;line-height:1.2}
.pf-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}
.pf-sec{background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--shadow);padding:22px}
.pf-sec .n{font-family:"IBM Plex Mono",monospace;font-size:34px;font-weight:600;line-height:1;color:var(--amber-dark)}
.pf-sec h3{font-size:17.5px;font-weight:600;margin:10px 0 6px;line-height:1.3}
.pf-sec p{font-size:13.5px;color:var(--muted);line-height:1.5;margin:0}
.pf-sec.dark{background:var(--ink);color:#fff;border-color:var(--ink)}.pf-sec.dark p{color:#fff;opacity:.82}.pf-sec.dark .n{color:var(--amber)}
.pf-two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;align-items:start}
.pf-card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--shadow);padding:24px 26px}
.pf-card h3{font-size:17px;font-weight:600;margin:0 0 12px}
.pf-card h3+.pf-list+h3{margin-top:24px}
.pf-list div{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:7px 0;border-top:1px solid var(--line);font-size:14.5px}
.pf-list div:first-child{border-top:0}.pf-list b{font-family:"IBM Plex Mono",monospace;font-weight:600}
.pf-card .pf-chips span{background:var(--paper)}
#next{padding:28px 0 64px}
.obj-next{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--amber);border-radius:var(--r);box-shadow:var(--shadow);padding:28px 30px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:18px 32px}
.obj-next h2{margin:0;max-width:520px;font-size:clamp(20px,2.6vw,26px);line-height:1.3}
.obj-cta{justify-content:flex-start;flex-wrap:wrap}
@media(max-width:1000px){.pf-nums,.pf-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:700px){.pf-two{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.pf-grid{grid-template-columns:minmax(0,1fr)}}
'''
rows = lambda items: "".join(f"<div><span>{e(t)}</span><b>{n}</b></div>" for t, n in items)
main = f'''<main>
<div class="hero">
<span class="kicker">Портфоліо</span>
<h1>{OBJECTS} об'єктів у {REGIONS_N} областях</h1>
<p class="pitch">Школи, лікарні, укриття, мости, сонячні станції. З нашим аналізом цін проєкти <b>проходять експертизу і тендери</b>.</p>
</div>

<section id="numbers">
<div class="wrap">
<div class="pf-nums">
{tile(str(OBJECTS), "об'єктів")}
{tile(str(REGIONS_N), "областей")}
{tile(str(TOWNS), "населених пунктів")}
{tile(POSITIONS, "позицій матеріалів")}
{tile(PRICING, "ціноутворюючі позиції")}
{tile(MATERIALS, "вартість матеріалів у відомостях")}
</div>
</div>
</section>

<section class="pf">
<div class="wrap">
<div class="pf-h"><h2>Напрями</h2></div>
<div class="pf-grid">
{chr(10).join(f'<div class="pf-sec"><div class="n">{n}</div><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, n, d in SECT)}
<div class="pf-sec dark"><div class="n">DREAM</div><h3>Відбір у державній системі</h3><p>Один з проєктів з нашим аналізом цін пройшов відбір у системі управління публічними інвестиціями DREAM.</p></div>
</div>
</div>
</section>

<section class="pf">
<div class="wrap">
<div class="pf-two">
<div class="pf-card"><h3>Види робіт</h3><div class="pf-list">{rows(WORK)}</div><h3>Розмір об'єкта за вартістю матеріалів</h3><div class="pf-list">{rows(SIZE)}</div></div>
<div class="pf-card"><h3>Області</h3><div class="pf-chips">{"".join(f"<span>{e(t)}</span>" for t in REG)}</div></div>
</div>
</div>
</section>

<section id="next">
<div class="wrap">
<div class="obj-next">
<h2>Потрібен аналіз цін для вашого кошторису?</h2>
<div class="cta-row obj-cta">
<a class="btn btn-amber" href="https://app.budprocess.com/">Зробити онлайн</a>
<a class="btn btn-line" href="/analiz-tsin#contact">Замовити під ключ</a>
</div>
</div>
</div>
</section>
</main>'''
out = head.replace("</style>", CSS_PAGE + "</style>", 1) + main + tail
io.open(LAND + r"\portfolio.html", "w", encoding="utf-8", newline="").write(out.replace("\n", NL))
print("portfolio.html", len(out), "символів; блок на analiz-tsin.html оновлено")
