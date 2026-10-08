"""未デプロイのサイトを特定する（ローカルにあるのに Pages に無いもの）

注意: サブドメインに接尾辞が付くため、名前の前方一致で照合する。
"""
import os, json

BASE = os.path.expanduser("~/Desktop/agentic-sites")

# ローカルのサイト候補（ディレクトリ）
local = []
for d in sorted(os.listdir(BASE)):
    p = os.path.join(BASE, d)
    if not os.path.isdir(p):
        continue
    if d.startswith("_") or d.startswith(".") or d == "__pycache__":
        continue
    # index.html か package.json があるものだけサイトとみなす
    if any(os.path.exists(os.path.join(p, f)) for f in ("index.html", "package.json", "wrangler.toml", "wrangler.jsonc")):
        local.append(d)

# デプロイ済み（名前 → 実サブドメイン）
deployed = {}
for line in open(os.path.join(BASE, "_pages_real.txt"), encoding="utf-8"):
    parts = line.split()
    if len(parts) >= 2:
        deployed[parts[0]] = parts[1]

# 前方一致で照合（ローカル名がデプロイ名の接頭辞）
missing = []
matched = []
for d in local:
    hit = None
    for name in deployed:
        if name == d or name.startswith(d + "-") or d.startswith(name):
            hit = name
            break
    if hit:
        matched.append((d, hit))
    else:
        missing.append(d)

print("=== 集計 ===")
print("  ローカルのサイト:", len(local))
print("  Pages にデプロイ済み:", len(deployed))
print("  ★照合できた:", len(matched))
print("  ★★未デプロイ:", len(missing))

print("\n=== ★未デプロイ一覧（%d件）===" % len(missing))
for d in missing:
    p = os.path.join(BASE, d)
    has = [f for f in ("index.html", "package.json", "wrangler.toml", "wrangler.jsonc") if os.path.exists(os.path.join(p, f))]
    n = 0
    try:
        n = sum(len(files) for _, _, files in os.walk(p))
    except Exception:
        pass
    print("  %-34s files=%-4d has=%s" % (d, n, ",".join(has)))
