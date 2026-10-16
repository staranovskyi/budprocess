"""Локальний перегляд сайту як на GitHub Pages: адреси без .html і теки з index.html.

Запуск з кореня репозиторію:  py tools/serve.py        (порт 8787, http://localhost:8787/)
Інший порт:                   py tools/serve.py 8790
"""
import http.server, mimetypes, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
mimetypes.add_type("image/webp", ".webp")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def translate_path(self, path):
        p = pathlib.Path(super().translate_path(path))
        if not p.exists() and not p.suffix and p.with_suffix(".html").exists():
            return str(p.with_suffix(".html"))
        return str(p)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
print(f"http://localhost:{port}/   (Ctrl+C — зупинити)")
http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
