#!/usr/bin/env python3
"""生成済みディレクトリサイトを一括デプロイする。"""
import os, subprocess, sys

BASE = os.path.expanduser("~/Desktop/agentic-sites")
os.chdir(BASE)

# 生成済みディレクトリサイト（gen_directories.py で生成）
SITES = ["dog-care-directory","cat-care-directory","diy-home-directory","gardening-directory",
         "cooking-directory","baking-directory","travel-directory","camping-directory",
         "fitness-directory","yoga-directory","nutrition-directory","photography-directory",
         "knitting-directory","woodworking-directory","parenting-directory","homeschool-directory",
         "tech-gadgets-directory","software-directory","car-care-directory","sustainability-directory",
         "fish-keeping-directory","bird-care-directory","interior-design-directory","cleaning-directory",
         "laundry-directory","grilling-directory","coffee-directory","wine-directory",
         "hiking-directory","roadtrip-directory","sleep-directory","mental-health-directory",
         "meditation-directory","painting-directory","drawing-directory","pottery-directory",
         "sewing-directory","embroidery-directory","language-learning-directory","coding-kids-directory",
         "cybersecurity-directory","ai-tools-directory","motorcycle-directory","rv-directory",
         "recycling-directory","composting-directory","guitar-directory","piano-directory",
         "running-directory","cycling-directory","swimming-directory","freelancing-directory",
         "resume-directory","interview-directory","wedding-directory","baby-directory",
         "reptile-directory","horse-directory","furniture-directory","appliance-directory",
         "vegan-directory","glutenfree-directory","beach-directory","ski-directory",
         "dental-directory","vision-directory","origami-directory","model-building-directory",
         "college-prep-directory","study-skills-directory","webdev-directory","datascience-directory",
         "boat-directory","bicycle-directory","solar-directory","water-conservation-directory",
         "drums-directory","singing-directory","tennis-directory","golf-directory",
         "marketing-directory","ecommerce-directory","moving-directory","storage-directory",
         "hamster-directory","pest-control-directory","sourdough-directory","cruise-directory",
         "posture-directory","calligraphy-directory","tutoring-directory","smart-home-directory",
         "tire-directory","beekeeping-directory","ukulele-directory","basketball-directory",
         "productivity-directory","decluttering-directory"]

wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
if not os.path.exists(wrangler):
    wrangler = "npx wrangler"

ok = 0
fail = 0
for slug in SITES:
    # Pagesプロジェクト作成（既存ならスキップ）
    subprocess.run([wrangler, "pages", "project", "create", slug, "--production-branch", "main"],
                   capture_output=True, text=True, timeout=60)
    # デプロイ
    r = subprocess.run([wrangler, "pages", "deploy", os.path.join(BASE, slug),
                        "--project-name=" + slug, "--commit-dirty=true", "--branch=main"],
                       capture_output=True, text=True, timeout=120,
                       env={**os.environ})
    if r.returncode == 0:
        ok += 1
        print(f"✅ {slug}")
    else:
        fail += 1
        print(f"❌ {slug}: {r.stderr[-150:]}")

print(f"\n=== 完了: {ok}/{len(SITES)} 成功, {fail} 失敗 ===")
