"""Збирає сторінки довідника /dovidnyk/ з content/*.html.

Шапка, стилі й підвал беруться з analiz-tsin.html, тож дизайн завжди той самий.
Запуск: py tools/build_dovidnyk.py  (з кореня репозиторію)
Кожен файл у content/ починається з блоку метаданих (рядки "ключ: значення"), далі порожній рядок, далі тіло статті (HTML).
"""
import json, re, sys, pathlib, datetime
from html import unescape

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "content"
OUT = ROOT / "dovidnyk"
BASE = (ROOT / "analiz-tsin.html").read_text(encoding="utf-8")
SITE = "https://budprocess.com"

ARTICLE_CSS = """
.art{max-width:780px;margin:0 auto;padding:36px 0 44px}
.crumbs{font-family:"IBM Plex Mono",monospace;font-size:12.5px;color:var(--muted);margin-bottom:18px}
.crumbs a{text-decoration:none;color:var(--muted)}
.crumbs a:hover{color:var(--ink)}
.art h1{font-size:clamp(28px,4.4vw,42px);line-height:1.15;margin:0 0 14px;max-width:none}
.art .lead{font-size:18px;color:var(--muted);margin-bottom:22px}
.art .meta{font-family:"IBM Plex Mono",monospace;font-size:12.5px;color:var(--muted);margin-bottom:28px;padding-bottom:18px;border-bottom:1px solid var(--line)}
.art .meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.art .meta .ava{width:28px;height:28px;border-radius:50%;object-fit:cover;flex:none}
.author{display:flex;gap:18px;align-items:flex-start;margin:36px 0 0;padding:20px 22px;background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--shadow);font-size:15px;line-height:1.55;color:var(--muted)}
.author img{width:72px;height:72px;border-radius:50%;object-fit:cover;flex:none}
.author b{color:var(--ink);font-size:16px}
.author a{color:var(--amber-dark);text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px;transition:color .13s ease}
.author a:hover{color:var(--ink)}
@media(max-width:560px){.author{padding:16px}.author img{width:56px;height:56px}}
.art h2{font-size:24px;margin:36px 0 12px;max-width:none}
.art h3{font-size:18px;font-weight:600;margin:24px 0 8px}
.art p{margin:0 0 14px}
.art p a:not(.btn),.art li a,.art td a,.art figcaption a{color:var(--amber-dark);text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px;transition:color .13s ease}
.art p a:not(.btn):hover,.art li a:hover,.art td a:hover,.art figcaption a:hover{color:var(--ink)}
.cta-box p a:not(.btn){color:var(--amber)}
.cta-box p a:not(.btn):hover{color:#fff}
.art ul,.art ol{margin:0 0 16px 22px}
.art li{margin-bottom:6px}
.art table{width:100%;border-collapse:collapse;font-size:14.5px;margin:12px 0 20px;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.art th,.art td{padding:9px 12px;text-align:left;border-top:1px solid var(--line);vertical-align:top}
.art th{background:var(--paper);font-weight:600;font-size:13.5px}
.art tr:first-child th{border-top:none}
.art td.r,.art th.r{text-align:right;font-family:"IBM Plex Mono",monospace;white-space:nowrap}
.art .tblw{overflow-x:auto;margin:0 -4px}
.art .note{background:var(--amber-soft);border-left:3px solid var(--amber);border-radius:0 12px 12px 0;padding:14px 18px;margin:18px 0;font-size:15px}
.art .note b{color:#8a6400}
.art .kbp-help{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px 20px;margin:20px 0;font-size:15.5px}
.art .kbp-help b{color:var(--ink)}
.art .kbp-help .kh-b{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.art .kbp-help .kh-b a{display:inline-flex;align-items:center;gap:7px;padding:8px 16px;border-radius:999px;border:1.5px solid var(--line);background:#fff;color:var(--ink);font-weight:600;font-size:14.5px;text-decoration:none;transition:border-color .13s ease,background .13s ease}
.art .kbp-help .kh-b a:hover{border-color:var(--ink)}
.art .kbp-help .kh-b a.kh-main{background:var(--amber);border-color:var(--amber)}
.art .kbp-help .kh-b a.kh-main:hover{background:#e0a800;border-color:#e0a800}
.art .kbp-help .kh-tel{margin-top:10px;font-size:14.5px;color:var(--muted)}
.art .kbp-help .kh-tel a{color:var(--ink);font-weight:600;text-decoration:none;white-space:nowrap;transition:color .13s ease}
.art .kbp-help .kh-tel a:hover{color:var(--amber-dark)}
.art .letter{background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:18px 22px;margin:14px 0 18px;font-size:14.5px;line-height:1.6}
.art .letter p{margin:0 0 10px}
.art .letter table{font-size:13.5px;margin:8px 0 12px}
.art .letter .muted{color:var(--muted)}
.art a.btn-dl{display:inline-flex;align-items:center;gap:8px;margin:4px 0 18px;padding:10px 18px;border-radius:999px;background:var(--amber);color:var(--ink);font-weight:600;text-decoration:none;transition:background .13s ease}
.art a.btn-dl:hover{background:#e0a800}
.art .svc-kp{margin:36px 0 8px;background:var(--card);border:1px solid var(--line);border-top:3px solid var(--amber);border-radius:var(--r);padding:24px 26px;box-shadow:var(--shadow)}
.art .svc-kp h2{margin:0 0 10px;font-size:22px}
.art .svc-kp ol{margin:6px 0 12px 20px}
.art .svc-kp .svc-note{font-size:14.5px;color:var(--muted)}
.art .svc-kp .svc-price{font-family:"IBM Plex Mono",monospace;font-weight:600;font-size:18px;margin:4px 0 14px}
.art .svc-kp button,.art .svc-kp .svc-form button{font:inherit;font-weight:600;padding:11px 22px;border-radius:999px;border:0;background:var(--amber);color:var(--ink);cursor:pointer;transition:background .13s ease}
.art .svc-kp button:hover{background:#e0a800}
.art .svc-kp button:disabled{opacity:.6;cursor:default}
.art .svc-kp .svc-alt{margin:12px 0 0;font-size:14.5px;color:var(--muted)}
.art .svc-kp .svc-alt a{color:var(--ink);font-weight:600;white-space:nowrap}
.art .svc-form{display:grid;gap:12px;margin-top:6px}
.art .svc-form[hidden],.art .svc-ok[hidden]{display:none}
.art .svc-form label{display:grid;gap:5px;font-size:14px;font-weight:600}
.art .svc-form label span{font-weight:400;color:var(--muted)}
.art .svc-form input,.art .svc-form textarea{font:inherit;font-size:15px;padding:10px 12px;border:1.5px solid var(--line);border-radius:10px;background:#fff;color:var(--ink)}
.art .svc-form input:focus,.art .svc-form textarea:focus{outline:none;border-color:var(--amber)}
.art .svc-form textarea{min-height:90px;resize:vertical}
.art .svc-form .hp{position:absolute;left:-9999px}
.art .svc-form .svc-err{color:#9B2C2C;font-size:14px}
.art .svc-form .svc-legal{font-size:13px;color:var(--muted)}
.art .svc-ok{background:#EEF6F1;color:#1F5E46;border-radius:10px;padding:12px 16px;font-weight:600}
.art figure{margin:20px 0;background:#fff;border:1px solid var(--line);border-radius:var(--r);overflow:hidden;box-shadow:var(--shadow)}
.art figure img{display:block;width:100%;height:auto}
.art figcaption{font-size:13.5px;color:var(--muted);padding:10px 16px;border-top:1px solid var(--line)}
.cta-box{margin:36px 0 8px;background:var(--ink);color:#fff;border-radius:20px;padding:30px 32px;position:relative;overflow:hidden}
.cta-box::after{content:"";position:absolute;top:0;right:0;width:44px;height:44px;background:linear-gradient(225deg,transparent 0 50%,var(--amber) 50% 100%)}
.cta-box h2{color:#fff;font-size:22px;margin:0 0 8px}
.cta-box p{opacity:.85;margin:0 0 18px;font-size:15.5px;max-width:560px}
.cta-box .btn-amber{box-shadow:none}
.cta-box .btn-line{background:transparent;color:#fff;border-color:rgba(255,255,255,.35)}
.cta-box .btn-line:hover{border-color:#fff}
.cta-box .gift{display:inline-block;margin-left:10px;background:var(--amber);color:var(--ink);font-weight:700;font-size:13.5px;padding:5px 11px;border-radius:999px;vertical-align:middle}
@media(max-width:560px){.cta-box{padding:24px 20px}.cta-box .gift{margin:10px 0 0}}
.art .faq{margin-top:12px}
.step-h{display:flex;align-items:center;gap:14px;margin:40px 0 10px}
.step-h .n{flex:none;width:40px;height:40px;border-radius:12px;background:var(--ink);color:#fff;display:grid;place-items:center;font-family:"IBM Plex Mono",monospace;font-weight:600;font-size:18px}
.step-h h2{margin:0}
.art .do{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--amber);border-radius:0 12px 12px 0;padding:12px 18px;margin:0 0 14px;font-size:15.5px}
.art .do b{color:#8a6400}
.art .toc{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:18px 22px;margin:0 0 8px}
.art .toc ol{margin:8px 0 0 20px;columns:2;column-gap:28px}
@media(max-width:560px){.art .toc ol{columns:1}}
.art .toc li{margin:0 0 4px;font-size:15px;break-inside:avoid}
.more{margin:40px 0 0;padding-top:24px;border-top:1px solid var(--line)}
.more h2{font-size:18px;margin:0 0 12px}
.more ul{list-style:none;margin:0;padding:0}
.more li{margin:0 0 8px}
.more a{font-weight:600}
.idx{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:8px}
@media(max-width:720px){.idx{grid-template-columns:1fr}}
.idx a{display:flex;flex-direction:column;text-decoration:none;background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden;box-shadow:var(--shadow);transition:transform .13s ease,border-color .13s ease}
.idx a:hover{transform:translateY(-2px);border-color:var(--amber)}
.idx img,.idx .noimg{display:block;width:100%;aspect-ratio:16/8;object-fit:cover;object-position:top left;background:var(--paper);border-bottom:1px solid var(--line)}
.idx a>div{padding:18px 22px 22px}
.idx h3{font-size:17px;font-weight:600;margin:0 0 6px;color:var(--ink)}
.idx p{font-size:14.5px;color:var(--muted);margin:0}
"""

