---
name: sb-init
description: Initialize and configure this second brain workspace. Interviews the owner about why they want a second brain, selects a profile (agency, freelance, solopreneur, personal), writes the workspace charter and context files, prunes unused zones, and optionally wires up Basic Memory. Use on first run after cloning the boilerplate, or to reconfigure the workspace. Triggers on "sb-init", "initialize workspace", "set up my second brain", "configure this workspace".
---

<objective>
Turn the freshly cloned boilerplate into a personalized, working second brain in one guided session. The outcome is a workspace where the owner knows exactly what to capture, the agent knows exactly who it works for, and the first real note can be filed immediately.
</objective>

<quick_start>

```
/sb-init          # Full guided initialization (recommended, ~15 min)
/sb-init -q       # Quick mode: skip the deep interview, minimal questions
/sb-init -r       # Reconfigure: re-run on an already initialized workspace
```

</quick_start>

<flags>

| Flag | Effect |
|------|--------|
| `-q` | Quick mode: skip the "why" interview (step-01), use profile defaults |
| `-r` | Reconfigure: allow re-running on an initialized workspace |

**Remainder** after flags is ignored.
</flags>

<workflow>
1. **Welcome** → Detect state, parse flags, explain the journey
2. **Why** → Forcing questions: trigger, status quo, 90-day success, wedge flow
3. **Profile** → Agency / freelance / solopreneur / personal, zone selection
4. **Identity** → Owner, organization, working language, communication defaults
5. **Personalize** → Write charter, context, profile block; prune zones; adjust schemas
6. **Memory** → Optional Basic Memory install and MCP wiring
7. **Launch** → Smoke test, first note, maintenance ritual, summary
</workflow>

<step_files>

| Step | File | Purpose |
|------|------|---------|
| 00 | `steps/step-00-welcome.md` | State detection, flag parsing, journey overview |
| 01 | `steps/step-01-why.md` | Forcing questions, charter material |
| 02 | `steps/step-02-profile.md` | Profile and zone selection |
| 03 | `steps/step-03-identity.md` | Owner identity and communication defaults |
| 04 | `steps/step-04-personalize.md` | Write all files, prune zones, adjust schemas |
| 05 | `steps/step-05-memory.md` | Basic Memory setup (optional) |
| 06 | `steps/step-06-launch.md` | Smoke test, first note, ritual, summary |

</step_files>

<state_variables>

| Variable | Type | Set by |
|----------|------|--------|
| `{quick_mode}` | boolean | step-00 |
| `{reconfigure}` | boolean | step-00 |
| `{charter}` | object | step-01 (trigger, status_quo, success_90d, wedge_flow, retrieval_pain) |
| `{profile}` | string | step-02 (agency, freelance, solopreneur, personal) |
| `{zones}` | list | step-02 (subset of clients, partners, internal, personal) |
| `{owner_name}` | string | step-03 |
| `{org_name}` | string | step-03 (may equal owner_name for solo profiles) |
| `{working_language}` | string | step-03 |
| `{comm_defaults}` | object | step-03 (tone, addressing, signature) |
| `{service_types}` | list | step-03 (the owner's offer categories, optional) |
| `{bm_enabled}` | boolean | step-05 |
| `{bm_project}` | string | step-05 |

</state_variables>

<execution_rules>
- **Load one step at a time** (progressive loading); follow the next_step directive at the end of each step
- **Use AskUserQuestion** for structured choices; accept free text via "Other" and treat it with care
- **Ask, then act**: batch related questions, keep the pace brisk; this is an interview, not a form
- **Show a recap before writing anything** in step-04; nothing is written to disk before the owner approves the recap
- **Never write outside the workspace**, with two explicit exceptions in step-05 (Basic Memory config and MCP registration), each individually confirmed
- **Answer in the owner's language** during the interview if they engage in another language, but write all structural files in English and content files in the working language
- **Never fabricate answers** for skipped questions; quick mode uses documented defaults, not invented ones
</execution_rules>

<entry_point>
**FIRST ACTION:** Load `steps/step-00-welcome.md`
</entry_point>
