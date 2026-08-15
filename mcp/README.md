# Agentic Guides MCP Server

MCP server for **Agentic Guides** — search articles across all Agentic Guides sites (grants, taxes, mortgages, side hustles, elder care) through a single interface.

## Tools

### `search_articles`
Search articles across all Agentic Guides sites.

**Parameters:**
- `query` (string, required): Search query, e.g. "small business grant" or "mortgage rates"
- `category` (string, optional): Filter by category
- `limit` (number, optional): Max results (default 5)

### `list_sites`
List all Agentic Guides sites and their focus areas.

## Deploy

```bash
npm install
npx wrangler deploy
```

## Connect

The server is available at:
```
https://agentic-guides-mcp.pickaxe.workers.dev/mcp
```

## License

MIT
