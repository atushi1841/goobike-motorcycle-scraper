# Goobike Japan Used Motorcycles Scraper

Scrape used motorcycle listings from **goobike.com** (バイクブロス), Japan's largest used motorcycle marketplace. Extract maker, model, price, year, engine displacement, mileage, repair history, shop location and contact info — perfect for reseller arbitrage, market research, and price monitoring.

> 🇯🇵 **Japanese used motorcycle market data** — goobike.com lists 100,000+ used bikes from nationwide dealers. Ideal for motorcycle exporters and cross-border market analysis.

## Output Sample

```json
{
  "itemId": "8503623B30260806013",
  "title": "ＣＢＲ２５０ＲＲ ２０１７年モデル ローダウン仕様",
  "maker": "ホンダ",
  "price": 668000,
  "imageUrl": "https://picture.goobike.com/850/8503623/Q/8503623B3026080601300.jpg",
  "detailUrl": "https://www.goobike.com/spread/8503623B30260806013/index.html",
  "year": "2017年",
  "displacement": "250cc",
  "mileage": "2316 km",
  "repairHistory": "なし",
  "location": "千葉県木更津市",
  "shop": "バイク王　ＨＵＮＴ木更津店",
  "phone": "0438-30-0190",
  "source": "goobike"
}
```

## Input

| Field | Type | Description |
|-------|------|-------------|
| `searchKeyword` | string | Maker or model name (e.g. `ホンダ`, `CBR250RR`). Empty = scan all bikes |
| `maxItems` | integer | Max number of listings to fetch (default 100) |
| `maxPages` | integer | Max pages to crawl (default 5) |
| `statsMode` | boolean | Return price statistics instead of raw listings |
| `statsKeyword` | string | Model name to aggregate price stats for (e.g. `CBR250RR`) |
| `proxyConfiguration` | object | Apify proxy (auto by default) |

## Use Cases

- **Motorcycle exporters** — source Japanese used bikes for overseas resale (Japan exports ~500K bikes/year, scooters = 58%)
- **Reseller arbitrage** — compare JDM motorcycle prices across dealers
- **Market research** — track model-specific price trends (use `statsMode`)
- **Price monitoring** — watch for deals on specific models

## Pricing

Pay-per-event: small fee per result. Use `statsMode` to get aggregated price stats (min/max/avg/median) for a specific model in a single call.

## Limitations

- Requires Apify proxy (auto) — goobike may block overseas datacenter IPs
- Default fetch is 100 items / 5 pages; raise `maxItems`/`maxPages` for more
- Japanese-language output (maker/title/location are in Japanese)

## FAQ

**Q: Can I search by maker?** Yes — pass `searchKeyword: "ホンダ"` (or any maker/model name).

**Q: How do I get price statistics?** Set `statsMode: true` and `statsKeyword: "CBR250RR"` to get count/min/max/avg/median prices.

## Changelog

- **0.1** — Initial release: keyword search, full listing fields, stats mode.

## MCP Server & Registry

This scraper is also available as an MCP server for AI agents:

- **MCP Registry**: `io.github.atushi1841/japan-motorcycle-market-mcp`
- **Apify Store**: https://apify.com/fruitful_quintessence/goobike-motorcycle-scraper
- **Gumroad**: https://atushi5.gumroad.com/l/kutuxe

Install via MCP: add to your MCP config:
```json
{"mcpServers": {"japan-motorcycle-market-mcp": {"command": "python3", "args": ["src/stdio_main.py"]}}}
```

## Smithery

[![Smithery](https://smithery.ai/server/japan-motorcycle-market-mcp/badge)](https://smithery.ai/server/japan-motorcycle-market-mcp)

Install via Smithery:

```bash
npx @smithery/cli install japan-motorcycle-market-mcp --client claude
```
