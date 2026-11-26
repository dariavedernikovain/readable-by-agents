# Where the rules come from

Read this when the user asks why a rule exists, how strong the evidence is, or where the idea came from.

## Primary sources

- **Vercel and Ora, "Make your site readable by AI agents"** (vercel.com/kb/guide/make-your-site-readable-by-ai-agents, published 28 August 2026, updated 3 September; data from June to August 2026). Two data sets. A trace study: 1,033 agent runs on 25 sites, mostly SaaS documentation. Controlled fetch probes: 190 probes on one documentation site served in 19 configurations, each read by a plain fetch client without JavaScript and by one that runs JavaScript. Agents read the same HTML as people and usually start from the home page. The findings this skill leans on come from the probes: adding `llms.txt`, JSON-LD, sitemaps and Markdown mirrors did not change retrieval of an answer already in server-rendered HTML; a 403 to agent user agents blocked both clients; an answer available only through JavaScript blocked the fetch-only client (0 of 5) but not the one that runs JavaScript (5 of 5). The probes used one documentation site, not portfolios. Practical advice: accurate 404s, one canonical page per answer, `rel="alternate"` to Markdown, a sitemap, `robots.txt` only for deliberate exclusions. This is the strongest evidence behind the Critical level.
- **web.dev, "AI agent site UX"** (Kasper Kulikowski, Omkar More; Chrome team; undated, no measurements). Agents see a site through screenshots, the DOM and the accessibility tree, so hover-only states, shifting layouts and motion break for them. Advice: semantic `<button>` and `<a>`, no transparent overlays over controls, `cursor: pointer`, stable layout, labelled form fields, audit the accessibility tree, WebMCP for sites where agents act. Source for M5 and the browser-reader checks.
- **Lù, Kamath, Mosbach, Reddy, "Build the web for agents, not agents for the web"** (arXiv 2506.10953, McGill and Mila, June 2025). A position paper, no experiments. Argues for an Agentic Web Interface built for agents rather than making agents operate human UIs. Principles that match this skill's approach: send a small representation first and details on request (an index, then full text), give agents only what they need, keep a human in the loop for actions.

- **Builder test, 26 November 2026** (own measurement; small sample). Four Framer sites (three portfolios on `*.framer.website`, two of them templates, plus framer.com) and ten live Readymag sites from Readymag's own showcase post (January 2024), fetched with curl as a browser and as up to nine bot user agents, repeated four times on four Readymag sites, and cross-checked with Claude WebFetch on six pages (on three Readymag sites it returned only the page title, not the meta description). Framer: full text in the HTML every time, a Markdown version on request. Readymag: an empty shell on the first pass for all ten; pre-rendered text for bots appeared only some of the time. On two of three Framer portfolios every image had an empty alt (marked decorative). Limits: user-agent strings in curl do not reproduce the bots' IP addresses; only one real reader (WebFetch) was used; one day. Source for C1 "every time" and M5b.

## The two checkers, and why they disagree

- **is-agentic.com** (Vercel and Ora): scores whether an ordinary agent can reach, read and use a site, and runs an agent on a task ("What does this site do and who is it for?"). Closest to this skill's question. Its remaining deductions on a good static portfolio are usually Markdown negotiation and trust pages (see "Not for these sites").
- **isitagentready.com** (Cloudflare): scores adoption of emerging protocols (MCP, OAuth discovery, API catalog, Agent Skills, WebMCP, commerce). Made for products and shops. On a portfolio it stays low whatever you do, which is why this skill does not use it.
- On the same day the same portfolio scored 74/100 on the first and 25/100 on the second. This is why the skill reports a task-test result instead of inventing a third number.

## A short genealogy

- **2001.** Berners-Lee, Hendler and Lassila, "The Semantic Web" (Scientific American): software agents that read marked-up data on websites. Marking up was costly and agents were weak; the idea stalled.
- **2011.** Google, Bing and Yahoo launch schema.org: shared vocabulary for structured data. JSON-LD on a portfolio descends from it.
- **2023–2024.** Browser agents start reading the accessibility tree; work done for screen-reader users becomes an interface for machines.
- **2024.** Jeremy Howard (Answer.AI) proposes `llms.txt`; Anthropic releases the Model Context Protocol.
- **2025–2026.** WebMCP proposals for in-browser agent tools; position papers on agent-specific interfaces; the first measured studies (Vercel and Ora) find that for reading, good server-rendered HTML is what matters.

## The case the skill was built from

dariaprojects.com, a product leader's portfolio (Astro on Cloudflare Pages), November 2026. The README has the before/after. The sequence that produced the rules: read the guide, test with real readers, fix, measure again, and twice discover that an earlier conclusion was wrong because only one reader had been tried.
