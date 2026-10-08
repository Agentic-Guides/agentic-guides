"""77サイト（実際は149）のデプロイ状況をHTTPで実測する。

各サイトについて:
  - Cloudflare Pages の URL（<name>.pages.dev）にアクセス
  - HTTPステータス / タイトル / コンテンツ長 を確認
  - 結果をCSVに保存
"""
import json, os, sys, csv, concurrent.futures, urllib.request, urllib.error, ssl

BASE = os.path.expanduser("~/Desktop/agentic-sites")
targets = json.load(open(os.path.join(BASE, "_ai-search-targets.json"), encoding="utf-8"))
print("対象:", len(targets))

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def check(name):
    # 候補URL（複数のドメインパターンを試す）
    urls = [
        "https://%s.pages.dev/" % name,
    ]
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
                body = r.read(200000).decode("utf-8", errors="replace")
                title = ""
                import re as _re
                m = _re.search(r"<title[^>]*>(.*?)</title>", body, _re.I | _re.S)
                if m:
                    title = m.group(1).strip()[:60]
                return {"name": name, "url": u, "status": r.status, "size": len(body), "title": title, "err": ""}
        except urllib.error.HTTPError as e:
            return {"name": name, "url": u, "status": e.code, "size": 0, "title": "", "err": str(e)[:40]}
        except Exception as e:
            last = str(e)[:40]
    return {"name": name, "url": urls[0], "status": 0, "size": 0, "title": "", "err": last}


rows = []
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    for res in ex.map(check, targets):
        rows.append(res)

ok = [r for r in rows if r["status"] == 200]
bad = [r for r in rows if r["status"] != 200]

print("\n=== 結果 ===")
print("  ★200 OK : %d" % len(ok))
print("  ★失敗   : %d" % len(bad))

out = os.path.join(BASE, "_deploy_status.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["name", "url", "status", "size", "title", "err"])
    w.writeheader()
    w.writerows(rows)
print("  saved:", out)

print("\n=== 失敗一覧（上位30）===")
for r in bad[:30]:
    print("  %-30s %s %s" % (r["name"], r["status"], r["err"]))

print("\n=== 成功例（上位10）===")
for r in ok[:10]:
    print("  %-30s %s %s" % (r["name"], r["status"], r["title"]))
