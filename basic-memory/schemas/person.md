---
title: Person
type: schema
entity: person
schema_version: 1
schema:
  name: string, "full name, used as the title for wikilinks"
  role?: string, "role or function"
  email?: string, "primary email address"
  phone?: string, "phone number"
  linkedin?: string, "LinkedIn URL"
  works_at?: ClientContext, "primary client entity"
  partner_at?: PartnerContext, "primary partner entity"
  notes?: string, "free-form note about the person"
settings:
  validation: strict
---

# Schema, Person

Represents a physical person, contact, interlocutor, decision-maker. Lets us cleanly model the reality where the same person can be both a contact at a client and a partner elsewhere, or change employers over time.

## Typical location

- `atlas/people/{slug}.md` at the workspace root (folder to be created when the first `person` is written)
- Alternatively, in `sources/clients/{client}/people/` or `sources/partners/{partner}/people/` if the person only makes sense in that context

## Why this schema

Without a `person` schema, people only exist as `[contact]` observations in the client/partner `CLAUDE.md` sources, or as orphan wikilinks `[[Sam Rivera]]`. Impossible to query "all people who work at an active client", "all emails sent to Sam", "Alex's LinkedIn".

## Wikilink naming convention

`[[First Last]]` for unambiguous people.
`[[First Last (Company)]]` if two people share the same name (two Sams, two Chris).

## Expected observations

- `[role]` role or function (can change over time)
- `[skill]` identified skill
- `[preference]` individual communication preference (different from the company's)
- `[history]` historical element about the relationship with the organization

## Typed relations in the frontmatter

- `works_at`, primary employing client entity
- `partner_at`, partner entity if the person carries a partnership

## Additional relations in markdown

- `manages [[Other person]]`, supervises another person
- `reports_to [[Other person]]`, is supervised by
- `contact_for [[Project]]`, primary contact for a project

## Example

```yaml
---
name: Alex Martin
role: Founder, coach and marketing
email: alex@example.com
phone: "+1 555 000 0000"
linkedin: https://linkedin.com/in/alex-martin
partner_at: Alex Martin
---

# Alex Martin

## Observations
- [role] Founder of the Bloom brand
- [skill] Digital marketing, coaching, sales funnels
- [preference] Informal address, friendly tone, email and video channel
- [history] Partnership since 2026-03, bringing marketing leads
```