AUTHOR = {"name": "Станіслав", "role": "засновник BudProcess"}
AUTHOR_CARD = """<div class="author">
<img src="/img/author.webp" width="72" height="72" alt="Станіслав, автор довідника BudProcess" loading="lazy">
<div><b>Станіслав</b>, засновник BudProcess<br>Створює сервіс аналізу цін і керує всіма процесами: від розробки до підготовки звітів. Матеріали довідника перевіряє сертифікований інженер-кошторисник команди з досвідом роботи головним інженером будівельної компанії. <a href="/analiz-tsin#contact">Поставити питання</a></div>
</div>"""

CTA = """<div class="cta-box">
<h2>Зробіть аналіз цін онлайн за кілька годин</h2>
<p>Завантажте відомість ресурсів (ПВР або РЛМТ). Сервіс підбере коди КБП, знайде джерела цін і збере три обмінні файли для ЄДЕССБ.</p>
<a class="btn btn-amber" href="https://app.budprocess.com/">Відкрити сервіс</a><span class="gift">Перші 500 грн — за наш рахунок</span>
<p style="margin:18px 0 0;font-size:14px">Потрібен комплект під ключ зі спеціалістом? <a href="/analiz-tsin#contact">Надішліть кошторис</a>, оцінка безкоштовна.</p>
</div>"""


