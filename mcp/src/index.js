import { McpServer } from "@modelcontextprotocol/server";
import { createMcpHandler } from "agents/mcp/server";
import { z } from "zod";
import { ARTICLES } from "./articles_data.js";

// Agentic Guides MCP Server
// 全サイトの記事を検索・取得できるツールを提供する。
// エージェントが「Agentic Guides」ブランドの全サイトを1つの窓口から呼べる。

function createServer() {
  const server = new McpServer({
    name: "agentic-guides",
    version: "1.0.0",
  });

  // 記事検索ツール
  server.registerTool(
    "search_articles",
    {
      description: "Search articles across all Agentic Guides sites (grants, taxes, mortgages, side hustles, elder care). Returns matching articles with titles, descriptions, and URLs.",
      inputSchema: {
        query: z.string().describe("Search query, e.g. 'small business grant' or 'mortgage rates'"),
        category: z.string().optional().describe("Optional category filter: Business Grants, Personal Aid, Energy, Startup, Housing, Tax Filing, Freelancer, Deductions, Retirement, e-Filing, Mortgage Basics, Rates, Tax Credits, Down Payment, Refinance, Getting Started, Remote Work, Skills, Taxes, Clients, Medicare, Long-Term Care, Care Services, Care Costs, Family Care"),
        limit: z.number().optional().describe("Max results to return (default 5)"),
      },
    },
    async ({ query, category, limit }) => {
      const q = (query || "").toLowerCase();
      const lim = limit || 5;
      let results = ARTICLES.filter((a) => {
        const matchesQuery = !q || a.title.toLowerCase().includes(q) || a.description.toLowerCase().includes(q);
        const matchesCategory = !category || a.category === category;
        return matchesQuery && matchesCategory;
      }).slice(0, lim);

      if (results.length === 0) {
        return {
          content: [{ type: "text", text: "No articles found. Try a different query or browse the sites directly." }],
        };
      }

      const text = results
        .map((a) => `### ${a.title}\n${a.description}\nSite: ${a.site} | Category: ${a.category}\nURL: ${a.url}`)
        .join("\n\n");

      return {
        content: [{ type: "text", text }],
      };
    }
  );

  // サイト一覧ツール
  server.registerTool(
    "list_sites",
    {
      description: "List all Agentic Guides sites and their focus areas.",
      inputSchema: {},
    },
    async () => {
      const sites = [
        { name: "Grant Navigator", url: "https://grant-navigator.pages.dev", focus: "US government grants and subsidies" },
        { name: "Tax Filing Guide", url: "https://tax-filing-guide.pages.dev", focus: "US tax filing, deductions, and credits" },
        { name: "Mortgage Guide", url: "https://mortgage-guide.pages.dev", focus: "US mortgages, rates, and homebuyer tax benefits" },
        { name: "Side Hustle Hub", url: "https://side-hustle-hub.pages.dev", focus: "Side hustles, remote work, and freelancing" },
        { name: "Elder Care Guide", url: "https://elder-care-guide.pages.dev", focus: "Medicare, long-term care, and elder care" },
      ];
      const text = sites.map((s) => `- **${s.name}**: ${s.focus}\n  ${s.url}`).join("\n");
      return { content: [{ type: "text", text }] };
    }
  );

  return server;
}

export default {
  fetch(request, env, ctx) {
    return createMcpHandler(createServer)(request, env, ctx);
  },
};
