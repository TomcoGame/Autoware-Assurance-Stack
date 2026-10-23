Some questions only the safety authority can answer. Until decision DQ-004 names a safety authority, the project
lead is it. Those questions are asked and answered in the
[decision register](../assurance/01-management/decisions/README.md); everything else is decided in the work itself.

## Who decides what

| Kind of question | Who decides | Where |
|---|---|---|
| Risk acceptance, ASIL and hazard scope, ODD limits, vehicle behaviour defaults, money and hardware, roles and independence, the assessor, gate go/no-go | The safety authority (the project lead for now) | An entry in the decision register |
| A reversible technical choice | The AI assistant takes the recommended option and says so (`decider: claude`); the lead can overrule it | An entry in the register, marked `assumed` |
| A task | Nobody: it is work, not a decision | The open items of its work product |

The rules for assurance work also set limits on the assistant: it never marks its own work Approved, never accepts
evidence or claims, never closes defeaters or passes gates, and never lowers an ASIL, changes a timing budget or
loosens a safety limit to make a finding go away ([`CLAUDE.md`](../CLAUDE.md)).

## How a question is written

Each entry in [`register.yaml`](../assurance/01-management/decisions/register.yaml) stands on its own, so it can be
answered from a phone without reading anything else:

- the question in plain words;
- a few lines on what is at stake, with the fact that matters most in bold;
- two to four options, the recommended one first, each with what it does and what it costs;
- how hard it is to undo (`reversibility`), what it blocks, the gate it is needed by, and its sources;
- a figure when a picture shows the difference between the options better than words.

[`check_decisions.py`](../assurance/01-management/decisions/check_decisions.py) checks the fields and the lifecycle
in CI. The full rules are in the
[register README](../assurance/01-management/decisions/README.md#writing-a-question).

## Lifecycle of a question

![A question's path through the register: queued moves to open when asked in a batch; an open question becomes answered when the lead picks an option, or assumed when an easy question has no answer by its proceed-after date; answered and assumed both become applied once the change is made; any state can become withdrawn. A hard question is never assumed.](../assurance/01-management/decisions/figures/fig-dr-1-lifecycle.svg)

*Drawn from the status table of the register README by
[`fig_lifecycle.py`](../assurance/01-management/decisions/fig_lifecycle.py).*

| Status | Meaning |
|---|---|
| `queued` | Recorded, not asked yet |
| `open` | Asked, in a numbered batch |
| `answered` | The lead picked an option |
| `assumed` | An easy question had no answer by its `proceed_after` date, so the recommended option was taken; the lead can still change it |
| `applied` | The change is made; the entry names the commit or pull request and where the decision is recorded |
| `withdrawn` | The question no longer applies |

A `hard` question is never assumed. About ten questions are open at a time, in numbered batches, those that unblock
the most first.

## Where a decision ends up

The register is where a question is asked and answered, not where the decision is kept. Once applied, a decision is
recorded where the project keeps that kind of decision: strategic decisions in
[WP-M-01 §8](../assurance/01-management/WP-M-01-assurance-strategy.md#8-strategic-decisions), others in the work
product that owns the subject. Work products cite the decision by its identifier, for example "DQ-015 B" for option
B of DQ-015.

## How the lead answers

Open questions are shown to the lead on a private inbox page built from the register by
[`build_inbox.py`](../assurance/01-management/decisions/build_inbox.py). The lead picks an option or asks for more
explanation there. At the start of each session the assistant copies answers into the register, answers requests
for explanation, and applies what it can before asking anything new. A question that blocks work right now can be
asked in chat instead, multiple choice with the recommendation first, and is then recorded with `via: chat`.