MONTHS = ["січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]


def human(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


def section(html, tag):
    m = re.search(rf"<{tag}\b.*?</{tag}>", html, re.S)
    return m.group(0)


def base_css():
    m = re.search(r"<style>(.*?)</style>", BASE, re.S)
    return m.group(1)


def header(active):
    h = section(BASE, "header").replace(' aria-current="page"', "")
    cur = ' aria-current="page"' if active == "dovidnyk" else ""
    if '<a href="/dovidnyk/">Довідник</a>' in h:
        return h.replace('<a href="/dovidnyk/">Довідник</a>', f'<a href="/dovidnyk/"{cur}>Довідник</a>')
    return h.replace('<a href="/koshtorysy">Кошториси</a>', f'<a href="/koshtorysy">Кошториси</a>\n<a href="/dovidnyk/"{cur}>Довідник</a>')


def footer():
    f = section(BASE, "footer")
    if "/dovidnyk/" in f:
        return f
    return f.replace('<a href="/koshtorysy">Кошториси</a>', '<a href="/koshtorysy">Кошториси</a><a href="/dovidnyk/">Довідник</a>')


_ga0 = BASE.find("<!-- Google Analytics 4 -->")
_ga1 = BASE.find("</script>", BASE.find("</script>", _ga0) + 1) + len("</script>")
GA = BASE[_ga0:_ga1]  # блок GA4: підключення + gtag('config')
SCRIPTS = BASE[BASE.rfind("<script>"):BASE.rfind("</script>") + 9]  # останній <script> — плавний скрол, липка панель, події кліків


def parse(path):
    txt = path.read_text(encoding="utf-8")
    head, body = txt.split("\n\n", 1)
    meta = {}
    for line in head.splitlines():
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    meta["faq"] = []
    # FAQ — блок <!--faq--> ... <!--/faq--> з <details>
    m = re.search(r"<!--faq-->(.*?)<!--/faq-->", body, re.S)
    if m:
        for q, a in re.findall(r"<summary>(.*?)</summary>\s*<p>(.*?)</p>", m.group(1), re.S):
            meta["faq"].append((re.sub("<.*?>", "", q), re.sub("<.*?>", "", a)))
    return meta, body


def page(meta, body, others):
    slug = meta["slug"]
    standalone = meta.get("kind") == "page"
    url = f"{SITE}/{slug}" if standalone else f"{SITE}/dovidnyk/{slug}"
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Article", "headline": meta["title"], "description": meta["description"], "url": url,
             "datePublished": meta.get("date", "2026-10-15"), "dateModified": meta.get("updated", meta.get("date", "2026-10-15")),
             "inLanguage": "uk", "author": {"@type": "Person", "name": AUTHOR["name"], "jobTitle": AUTHOR["role"], "image": SITE + "/img/author.webp", "worksFor": {"@type": "Organization", "name": "BudProcess", "url": SITE + "/"}},
             "publisher": {"@type": "Organization", "name": "BudProcess", "url": SITE + "/", "logo": {"@type": "ImageObject", "url": SITE + "/icon-192.png"}},
             "image": SITE + meta.get("image", "/og-image.jpg")},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Головна", "item": SITE + "/"},
                *([] if standalone else [{"@type": "ListItem", "position": 2, "name": "Довідник", "item": SITE + "/dovidnyk/"}]),
                {"@type": "ListItem", "position": 2 if standalone else 3, "name": meta.get("short", meta["h1"]), "item": url}]},
        ]}
    if meta.get("faq"):   # питання з блоку <!--faq--> — і для пошуковиків (розмітка FAQPage), 2026-10-29
        ld["@graph"].append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": unescape(q), "acceptedAnswer": {"@type": "Answer", "text": unescape(a)}} for q, a in meta["faq"]]})
    more = "".join(f'<li><a href="/dovidnyk/{o["slug"]}">{o["h1"]}</a></li>' for o in others)
    more_block = "" if standalone else f'<div class="more"><h2>Ще в довіднику</h2><ul>{more}</ul></div>'
    crumbs = (f'<a href="/">Головна</a> → {meta.get("short", meta["h1"])}' if standalone
              else f'<a href="/">Головна</a> → <a href="/dovidnyk/">Довідник</a> → {meta.get("short", meta["h1"])}')
    return f"""<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta["title"]}</title>
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<meta name="theme-color" content="#1A2230">
<meta name="description" content="{meta["description"]}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{base_css()}{ARTICLE_CSS}</style>
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="BudProcess">
<meta property="og:locale" content="uk_UA">
<meta property="og:title" content="{meta["title"]}">
<meta property="og:description" content="{meta["description"]}">
<meta property="og:image" content="{SITE}{meta.get("image", "/og-image.jpg")}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{meta["title"]}">
<meta name="twitter:description" content="{meta["description"]}">
<meta name="twitter:image" content="{SITE}{meta.get("image", "/og-image.jpg")}">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
{GA}
</head>
<body>
{header("" if standalone else "dovidnyk")}
<main>
<div class="wrap">
<article class="art">
<div class="crumbs">{crumbs}</div>
<h1>{meta["h1"]}</h1>
<p class="lead">{meta["lead"]}</p>
<div class="meta"><img class="ava" src="/img/author.webp" width="28" height="28" alt="">{AUTHOR["name"]}, {AUTHOR["role"]} · Оновлено {human(meta.get("updated", meta.get("date", "2026-10-15")))} · {meta.get("read", "7")} хв читання</div>
{body.strip()}
{'' if standalone or meta.get("cta") == "no" else CTA}
{more_block}
</article>
</div>
</main>
{footer()}
{SCRIPTS}
</body>
</html>
"""


