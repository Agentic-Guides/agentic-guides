#!/usr/bin/env python3
import re, os
BASE = os.path.join(os.path.expanduser("~/Desktop/agentic-sites"), "landing")
os.chdir(BASE)
html = open("index.html", encoding="utf-8").read()

# 1. 壊れたJSON-LDを完全に置換
fixed_json = '{"@context":"https://schema.org","@type":"Organization","name":"Agentic Guides","url":"https://agentic-guides.pages.dev/","description":"AI-agent-ready content sites covering grants, taxes, mortgages, insurance, investing, and personal finance.","sameAs":["https://github.com/Agentic-Guides/agentic-guides"],"contactPoint":{"@type":"ContactPoint","contactType":"customer service","email":"contact@agentic-guides.pages.dev","url":"https://agentic-guides.pages.dev/contact"},"address":{"@type":"PostalAddress","addressLocality":"Tokyo","addressCountry":"JP"}}'

html = re.sub(r'<script type="application/ld\+json">.*?</script>', 
              '<script type="application/ld+json">' + fixed_json + '</script>', html, flags=re.DOTALL)
open("index.html","w",encoding="utf-8").write(html)
print("JSON-LD修正完了")
