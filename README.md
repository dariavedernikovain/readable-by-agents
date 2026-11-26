# readable-by-agents

**Will an AI agent understand who you are from your site?**

A Claude skill for portfolios, personal sites and small brand "business card" sites. It asks your site the questions a visitor's agent would ask, checks what agents actually see, and tells you what to fix first.

More and more often, the person you send your site to does not read it. They paste it into ChatGPT or Claude and ask: *who is this, what have they done, are they a fit, how do I reach them?* This skill tells you what that agent answers, and why.

## What it is for

- **Sites:** portfolios, personal and CV sites, consultants, studios and small teams, project pages, small brand sites with no checkout.
- **The agent's job:** to **read** the site and answer for a visitor.
- **What you get:** a short report in your language:
  - the task-test result ("an agent given only your address answered 4 of 5 questions correctly");
  - what already works;
  - a plan ranked by how much each fix changes what agents answer;
  - what you can safely ignore.

## What it is not for

Online stores, SaaS apps, booking or login flows, MCP or API readiness, SEO rankings. Those are sites where an agent has to *act*, and they need different checks: protocol checkers such as Cloudflare's isitagentready.com are built for them.

## How it works

1. **Context.** What the site is for, who opens it, and 3–5 questions a visitor's agent should answer. There are defaults if you have none.
2. **Raw HTML.** `scripts/inspect_site.py` shows what an agent without JavaScript gets: visible text, where the main content starts, metadata, images without alt text, robots, sitemap, `llms.txt`, 404 behaviour, host variants, hidden emails, glued words, a CV linked through an online editor, internal comments left in the source, and whether repeated fetches get the same text.
3. **A real reader.** The page as a chat assistant's fetch tool returns it.
4. **The task test.** A fresh agent gets only the address and the questions, and no access to your files, like a stranger's assistant; every answer is checked against the site. A second, stricter reader may open only the page it is given.
5. **The accessibility tree,** if a browser tool is available: what browser agents and screen readers see.
6. **Optional:** search presence, and a second opinion from is-agentic.com, only with your consent, because its reports are public.
7. **A prioritized plan:** Critical (the agent can't read the site) → High (it answers wrong) → Medium (hygiene and findability) → Low (standards with no measured effect) → Not for this site.

Every finding is confirmed with a real reader before it goes in the report. That rule comes from experience: see below.

## Why there is no score

On the same day, the same portfolio scored **74/100** on is-agentic.com and **25/100** on isitagentready.com. Neither was wrong. The first scores whether an agent can reach and read the site; the second scores readiness signals, from robots files and sitemaps to protocols for agents that *act* (MCP, OAuth, API catalogs), which a portfolio does not need. A third invented number would look precise without meaning anything. So the headline is the outcome that matters: **did the agent answer correctly?**

## A real case: dariaprojects.com

The skill was built while making [dariaprojects.com](https://dariaprojects.com), a product leader's portfolio (Astro on Cloudflare Pages), readable by agents in November 2026. What we found and changed:

| Before | What agents got | After |
|---|---|---|
| Any unknown address returned the home page with 200 | Guessed URLs such as `/robots.txt` "existed" and returned the home page | A real 404 page with links to all cases |
| The site answered on `www`, on `*.pages.dev` and on the main domain | Three copies, split search results | One address, 301 redirects, canonical on every page |
| A 52 KB "Read with an agent" panel came before the greeting in the HTML | The greeting sat at 91% of the HTML; Claude's reader put it halfway through its text | Panel moved to the end of the page: greeting at 9% of the HTML, 5% of the reader's text |
| A live clock rendered by JavaScript | "Amsterdam00:00:00" | "Amsterdam" |
| Cloudflare email obfuscation | `/cdn-cgi/l/email-protection#e185…` instead of an address | The `mailto:` link is readable |
| Greeting: "…and now I'm building my own venture alone with AI" | Two separate agents reported her availability as unknown or contradictory | "…and my own products, alone with AI", plus an explicit "open to" block for agents. The re-test: "open to consulting projects… and to full-time or contract product-lead roles in the EU" |
| An old Google snippet said "12+ years"; Bing had no pages | Agents with search could quote outdated facts or find nothing | Domain verified in Search Console and Bing Webmaster Tools, sitemap submitted, home page re-crawled |
| Line breaks without spaces in handwritten notes | A browser agent read "below our plan.and a fractionof what B2B SaaSpays per lead" | A space before every line break |
| No link preview image or structured data on the home page | Links shared without a picture | A preview image and a JSON-LD `Person` card |

**Second opinion:** is-agentic.com went from 74 to 79. The rest of its list (Markdown by `Accept` header, trust pages) does not apply to a static portfolio.

**Two lessons that shaped the skill:**
- **Verify with a real reader.** A custom parser reported glued words that Claude's fetch tool did not glue. We almost closed it as a false alarm, until a browser agent's page reader glued them for real.
- **The biggest problem was a sentence, not markup.** Agents read "now I'm building my own venture" as "busy". Read what they answer, not only what the checklist says.

## How it was tested

The skill was built with the method of Anthropic's skill-creator: the same request goes to two agents, one with the skill and one without, and their reports are compared. There were three test cases: this portfolio, a portfolio on a builder that renders text with JavaScript, and a request to audit an online shop, which the skill should decline. There were three rounds, and the skill was revised after each.

- **Report checks.** These are statements a good report meets, such as "gives the task-test result as N of M", "lists the top fixes first" or "declines the shop". In the last round the skill's reports met 98% of them, the reports without the skill 72%.
- **Length.** About 1,400 words with the skill, about 2,500 without.
- **Coverage of the checklist.** A separate agent graded eight reports blind against a 28-item list drawn from `references/checks.md` and the skill's method (the task test, the readers used, the "not for this site" section).
  - With the skill: 18–28 items per report.
  - Without it: 13–24.
  - The 404 page, JavaScript placeholders and glued words never made it into a report written without the skill.
- **What Claude does well on its own.** On a well-built site it found about as many problems without the skill. In every round it also raised something the checklist lacked. Several checks came from those runs: internal comments in the page source, orders addressed to agents, numbers without a time frame, the facts visitors filter on, outside proof, and documents a reader can't open. The skill's own value is a full set of checks every time, clear priorities and a report half as long.
- **Limits.**
  - One run per configuration.
  - The checks were written by the skill's author.
  - Every reader was a Claude model.

  - This published version adds a few checks made after the last round, and it was not measured again.

  Treat the numbers as a direction, not a benchmark.

## Install

**Claude Code:**

```bash
git clone https://github.com/dariavedernikovain/readable-by-agents ~/.claude/skills/readable-by-agents
```

You can also copy the folder to `.claude/skills/` in a project. Then just ask, for example:
- "Will ChatGPT understand my portfolio at example.com?"
- "Check how readable my studio's site is for AI agents and tell me what to fix first."
- "Here's my personal site's repo. Make it agent-ready."

**Claude.ai:** zip the folder and upload it as a skill in Settings → Capabilities. Some steps need tools Claude.ai may not have (running the script, a browser); the skill says what it could not check.

**Codex:** the skill follows the open Agent Skills format, so Codex can load the same folder:

```bash
git clone https://github.com/dariavedernikovain/readable-by-agents ~/.agents/skills/readable-by-agents
```

Or put it in `.agents/skills/` in a repository. It has not been tested in Codex yet; steps that need a tool Codex lacks are listed in the report under what could not be checked.

## Where the rules come from

- Vercel and Ora, *Make your site readable by AI agents* (2026): 1,033 agent runs on 25 sites and 190 controlled fetch probes. The findings on blocking and on `llms.txt` come from the probes.
- web.dev, *Build agent-friendly websites*.
- Lù et al., *Build the web for agents, not agents for the web* (arXiv 2506.10953).
- Our own tests on dariaprojects.com with Claude's fetch tool, a browser agent's page reader and the agent run by is-agentic.com.
- A builder test, November 2026, on four Framer sites and ten Readymag sites. Framer served full text every time; Readymag served it only some of the time.
- The comparison runs without the skill, described above.

See `references/sources.md` for details and a short history of the idea, from the Semantic Web to `llms.txt`.

## Licence

MIT. Built with Claude Code by Daria Vedernikova.
