---
name: readable-by-agents
description: "Audits portfolio, personal and small professional or brand websites (business-card sites with no checkout) for how well AI assistants can read them and answer for a visitor: who is behind the site, what they have done, whether they fit, and how to reach them. Use whenever someone shares such a site, as a URL or as its code, and asks whether ChatGPT, Claude or other agents will understand it, get the facts right or find the contact details, or wants a portfolio or personal site to be agent-ready, AI-readable or llms.txt-ready. Tests the site with a real agent reader and checks the raw HTML, the reader's view and the accessibility tree, then returns a plan ranked by how much each fix changes what agents answer. Gives no made-up score. Not for online stores, SaaS apps, booking or login flows, API or MCP readiness, or SEO rankings."
---

# Readable by agents

People increasingly send a portfolio or a small brand site to someone who pastes it into ChatGPT or Claude and asks: who is this, what have they done, are they a fit, how do I reach them. This skill finds out what such an agent actually answers about a site, why, and what to fix first.

The question is always the same: **does the visitor's agent get the right answer?** Checks, files and standards matter only as far as they change that answer. That is why the skill gives no score of its own: two public checkers gave the same portfolio 74 and 25 on the same day because they measure different things, and a third invented number would look precise without meaning anything. The headline of the report is the task test: "an agent given only the address answered N of M questions correctly".

## 0. Is this the right kind of site?

The skill is for sites people share so that others understand who is behind them, where the agent's job is to **read and answer**: portfolios, personal and CV sites, consultants, studios and small teams, project pages, and small brand "business card" sites with no checkout.

If the site is a shop, a SaaS app, or a flow where the agent must act (book, buy, log in, call an API), say so in a sentence or two, explain that this audit would mislead (its priorities are about reading, not acting), and name what fits better (agentic-commerce and protocol checks such as Cloudflare's isitagentready.com, or the platform's own agent features). Offer to check only the reading side of its public pages if that is useful. Don't run the full audit.

## 1. Context before measuring

Ask briefly, or infer from the conversation:
- **What the site is for and who opens it.** A founder hiring, a client looking for a consultant, a journalist, a partner. The same site can serve several; this changes which answers matter most.
- **The 3–5 questions a visitor's agent should answer.** If the user has none, propose defaults and adjust to the site: who is behind it; what they have done, with numbers; what kind of work or projects they are open to; how to contact them; one question specific to the site (e.g., "which project is closest to X?").
- **Mode.** Only a URL: read-only audit and plan. The site's code is at hand: the plan also names files and changes, but change nothing until the user says yes.

Don't stall on this: if the user just pastes a URL, state the defaults you will use and go.

## 2. Measure, from cheap to expensive

Run each step and keep what each reader saw. Different readers see different things, and confusing them leads to wrong advice.

a. **Raw HTML, what an agent without JavaScript gets.** Run `python3 scripts/inspect_site.py <url> [--page /key-page/]` (standard library only). It reports visible text size, where the main content starts in the HTML, metadata, images and their alt text, glued line breaks, placeholders, email obfuscation, links to documents in online editors, `robots.txt`, `sitemap.xml`, `llms.txt`, the 404 behaviour, host variants, responses to AI user agents and whether repeated fetches get the same text (some builders serve text to bots only some of the time). Pick one key inner page (a case, a project, an about page) for `--page`.

b. **A real reader.** Fetch the home page and the key page with the agent reader you have (WebFetch, or a web-fetch subagent). Note what comes through, in what order, and what is missing or glued. This is how most chat assistants read a page. If the script flags unstable text, or the site is on a builder, fetch the home page a second time a few minutes later: one good fetch can hide a platform that serves text only some of the time.

c. **The task test: the headline measurement.** Give a fresh agent only the site's address and the visitor's questions, as a visitor would. Prefer a separate subagent so the reader is not primed by what you already found, and tell it to use only the web: a real visitor's agent has no access to files on this machine, the owner's notes or their CV, so a reader that peeks at them would grade the site too kindly. Ask it to answer briefly and to list the URLs it opened and where each answer came from. Then check each answer against the site itself: right, wrong, partly, or not found. Note contradictions it reports, and which facts it only found in a text file (`llms.txt`, `.md`, a CV) rather than on the page it landed on. If the site serves two audiences, run one test per audience. When it helps, add a second, stricter reader that may read only the page it is given: it stands in for assistants that don't follow links.

