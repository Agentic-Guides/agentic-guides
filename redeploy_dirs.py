#!/usr/bin/env python3
"""デプロイ済みディレクトリ27個を再デプロイ（llms.txt反映）"""
import os, subprocess

BASE = os.path.expanduser("~/Desktop/agentic-sites")
os.chdir(BASE)

DIRS = ["ai-tools-directory-6ny","appliance-directory","baby-directory","baking-directory",
        "basketball-directory","beach-directory","beekeeping-directory","camping-directory",
        "cat-care-directory","coffee-directory","cooking-directory","diy-home-directory",
        "dog-care-directory","fitness-directory","gardening-directory","guitar-directory",
        "hiking-directory","interior-design-directory","knitting-directory","meditation-directory",
        "nutrition-directory","photography-directory","running-directory","sewing-directory",
        "travel-directory","woodworking-directory","yoga-directory"]

wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
if not os.path.exists(wrangler):
    wrangler = "npx wrangler"

ok = 0
fail = 0
for slug in DIRS:
    r = subprocess.run(
        [wrangler, "pages", "deploy", os.path.join(BASE, slug),
         "--project-name=" + slug, "--commit-dirty=true", "--branch=main"],
        capture_output=True, text=True, timeout=120, env={**os.environ})
    if r.returncode == 0:
        ok += 1
        print(f"✅ {slug}")
    else:
        fail += 1
        print(f"❌ {slug}: {r.stderr[-200:]}")
print(f"\n=== 完了: {ok}/{len(DIRS)} 成功, {fail} 失敗 ===")
