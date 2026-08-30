# Review ritual design constraints

Shared reference for any skill that asks the owner to look back at their workspace: `curate`, `ops-weekly-pulse`, `close-session`, and anything added later. Load it when writing or changing one of them.

## Why this file exists

The periodic review is the single mechanism that turns a pile of captured material into a working second brain. It is also the most reliably abandoned habit in the entire productivity literature, and its abandonment is what collapses the system around it.

The reason is an unfavourable trade, not a lack of discipline. Capture pays immediately and costs later; review costs immediately and pays later. Every improvement in note-taking tooling over the last decade has lowered the cost of capture and left the cost of review untouched. A review skill that ignores this ships a ritual its owner will drop by February.

So a review skill is not judged on completeness. It is judged on whether someone still runs it in six months.

## The four properties

A review that survives has all four. A skill that breaks one of them is a defect, not a preference.

### 1. It draws on material already written

The review reads what exists; it does not ask the owner to produce input first. A ritual whose first step is "tell me what you did this week" has already lost, because recalling the week is the expensive part.

`close-session` reads the previous session file and the current session's activity. `ops-weekly-pulse` scans `sources/` by date. `curate` scans the zones. None of them opens with a blank prompt.

### 2. It tolerates gaps without breaking

Skipping a week must cost nothing. A streak that can be broken is a streak that will be abandoned the first time it breaks, and a system that punishes a gap teaches the owner to avoid it entirely rather than to resume.

Concretely: an empty period still produces a valid, honest output. `ops-weekly-pulse` writes the report anyway and states that no activity was detected. `curate` exits cleanly on zero candidates and suggests spacing the reviews out. `close-session` refuses to invent a project rather than writing a hollow memory.

Never fabricate activity to fill a quiet period. An empty week reported as empty is useful information.

### 3. It stays short, and offers a smaller version

The complete checklist is what makes people quit. Every review skill must have a bounded mode that covers less ground on purpose, and it must be reachable without reading the documentation.

`curate` has `-only` and `-s` to narrow the scan, and `-w` to shorten the window. `ops-weekly-pulse` has `-p` for the period. If a new review skill has no way to run a smaller pass, it is not finished.

### 4. It looks forward, not only back

An audit of the past is a chore. A review that ends on "what does this mean for next week" pays part of its cost immediately, which is the only lever available against the intertemporal trade described above.

`ops-weekly-pulse` ends on a "Next week" section. `close-session` writes `[next]` observations and cross-checks the previous session's. `curate` produces actions to take rather than a description of the state.

## What this does not license

Do not add steps to a review skill because they would be thorough. Every step added is paid by the owner on every run, and the failure mode of these skills is abandonment, not incompleteness.

Do not automate the judgement away either. The point of the review is that the owner looks at their own work; a skill that decides for them removes the cost and the benefit at the same time.
