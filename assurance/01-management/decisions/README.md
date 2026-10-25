# Decision register

Questions that wait on the project lead live in [`register.yaml`](register.yaml), one entry per question. Until
decision DQ-004 names a safety authority, the project lead is it. The inbox page is built from the register by
[`build_inbox.py`](build_inbox.py), and [`check_decisions.py`](check_decisions.py) checks the register in CI.

The register is where a question is asked and answered. It is not where the decision is kept: once a decision is
applied, it is recorded where the project already keeps that kind of decision (WP-M-01 §8 for strategic decisions,
otherwise the work product that owns the subject), and the entry points there.

## Lifecycle

![A question's path through the register: queued (recorded, not asked) moves to open when asked in a batch; an open question becomes answered when the lead picks an option, or assumed when an easy question has no answer by its proceed-after date; answered and assumed both become applied once the change is made; any state can become withdrawn. A hard question is never assumed.](figures/fig-dr-1-lifecycle.svg)

*Figure 1. How an entry moves between the states of the table below; drawn from the table by
[`fig_lifecycle.py`](fig_lifecycle.py) (CI fails if stale).*

| Status | Meaning | Who moves it |
|---|---|---|
| `queued` | Recorded, not asked yet. Shown collapsed on the inbox page; needs no gate or asked date. `after` names questions to settle first | Claude |
| `open` | Asked, in a numbered batch; no answer yet | Claude, when asking |
| `answered` | The lead picked an option, on the inbox page or in chat | Claude, when copying the answer in |
| `assumed` | An easy question had no answer by `proceed_after`, so Claude went ahead with the recommended option. The lead can still change it | Claude |
| `applied` | The change is made; `applied.ref` names the commit or pull request, `applied.record` where the decision is recorded | Claude |
| `withdrawn` | The question no longer applies; `note` says why | Claude |

A `hard` question is never assumed and never applied without the lead's answer. A `revisit` question also waits
for an answer, but can be reopened at the gate named in `gate`. `decider: claude` marks a reversible technical
choice: Claude takes the recommended option when the work reaches it, as `assumed`, and the lead can overrule it.

## Writing a question

Ask the lead only what the lead alone can decide: risk acceptance, ASIL or hazard scope, ODD limits, vehicle
behaviour defaults, money or hardware, the assessor, roles and independence, gate go/no-go. A task is not a
decision; it stays in its work product.

Every entry stands on its own:

- the question in plain words, phrased as a question;
- two or three lines of context on what is at stake, with the one fact that matters most in bold;
- two to four options, the recommended one first, each saying what it does and what it costs;
- how hard it is to undo (`reversibility`), what it blocks, the gate it is needed by, and its sources;
- one figure when a picture shows the difference between the options better than words, drawn by
  [`fig_questions.py`](fig_questions.py) and checked against the entry.

The fields are checked by `check_decisions.py`.

## Batches

Keep about ten questions open at a time, those that unblock the most (earliest gate, nothing left in `after`).
An open question carries `batch: N`. The inbox page shows the earliest batch that still has an open question; when
the lead has worked through it, the next batch is written from the queue to the standard above.

## The inbox page

Published privately to the lead at <https://claude.ai/artifact/R8TuZ77QVwDQBvKxof3dSc> and republished to the same link after
every change to the register.

The page shows open questions first (hard, then revisit, then easy), then answers waiting to be applied, then what
is done, with a link to each commit. Answers and requests for more explanation are saved in the page's own store,
in the collections `answers` and `explain`, keyed by question id.

At the start of each session Claude reads both collections, copies answers into the register (`via: inbox`), writes
any requested explanation into the entry's `explanation`, applies what can be applied, rebuilds the page and
republishes it, before asking anything new.

```sh
python3 assurance/01-management/decisions/check_decisions.py
python3 assurance/01-management/decisions/build_inbox.py --out <scratch>/inbox.html
```

## How a question is asked

- **Blocking now, a quick choice:** asked in chat, multiple choice with the recommendation first, then recorded here
  with `via: chat`.
- **Needs context or a picture, or can wait:** an entry and a card on the inbox page, with one line and the link in
  chat. In chat a question is named by its words, not its id.
- **Easy to undo:** an entry with `proceed_after`; Claude goes ahead with the recommendation after that date and
  says so.

## Abbreviations, terms and symbols

| Term | Meaning |
|---|---|
| ASIL | Automotive Safety Integrity Level, A (lowest) to D (highest), from ISO 26262 |
| Batch | A numbered group of about ten questions asked together, field `batch: N` |
| CI | Continuous integration: the automated checks GitHub runs on every pull request and push |
| Claude | The AI assistant that drafts the work and keeps the register |
| DQ | Decision question: the identifier of a register entry, as in DQ-004. "DQ-015 B" means option B of DQ-015 |
| Gate, go/no-go | A project milestone (G0 to G6) and the decision whether the project may pass it |
| Hard, easy, revisit | How a question may be settled: a hard one needs the lead's answer; an easy one may be assumed after its date; a revisit one can be reopened at a later gate |
| ID, id | Identifier |
| Inbox page | The private web page where the lead reads and answers the open questions |
| ODD | Operational design domain: the roads, conditions and traffic the system is designed for |
| Safety authority | Who accepts risk and decides the questions here; the project lead until DQ-004 names one |
| WP-M-01 §8 | Section 8 of the assurance strategy, where strategic decisions are recorded |
| `code` text | A field name or value of `register.yaml`, such as `proceed_after` or `via: chat` |
| `<scratch>` | Placeholder for a temporary folder of your choice |
| § | Section, as in "WP-M-01 §8" |

Other terms are defined in the [Glossary](../../../wiki/Glossary.md).
