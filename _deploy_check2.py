"""実デプロイ済み95プロジェクトの【正しいURL】でHTTP実測する。"""
import os, csv, json, concurrent.futures, urllib.request, urllib.error, ssl, re

BASE = os.path.expanduser("~/Desktop/agentic-sites")
rows = []
for line in open(os.path.join(BASE, "_pages_real.txt"), encoding="utf-8"):
    parts = line.split()
    if len(parts) >= 2:
        rows.append({"name": parts[0], "url": "https://" + parts[1] + "/"})

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def check(r):
    try:
        req = urllib.request.Request(r["url"], headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            body = resp.read(200000).decode("utf-8", errors="replace")
            m = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
            return {**r, "status": resp.status, "size": len(body),
                    "title": (m.group(1).strip()[:55] if m else "")}
    except urllib.error.HTTPError as e:
        return {**r, "status": e.code, "size": 0, "title": ""}
    except Exception as e:
        return {**r, "status": 0, "size": 0, "title": str(e)[:30]}


with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    res = list(ex.map(check, rows))

ok = [r for r in res if r["status"] == 200]
bad = [r for r in res if r["status"] != 200]

print("=== デプロイ済み %d サイトの実測 ===" % len(res))
print("  ★200 OK : %d" % len(ok))
print("  ★失敗   : %d" % len(bad))

print("\n=== 失敗一覧 ===")
for r in bad:
    print("  %-32s %s %s" % (r["name"], r["status"], r["url"]))

print("\n=== 成功例（先頭15）===")
for r in ok[:15]:
    print("  %-32s %s | %s" % (r["name"], r["status"], r["title"]))

out = os.path.join(BASE, "_deploy_status_real.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["name", "url", "status", "size", "title"])
    w.writeheader()
    w.writerows(res)
print("\n  saved:", out)
