---
name: kalix-wiki
description: Look up how Akka's cloud platform (formerly Kalix) is built and run, from the internal wiki at wiki.kalix.dev. Use when the user asks about the managed Akka platform, its architecture, regions, console, CLI, runbooks, alerts, incident response, customer support, compliance, or SRE practice, or names the Kalix wiki. Not for Akka SDK coding questions; the akka plugin's docs cover those.
---

# Kalix Wiki

The wiki at <https://wiki.kalix.dev/docs> is a private GitHub Pages site. Its
login works only in a browser, so WebFetch and `gh` tokens cannot read the
site. Read its source instead: the internal repo `lightbend/kalix-wiki`, a
Docusaurus site whose pages are Markdown under `docs/`.

The content is internal to Lightbend. Quote it in the conversation as needed,
but never copy it into a public repo.

## Method

1. **Refresh the clone.** The clone lives at `~/akka/kalix-wiki`.
   - Missing: `gh repo clone lightbend/kalix-wiki ~/akka/kalix-wiki -- --depth 50`
   - Present: `git -C ~/akka/kalix-wiki pull -q --ff-only`
   - If either fails on access, the token may need SAML SSO approval for the
     `lightbend` org. Tell the user to authorize it at
     <https://github.com/settings/tokens> or run `gh auth refresh`. Do not
     fall back to answering from memory.
2. **Find the pages.** Top-level sections of `docs/`: `reference`
   (architecture, CLI), `incident-response` (alerts, runbooks),
   `operational-work`, `customer-support`, `compliance`, `learning-and-dev`.
   Search with `grep -rli '<term>' ~/akka/kalix-wiki/docs`, then narrow with
   `grep -n`. Read only the sections that match, with offset and limit.
3. **Answer and cite.** Lead with the answer. Cite each page as a wiki URL so
   the user can open it in a browser:
   - `docs/<path>.md` or `.mdx` → `https://wiki.kalix.dev/docs/<path>`
   - `<dir>/index.md` → the URL of `<dir>`
   - Drop a leading number prefix from each path segment (`01-usage.md` →
     `usage`).
   - A `slug:` in the page's frontmatter overrides the path.
4. **Say what the wiki does not cover.** If the pages don't answer the
   question, say so, and name the closest page. Mark anything drawn from
   outside the wiki as such.