def index(pages):
    cards = "".join(
        f'<a href="/dovidnyk/{m["slug"]}">'
        + (f'<img src="{m["image"]}" alt="" loading="lazy">' if m.get("image") else '<span class="noimg"></span>')
        + f'<div><h3>{m.get("card_title", m["h1"])}</h3><p>{m.get("card", m["lead"])}</p></div></a>'
        for m, _ in pages)
    url = SITE + "/dovidnyk/"
    title = "Довідник з аналізу цін і ЄДЕССБ"
    desc = "Аналіз цін для ЄДЕССБ крок за кроком: підбір джерел і цінових пропозицій, коди КБП, ранжування 60/30/10, обмінні файли та їх завантаження в ЄДЕССБ."
    return f"""<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | BudProcess</title>
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<meta name="theme-color" content="#1A2230">
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{base_css()}{ARTICLE_CSS}</style>
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="BudProcess">
<meta property="og:locale" content="uk_UA">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/og-image.jpg">
{GA}
</head>
<body>
{header("dovidnyk")}
<main>
<div class="wrap">
<article class="art" style="max-width:980px">
<div class="crumbs"><a href="/">Головна</a> → Довідник</div>
<h1>Довідник: аналіз цін для ЄДЕССБ</h1>
<p class="lead">Аналіз цін — фактично це процес підбору джерел і цінових пропозицій, кодів КБП, формування обмінних файлів і завантаження їх у ЄДЕССБ. У довіднику розібрано кожен із цих кроків: що потрібно, звідки брати дані і де найчастіше помиляються.</p>
<div class="idx">{cards}</div>
</article>
</div>
</main>
{footer()}
{SCRIPTS}
</body>
</html>
"""


