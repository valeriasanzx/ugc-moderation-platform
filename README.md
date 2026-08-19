# AI-Assisted UGC Moderation Platform

A full-stack platform that moves brand user-generated content through **premod → tagging → QA**, with Claude classifying against each brand's own guidelines at every stage.

**Built at:** Social Native · **Role:** AI Creator Marketing Associate · **2026–present**

> ⚠️ **This is a case study, not the source.** The implementation is Social Native production code and lives in the company's private repository. The snippets here illustrate the design patterns and contain no company code, prompts, client data, or credentials.

---

## The problem

User-generated content collected for brand clients was moderated entirely by hand. A moderator opened each image, checked it against that brand's written guidelines, decided approve or reject, then tagged which products appeared by searching the brand's catalog manually.

**15 minutes per image.** And every brand has different rules, so the knowledge lived in people's heads and in documents nobody actually re-read at review time. Two moderators could reach different decisions on the same image. It did not scale past a handful of clients.

## The approach

The core idea: **a brand's guidelines should be structured data that drives the prompt**, not a PDF a moderator is supposed to remember. Brands supply their rules through a client-facing form; those rules feed directly into classification.

AI assists at each of the three stages rather than replacing the stage.

```
Olapic ──sync──► Postgres snapshot ──► Blocklist ──► PREMOD ──► TAGGING ──► QA ──► complete
                 (moderation state              (auto-      (Claude:    (vision:   (human:
                  independent of                 reject)     approve/    top-3      approve /
                  upstream changes)                          reject/     product    reject /
                                                             flag +      matches)   send back)
                                                             rationale)
```

| Stage | What happens |
|---|---|
| **Sync** | UGC pulled from upstream into a local Postgres snapshot |
| **Blocklist** | Per-brand creator blocklists auto-reject and skip on sync, before a human sees anything |
| **Premod** | Claude classifies approve / reject / flag against that brand's structured guidelines, with a written rationale |
| **Tagging** | Vision model suggests the top 3 product matches from the brand's own catalog |
| **QA** | Human reviewer approves, rejects, or sends back to tagging |
| **Rights** | Rights requests tracked locally; a Chrome extension (MV3) requests them on-platform |

## Decisions worth explaining

**Guidelines as data, not as prompt text I wrote.**
Brands supply their own rules through a form, and those become structured input to the classifier. Onboarding a new brand becomes data entry rather than an engineering ticket, and when a brand changes its policy, the change is theirs to make — not a code deploy. See [`guideline_prompt.py`](snippets/guideline_prompt.py).

**A local snapshot instead of reading upstream live.**
Content syncs into our own Postgres rather than being read live from the upstream system. Moderation state — what was rejected, what's mid-QA — then survives upstream changes, and the review UI never depends on an external database being reachable.

**Text and metadata first, deliberately.**
The v1 scope explicitly excluded visual AI, at the CEO's direction. Automating the text and metadata decisions first meant the platform shipped and earned trust before taking on the harder, higher-risk visual judgments.

**Every automated decision is reversible.**
AI proposes, QA disposes. There's always a send-back path, and the rationale is shown to the reviewer. Moderation is a domain where a confident wrong answer costs a client relationship — so the system is built to be corrected, and the model is asked to abstain (`flag`) rather than guess. See [`moderation_decision.py`](snippets/moderation_decision.py).

## Stack

Python · FastAPI · Claude · PostgreSQL · React · Vite · Tailwind · AWS ECS · Terraform · Chrome MV3

Test suite covers auth scoping, the rules engine, brand stream isolation, tagging, rights language, and sync strategy.

---

**[← More case studies](https://portfolio-eta-eight-46.vercel.app)**
