#!/usr/bin/env python3
"""指定されたCloudflare Pagesプロジェクトを一括削除"""
import os, subprocess

BASE = os.path.expanduser("~/Desktop/agentic-sites")
os.chdir(BASE)

# 削除対象（ボス指示）
targets = ["scrollless", "ai-japan-hotels-japanese-only", "simulatorjp",
           "aitrace-dashboard", "eishinringyou-v2", "eishinringyou-v3",
           "subsidy-ai-web", "retirement-calc"]

wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
if not os.path.exists(wrangler):
    wrangler = "npx wrangler"

env = dict(os.environ)
envfile = os.path.join(BASE, ".env")
if os.path.exists(envfile):
    for line in open(envfile, encoding="utf-8"):
        if line.startswith("CLOUDFLARE_API_TOKEN="):
            env["CLOUDFLARE_API_TOKEN"] = line.split("=", 1)[1].strip()

ok = 0
fail = 0
for slug in targets:
    r = subprocess.run([wrangler, "pages", "project", "delete", slug, "--yes"],
                       capture_output=True, text=True, timeout=60, env=env)
    if r.returncode == 0:
        ok += 1
        print(f"✅ 削除 {slug}")
    else:
        fail += 1
        print(f"❌ {slug}: {r.stderr[-100:]}")

print(f"\n=== 完了: {ok}/{len(targets)} 削除, {fail} 失敗 ===")
