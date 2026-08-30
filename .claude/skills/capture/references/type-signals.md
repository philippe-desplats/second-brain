# Type detection signals

Match the raw content against these signal sets, strongest first. One dominant set → that type. Two plausible sets → ask the user.

## email

- Header block: `From:`, `To:`, `Cc:`, `Subject:`, `Date:` (any language variant)
- Quoted-reply markers: `>` prefixed blocks, "On {date}, {name} wrote:", forwarded separators
- Greeting + sign-off structure (salutation at top, name or signature block at bottom)
- Direction inference: the owner's address or name in `From:` → `out`; in `To:` → `in`; quoted thread below a fresh reply → `reply`

## transcript

- Timestamps (`00:12:45`, `[12:03]`) or speaker labels (`Jane:`, `SPEAKER 1:`) on most lines
- Verbatim spoken register: fillers, incomplete sentences, no headings
- Recording-tool preamble (participants list, duration, meeting link)

## meeting

- Structured notes about a live exchange WITHOUT verbatim speaker lines: agenda items, "Decisions", "Action items", "Next steps" sections
- Attendee list near the top; dates and owners attached to actions
- Distinguish from transcript: meeting = digested structure; transcript = verbatim flow

## clipping

- Frontmatter already carries `type: clipping` and a `source_url`: the Web Clipper wrote it, nothing to detect, file it as is
- A bare URL, or a URL plus a one-line reason for keeping it
- Prose in a third-party voice: an article body, a documentation page, a forum thread, with the owner absent from it
- Distinguish from research: `research` is what the owner produced about sources, a `clipping` IS the source

**On a bare URL**: fetch the page if a fetch tool is available, otherwise ask the owner to paste the content. Never reconstruct a page from memory; a clipping that does not match its `source_url` is worse than no clipping.

## research

- External sources: URLs, citations, tool comparisons, benchmark tables
- Question-driven structure ("which option", "state of the art", pros/cons)

## brainstorm

- Divergent idea lists, unfinished branches, "what if" phrasing
- No conclusions or many competing options with no decision

## note

- Default fallback: factual content that documents something (a status, a synthesis, a how-to fragment) without fitting the sets above
- Prefer `note` over forcing a weak match

## Rarely inbound (usually produced, not captured)

- `writing`, `deliverable`, `strategy`: capture them only when the user explicitly says the artifact is finished work arriving from outside (for example a signed contract received as PDF → `deliverable` as binary file)

## Non-signals (ignore these)

- File extension alone (a .txt can be an email dump)
- Length (short transcripts and long emails exist)
- The folder it came from (inbox/ items are unsorted by definition)
