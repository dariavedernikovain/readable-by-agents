# Report template

Write the report in the user's language. Keep the structure; drop a section only if it would be empty, and say so in one line. "What I could not check" is never dropped. No overall score of your own: the headline is the task test. Aim for about 1,200 words or fewer: one sentence of evidence per fix, no audit diary.

```markdown
# How agents read <site>

**Task test: an agent given only the address answered <N> of <M> questions correctly.**
<One or two sentences: what it got right, what it got wrong or could not find, which reader was used. If a step did not run, name it in a few words.>

**Fix first:**
1. <The single most valuable fix, one line.>
2. <Second.>
3. <Third, or "nothing else urgent".>

## What the agent was asked
| Question | Agent's answer (short) | Right? | Where it came from |
|---|---|---|---|
| Who is behind the site? | … | ✓ / ✗ / partly | home page HTML / llms.txt / guessed |

## What I could not check
- <Each step that did not run or ran only in part (the script, a real reader, the task test in a separate agent, the accessibility tree, search presence), why (no tool for it here, the page did not load, …), and which findings that leaves unconfirmed. If every step ran: "All steps ran.">

## What already works
- <Bullets: real strengths, with evidence. Owners need to know what not to break.>

## Plan, by priority
### Critical: the agent cannot read the site
1. **<Fix, as an action>.** <What is wrong, with evidence: the reader, the measurement, a quote>. **Why it matters:** <effect on answers>. **Effort:** <minutes / hours / a rebuild>. <In code mode: the file and the change.>

### High: the agent reads, but answers wrong or incomplete
…
### Medium: hygiene and findability
…
### Low: standards with no measured effect
…

## Not for this site
- <Item>: <one reason>. (Lists checker items the owner can safely ignore.)

## Owner's choices noted
- <A deliberate decision that costs some agent readability, with the trade-off. Not a to-do.>

## Want a second opinion?
<Offer is-agentic.com, noting the report there is public and the domain goes to a third party. Only run it after a yes.>

## Appendix: evidence (optional)
<Only when the owner will act on it in code: reader quotes, file paths and lines, per-page tables. Skip it for a URL-only audit.>
```

## A filled recommendation, for tone

> 1. **Move the "Read with an agent" dialog to the end of the page.** The dialog's 52 KB of prompts sits before the greeting in the HTML, so Claude's reader puts the greeting at 40–50% of its text (WebFetch, home page). **Why it matters:** tools that truncate long pages may never reach who you are. **Effort:** 30 minutes; the dialog opens with `showModal()`, so nothing moves on screen. In code: render the dialog through a slot after the footer in `src/layouts/Base.astro`.

What makes it good: an action first, evidence named (which reader, which page), the effect on answers in plain words, an honest effort, and the file only when the code is at hand.
