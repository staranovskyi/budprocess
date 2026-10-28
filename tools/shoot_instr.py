"""Скріншоти кроків онлайн-сервісу для сторінки /instrukciya — з демо-стенда (tools/demo_stand.py у kbp_tool_stage1).

Запуск:  py tools/shoot_instr.py [--base http://127.0.0.1:8090] [--pvr D:\\Демо\\Демо_ПВР_тестовий_обʼєкт.xlsx]
                                 [--kp "D:\\Демо\\Демо_КП_для_відео\\КП_Дорпромгруп_09.09.2026_асфальт_емульсія_ЩПС.pdf"]
Знімки → img/instr/NN-назва.png (1280×800, 2x). Потім конвертувати у webp (tools/instr_webp.py).
"""
import argparse, pathlib, sys, time
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "img" / "instr"
HIDE_FIXED = """() => { for (const e of document.querySelectorAll('body *')) {
  const cs = getComputedStyle(e);
  if (cs.position === 'fixed' && e.textContent.trim() === 'Підтримка' && e.getBoundingClientRect().width < 260) e.style.visibility = 'hidden'; } }"""


def shot(pg, name, sel=None, full=False):
    pg.evaluate(HIDE_FIXED)
    if sel:
        try:
            pg.locator(sel).first.scroll_into_view_if_needed(timeout=3000)
            pg.evaluate("s => { const e = document.querySelector(s); if (e) window.scrollBy(0, e.getBoundingClientRect().top - 96); }", sel)
        except Exception as e:
            print("  scroll", sel, "→", e)
    pg.wait_for_timeout(400)
    pg.screenshot(path=str(OUT / f"{name}.png"), full_page=full)
    print("shot", name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8090")
    ap.add_argument("--pvr", default=r"D:\Демо\Демо_ПВР_тестовий_обʼєкт.xlsx")
    ap.add_argument("--kp", default=r"D:\Демо\Демо_КП_для_відео\КП_Дорпромгруп_09.09.2026_асфальт_емульсія_ЩПС.pdf")
    ap.add_argument("--email", default="demo@example.com")
    ap.add_argument("--wait", type=int, default=45, help="скільки чекати пошук джерел, с")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=2, locale="uk-UA")
        pg = ctx.new_page()
        pg.goto(a.base + "/")
        pg.wait_for_timeout(1500)
        shot(pg, "01-home")

        # вхід: кнопка «Увійти» → діалог → пошта
        pg.locator("button.login-open, #login_btn, button:has-text('Увійти')").first.click()
        pg.wait_for_timeout(600)
        pg.locator("input[type=email]:visible").first.fill(a.email)
        shot(pg, "02-login")
        pg.locator("button:has-text('Увійти'):visible:not(#nav_login), button:has-text('Надіслати посилання'):visible").first.click()
        pg.wait_for_timeout(2500)
        pg.goto(a.base + "/")
        pg.wait_for_timeout(1500)

        # файл
        pg.set_input_files("#fi", a.pvr)
        pg.wait_for_timeout(4000)
        shot(pg, "03-cost", "#s2")
        pg.locator("button:has-text('Почати аналіз'):visible").first.click()
        # чекаємо коди
        for _ in range(60):
            pg.wait_for_timeout(2000)
            if pg.locator("#poslist .pos").count() > 0:
                break
        pg.wait_for_timeout(1500)
        print("url:", pg.url)
        shot(pg, "04-codes", "#steps")
        shot(pg, "05-codes-list", "#poslist")

        # ручне уточнення коду: перша кнопка «Уточнити код»
        btn = pg.locator("#poslist button:has-text('Уточнити')").first
        if btn.count():
            btn.click()
            pg.wait_for_timeout(1500)
            shot(pg, "06-manual")
            close = pg.locator("button:has-text('Згорнути'), button:has-text('Закрити'), button:has-text('Скасувати')").first
            if close.count():
                try:
                    close.click(timeout=2000)
                except Exception:
                    pass
            pg.wait_for_timeout(500)

        # джерела цін
        go = pg.locator("button:has-text('Знайти джерела цін'):visible").first
        if go.count():
            go.click()
            pg.wait_for_timeout(6000)
            shot(pg, "07-prices-progress", "#prices")
            for _ in range(a.wait // 3 + 10):
                pg.wait_for_timeout(3000)
                if pg.locator("#prices:has-text('Готово')").count() or pg.locator("text=Джерела знайдено").count():
                    break
            pg.wait_for_timeout(1500)
            shot(pg, "08-prices-done", "#prices")
        else:
            print("no prices button")

        # КП
        kpin = pg.locator("input[type=file][accept*='pdf'], input[type=file]#kpf, input[type=file][multiple]").first
        if kpin.count():
            kpin.set_input_files(a.kp)
            pg.wait_for_timeout(3000)
            shot(pg, "09-kp-reading", "text=Комерційні пропозиції")
            for _ in range(20):
                pg.wait_for_timeout(2000)
                if pg.locator("text=Читаємо").count() == 0:
                    break
            pg.wait_for_timeout(1500)
            shot(pg, "10-kp-done", "text=Комерційні пропозиції")
        else:
            print("no kp input")

        # файли для ЄДЕССБ і зауваження
        shot(pg, "11-files", "#files")
        sup = pg.locator("text=Уточніть дані").first
        if sup.count():
            shot(pg, "12-suppliers", "text=Уточніть дані")

        # мої задачі, історія
        pg.goto(a.base + "/#tasks"); pg.wait_for_timeout(2000); shot(pg, "13-tasks")
        pg.goto(a.base + "/#history"); pg.wait_for_timeout(2000); shot(pg, "14-history")
        b.close()


if __name__ == "__main__":
    main()
