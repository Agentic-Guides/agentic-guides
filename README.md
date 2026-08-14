# Agentic Guides — AI-Agent-Ready Content Site Generator

**Agentic Guides** is an open-source framework for generating AI-agent-ready content sites at scale. Each site is optimized for discovery and use by AI agents (WebMCP, AEO, structured data, Content Signals) and is ready to monetize via Cloudflare's agentic commerce infrastructure (Monetization Gateway / Wallets / x402) when it reaches general availability.

## What it does

Generates static, AI-agent-optimized content sites from a simple JSON config. Each site includes:

- **AEO optimization** — FAQ structured data + Article JSON-LD
- **WebMCP bridge** — agents can discover and call the site's content
- **robots.txt** — allows GPTBot, ClaudeBot, PerplexityBot, Google-Extended, CCBot
- **Content Signals** — declares how agents may use the content
- **Legal pages** — Privacy Policy, Terms of Service, Cookie Policy (required for US sites)
- **Disclaimer + affiliate disclosure** — YMYL risk mitigation
- **cron auto-update** — daily article generation and deployment

## Quick start

```bash
# 1. Configure your sites
# Edit sites_config.json (Japanese) or sites_config_en.json (English)

# 2. Seed initial articles
python site_cli.py seed <slug>

# 3. Build the site
python site_cli.py build <slug>

# 4. Deploy to Cloudflare Pages
python site_cli.py deploy <slug>

# 5. Set up daily auto-update (cron)
python daily_all.py
```

## Site config example

```json
{
  "name": "Grant Navigator",
  "slug": "grant-navigator",
  "project": "grant-navigator",
  "domain": "grant-navigator.pages.dev",
  "lang": "en",
  "description": "Latest information on US government grants...",
  "categories": {
    "Business Grants": "Business grants and subsidies",
    "Personal Aid": "Personal financial aid and benefits"
  }
}
```

## Architecture

```
agentic-sites/
├─ sites_config.json      # Japanese site configs
├─ sites_config_en.json   # English site configs
├─ site_builder.py        # Core builder (AEO/JSON-LD/WebMCP/legal pages)
├─ site_cli.py            # Build & deploy CLI
├─ daily_update.py        # Daily article generation (cron)
├─ daily_all.py           # Update all sites wrapper
└─ seeds/                 # Seed articles per site
```

## License

MIT

## Disclaimer

This framework generates informational content sites. Content is provided for reference purposes only and does not constitute professional legal, tax, medical, or financial advice. Always verify with official sources or consult a qualified professional.
