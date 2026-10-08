"""ハブにも Pages にも入っていないサイトを全部洗い出す。

判定:
  - ローカルに index.html がある
  - Pages プロジェクト名と前方一致しない（95+100件のどれとも）
  - _hub/ にも入っていない
"""
import os

BASE = os.path.expanduser("~/Desktop/agentic-sites")

# Pages のプロジェクト名
deployed = set()
for line in open(os.path.join(BASE, "_pages_real.txt"), encoding="utf-8"):
    p = line.split()
    if len(p) >= 2:
        deployed.add(p[0])

# ハブに入っているサイト
hub = set()
HUB = os.path.join(BASE, "_hub")
if os.path.isdir(HUB):
    for d in os.listdir(HUB):
        if os.path.isdir(os.path.join(HUB, d)):
            hub.add(d)

# ローカルの候補
local = []
for d in sorted(os.listdir(BASE)):
    if d.startswith(("_", ".")) or d == "__pycache__":
        continue
    p = os.path.join(BASE, d)
    if not os.path.isdir(p):
        continue
    if os.path.exists(os.path.join(p, "index.html")):
        local.append(d)

def matched(name, pool):
    return any(n == name or n.startswith(name + "-") or name.startswith(n) for n in pool)

missing = [d for d in local if not matched(d, deployed) and d not in hub]

print("=== 集計 ===")
print("  ローカルサイト:", len(local))
print("  Pages にあり :", len(deployed))
print("  ハブにあり   :", len(hub))
print("  ★まだ未配置 :", len(missing))

print("\n=== ★未配置サイト一覧 ===")
for d in missing:
    p = os.path.join(BASE, d)
    files = []
    for r, _, fs in os.walk(p):
        files.extend(fs)
    # 構造を判定（ディレクトリ型 or ガイド型）
    kind = "directory" if "-directory" in d else ("guide" if "-guide" in d else "other")
    print("  %-34s kind=%-9s files=%-5d" % (d, kind, len(files)))