def main():
    OUT.mkdir(exist_ok=True)
    allp = [parse(p) for p in sorted(SRC.glob("*.html"))]
    standalone = [(m, b) for m, b in allp if m.get("kind") == "page"]
    pages = [(m, b) for m, b in allp if m.get("kind") != "page"]
    pages.sort(key=lambda mb: int(mb[0].get("order", "99")))
    metas = [m for m, _ in pages]
    for m, body in pages:
        others = [o for o in metas if o["slug"] != m["slug"]]
        (OUT / f'{m["slug"]}.html').write_text(page(m, body, others), encoding="utf-8", newline="\n")
        print("built", m["slug"], "faq:", len(m["faq"]))
    for m, body in standalone:
        (ROOT / f'{m["slug"]}.html').write_text(page(m, body, []), encoding="utf-8", newline="\n")
        print("built page", m["slug"])
    (OUT / "index.html").write_text(index(pages), encoding="utf-8", newline="\n")
    print("built index,", len(pages), "pages")
    # sitemap
    sm = ROOT / "sitemap.xml"
    txt = sm.read_text(encoding="utf-8")
    txt = re.sub(r"\s*<url><loc>https://budprocess.com/dovidnyk/.*?</url>", "", txt)
    for m, _ in standalone:
        txt = re.sub(r"\s*<url><loc>https://budprocess.com/" + re.escape(m["slug"]) + r"</loc>.*?</url>", "", txt)
    today = datetime.date.today().isoformat()
    rows = [f"  <url><loc>{SITE}/dovidnyk/</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>"]
    rows += [f'  <url><loc>{SITE}/dovidnyk/{m["slug"]}</loc><lastmod>{m.get("updated", m.get("date", today))}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>' for m in metas]
    rows += [f'  <url><loc>{SITE}/{m["slug"]}</loc><lastmod>{m.get("updated", m.get("date", today))}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>' for m, _ in standalone]
    txt = txt.replace("</urlset>", "\n".join(rows) + "\n</urlset>")
    sm.write_text(txt, encoding="utf-8", newline="\n")
    print("sitemap updated")


if __name__ == "__main__":
    main()