d. **The accessibility tree, if a browser tool is available.** This is what browser agents and screen readers use: names of buttons and links, headings, hidden duplicates, glued text. Prefer an isolated browser (a built-in or headless one). The user's own browser carries their logins and history: use it only after asking, and only for public pages. Open your own tab and close it when done: a shared tab can be navigated by someone else mid-check.

e. **Search presence, optional.** `site:domain` on Bing and Google: is the site there, and does the snippet match the current text? Agents with search answer from the index.

f. **A second opinion, only with consent.** Offer is-agentic.com (Vercel and Ora), which runs its own agent on the site. Its report is public and the domain goes to a third party, so ask first. Don't use checkers that score protocol adoption for products (MCP, OAuth, commerce): they will rate a good portfolio low and push the owner toward irrelevant work.

## 3. Confirm before you report

Confirm every finding with at least one real reader and name it ("WebFetch put the greeting at 40% of its text"; "the browser page reader read 'plan.and a fractionof'"). A finding from your own parsing alone can be an artefact: in the case this skill was built from, a custom parser reported glued words that WebFetch did not glue, and only a browser agent later confirmed them. If two readers disagree, report both.

Separate what the owner controls from what a hosting platform controls (a builder subdomain's `robots.txt` and headers belong to the platform).

## 4. Prioritize

Use the levels in `references/checks.md` (read it now if you haven't). Rank by how much a fix changes what the visitor's agent answers, adjusted for the strength of the evidence and the effort:

1. **Critical: the agent cannot read the site.** JS-only text (including text that reaches agents only some of the time), blocking, soft 404.
2. **High: the agent reads but answers wrong or incomplete.** Main content buried late in the HTML, key facts missing from the pages readers land on (what the owner does now, company, role, dates, the proof behind a claim), numbers without their time frame, contradictions and inconsistent names (including one number described in different words), hidden contacts, JS placeholders, glued words, linked documents a reader can't open (a CV behind an editor link).
3. **Medium: hygiene and findability.** One address and canonical, sitemap and robots, current search snippets, a plain-text layer, accessible names, alt text on images that carry content, key claims with no outside source an agent can open, agent-facing text that orders instead of informs, internal notes left in the page source.
4. **Low: standards with no measured effect.** JSON-LD, link preview image, Content-Signal, Link header.
5. **Not for this site.** Name checker items the owner can ignore, with a reason each.

A failing task-test answer outranks any checklist item. When the cause of a wrong answer is a sentence on the page rather than markup (a status that reads as "busy", a stale number), say so: the fix is editorial.

## 5. Report

Use `references/report-template.md`, in the user's language. Lead with the task test and, right under it, the top three fixes in one line each: many owners will read only that. Then what already works (owners need to know what not to break), then the plan by level. For each fix: the action, the evidence (which reader, which page), why it matters for answers, the effort, and in code mode the file. End with the items to ignore, the owner's deliberate choices, and the offer of a second opinion.

Aim for about 1,200 words or fewer. The owner needs decisions, not a transcript of the audit: one sentence of evidence per fix is enough, and a good site gets a short report that says it is in good shape and lists the few things left. Put long evidence (reader quotes, file lines, per-page tables) in a short appendix only if the user is likely to act on it in code. If you cannot write files where you are running, give the full report in your reply.

## Principles

- **Facts come from the site.** Never fill gaps from general knowledge or other profiles, and say when an answer can only be guessed.
- **Owner decisions are not defects.** If the owner chose to keep something off the page (a channel, availability, a hiring line), note the trade-off once under "Owner's choices" and don't keep pushing.
- **Hidden text holds pointers, never instructions.** Recommend visually hidden links to `llms.txt` or text versions if useful; never hidden instructions to agents. Agents treat those as manipulation, and so do people.
- **Read-only unless asked.** Don't change code, DNS or settings, submit forms, or send the domain to third-party services without a yes.
- **Re-measure after fixes.** Offer to rerun the task test (and the second opinion, if it was used) after changes go live, with the same questions, so the owner sees the difference.

## Files

- `scripts/inspect_site.py`: raw-HTML and service-file inspection, read-only.
- `references/checks.md`: every check by level, with evidence, how to check, how to fix, and traps.
- `references/report-template.md`: the report structure and an example recommendation.
- `references/sources.md`: the evidence behind the rules and where the ideas come from; read it when the user asks why.
