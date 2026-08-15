#!/usr/bin/env python3
"""US Government Grants Directory パイロット
既存の補助金情報サイトへのリンク集（著作権リスク0・内容複製なし）
"""
import sys, os
sys.path.insert(0, os.path.expanduser("~/Desktop/agentic-sites"))
from directory_builder import build_directory

site = {
    "name": "US Government Grants Directory",
    "slug": "us-grants-directory",
    "domain": "us-grants-directory.pages.dev",
    "description": "A curated directory of US government grant resources, funding opportunities, and application guides. Links to official and trusted sources.",
    "kicker": "Find US Government Grants & Funding Resources",
}

categories = {
    "Federal Grants": [
        {"title": "Grants.gov - Official Federal Grant Portal", "url": "https://www.grants.gov/", "desc": "The official US government portal for finding and applying for federal grants."},
        {"title": "USA.gov Grants", "url": "https://www.usa.gov/grants", "desc": "US government guide to grants, loans, and financial assistance programs."},
        {"title": "SAM.gov - System for Award Management", "url": "https://sam.gov/", "desc": "Official registry for entities doing business with the US government."},
        {"title": "CFDA - Catalog of Federal Domestic Assistance", "url": "https://www.cfda.gov/", "desc": "Catalog of all federal assistance programs available to the public."},
    ],
    "Small Business Grants": [
        {"title": "SBA Grants - Small Business Administration", "url": "https://www.sba.gov/funding-programs/grants", "desc": "Small Business Administration grants and funding programs for small businesses."},
        {"title": "SBIR/STTR - Small Business Innovation Research", "url": "https://www.sbir.gov/", "desc": "Federal programs for small businesses to engage in R&D with potential for commercialization."},
        {"title": "Grants.gov Small Business", "url": "https://www.grants.gov/web/grants/search-grants.html", "desc": "Search federal grants for small businesses."},
    ],
    "Education Grants": [
        {"title": "Federal Student Aid - FAFSA", "url": "https://studentaid.gov/", "desc": "Official source for federal student financial aid, including grants and loans."},
        {"title": "Pell Grants", "url": "https://studentaid.gov/understand-aid/types/grants/pell", "desc": "Federal Pell Grant program for undergraduate students with financial need."},
        {"title": "Institute of Education Sciences", "url": "https://ies.ed.gov/funding/", "desc": "Education research grants and funding from the US Department of Education."},
    ],
    "Housing & Community": [
        {"title": "HUD Grants - Housing and Urban Development", "url": "https://www.hud.gov/program_offices/spm/gmomgrants", "desc": "Housing and community development grants from the US Department of Housing and Urban Development."},
        {"title": "Community Development Block Grants", "url": "https://www.hud.gov/program_offices/comm_planning/communitydevelopment/programs", "desc": "CDBG program providing communities with resources to address a wide range of needs."},
    ],
    "Research & Science": [
        {"title": "NSF Funding - National Science Foundation", "url": "https://www.nsf.gov/funding/", "desc": "National Science Foundation grants for research and education in science and engineering."},
        {"title": "NIH Grants - National Institutes of Health", "url": "https://grants.nih.gov/", "desc": "National Institutes of Health research grants and funding opportunities."},
        {"title": "DOE Funding - Department of Energy", "url": "https://www.energy.gov/science-innovation/funding-opportunities", "desc": "Department of Energy research and development funding opportunities."},
    ],
}

if __name__ == "__main__":
    ok = build_directory(site, categories)
    print(f"✅ {site['slug']}: ディレクトリ生成完了" if ok else "❌ 失敗")
