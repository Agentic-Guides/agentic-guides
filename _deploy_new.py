"""未デプロイのディレクトリサイトを Cloudflare Pages に一括デプロイする。

★注意:
  - Pages のプロジェクト名は【既存と衝突しない】よう注意（サブドメインに接尾辞が付く）
  - 1件ずつ順番にデプロイ（並列はAPI制限に当たる）
  - 結果をCSVに記録
  - --apply で実行、無しなら対象一覧の表示のみ
"""
import os, sys, json, csv, subprocess, time

BASE = os.path.expanduser("~/Desktop/agentic-sites")
APPLY = "--apply" in sys.argv
LIMIT = None
for a in sys.argv:
    if a.startswith("--limit="):
        LIMIT = int(a.split("=")[1])

# 未デプロイ一覧（_find_undeployed.py の出力と同じロジックで再計算）
local = []
for d in sorted(os.listdir(BASE)):
    p = os.path.join(BASE, d)
    if not os.path.isdir(p) or d.startswith(("_", ".")) or d == "__pycache__":
        continue
    if os.path.exists(os.path.join(p, "index.html")):
        local.append(d)

deployed = set()
for line in open(os.path.join(BASE, "_pages_real.txt"), encoding="utf-8"):
    parts = line.split()
    if len(parts) >= 2:
        deployed.add(parts[0])

missing = []
for d in local:
    hit = any(name == d or name.startswith(d + "-") or d.startswith(name) for name in deployed)
    if not hit:
        missing.append(d)

print("=== 未デプロイ: %d 件 ===" % len(missing))
if LIMIT:
    missing = missing[:LIMIT]
    print("  --limit により %d 件に絞る" % len(missing))
for d in missing:
    print("  ", d)

if not APPLY:
    print("\n(dry run — 実行するには --apply を付ける)")
    sys.exit(0)

env = dict(os.environ)
env.pop("CLOUDFLARE_API_TOKEN", None)   # 死んだトークンを避けて OAuth を使う

results = []
for i, name in enumerate(missing, 1):
    d = os.path.join(BASE, name)
    print("\n[%d/%d] %s" % (i, len(missing), name), flush=True)
    try:
        r = subprocess.run(
            ["npx", "wrangler", "pages", "project", "create", name,
             "--production-branch", "main"],
            cwd=d, env=env, capture_output=True, timeout=180, shell=True)
        out = (r.stdout.decode("utf-8", errors="replace")
               + r.stderr.decode("utf-8", errors="replace")).strip()
        created = "already exists" not in out.lower()
        print("  create:", out.splitlines()[-1][:120] if out else "(no output)")

        r2 = subprocess.run(
            ["npx", "wrangler", "pages", "deploy", ".", "--project-name", name,
             "--branch", "main", "--commit-dirty=true"],
            cwd=d, env=env, capture_output=True, timeout=300, shell=True)
        out2 = (r2.stdout.decode("utf-8", errors="replace")
                + r2.stderr.decode("utf-8", errors="replace")).strip()
        url = ""
        for line in out2.splitlines():
            if "pages.dev" in line:
                for tok in line.replace("│", " ").split():
                    if tok.startswith("https://") and "pages.dev" in tok:
                        url = tok
        print("  deploy:", (url or out2.splitlines()[-1][:120]))
        results.append({"name": name, "ok": bool(url), "url": url, "note": ""})
    except Exception as e:
        print("  ERR:", e)
        results.append({"name": name, "ok": False, "url": "", "note": str(e)[:60]})
    time.sleep(1.5)

out_csv = os.path.join(BASE, "_deploy_new_results.csv")
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["name", "ok", "url", "note"])
    w.writeheader()
    w.writerows(results)

okn = sum(1 for r in results if r["ok"])
print("\n=== 完了: %d/%d 成功 ===" % (okn, len(results)))
print("  saved:", out_csv)
